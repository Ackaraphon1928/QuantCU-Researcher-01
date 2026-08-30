from __future__ import annotations

import itertools
from typing import Any

import numpy as np


def validate_binary_vector(x: np.ndarray, n_assets: int | None = None) -> None:
    """Check that a candidate vector is binary and of the expected dimension."""
    arr = np.asarray(x, dtype=int)
    if n_assets is not None and arr.shape[0] != n_assets:
        raise ValueError("Binary vector length does not match the number of assets.")
    if not np.isin(arr, [0, 1]).all():
        raise ValueError("Binary vector contains values other than 0 or 1.")


def discrete_objective(x: np.ndarray, mu: np.ndarray, covariance: np.ndarray, k: int, risk_aversion: float = 1.0) -> float:
    """Compute the equal-weight discrete objective for a K-asset subset."""
    x = np.asarray(x, dtype=int)
    validate_binary_vector(x, len(mu))
    if x.sum() != k:
        raise ValueError(f"The selected asset count is {x.sum()}, not the required {k}.")
    weights = x / k
    ret = float(np.dot(weights, mu))
    risk = float((weights @ covariance @ weights))
    return float(ret - risk_aversion * risk)


def build_discrete_qubo(mu: np.ndarray, covariance: np.ndarray, k: int, risk_aversion: float = 1.0, penalty: float | None = None) -> tuple[np.ndarray, np.ndarray, float, dict[str, Any], Any]:
    """Construct the objective-only QUBO and return the separate cardinality penalty.

    For a fixed-cardinality binary portfolio with x_i in {0,1}, the discrete objective is:
        maximize (1 / k) mu^T x - (risk_aversion / k^2) x^T Sigma x
    subject to sum(x) = k.

    The QUBO energy returned here is the minimization equivalent of the objective only:
        E_obj(x) = -(1 / k) mu^T x + (risk_aversion / k^2) x^T Sigma x.

    The cardinality penalty is returned separately as A(sum(x) - k)^2 and is added outside the QUBO.
    """
    mu = np.asarray(mu, dtype=float)
    cov = np.asarray(covariance, dtype=float)
    n = len(mu)
    if cov.shape != (n, n):
        raise ValueError("Covariance matrix shape does not match expected return vector.")
    if penalty is None:
        penalty = 1.0 / max(k, 1)

    linear = np.zeros(n, dtype=float)
    q = np.zeros((n, n), dtype=float)

    for i in range(n):
        linear[i] = -(mu[i] / k) + (risk_aversion * cov[i, i]) / (k * k)
    for i in range(n):
        for j in range(i + 1, n):
            q[i, j] = 2.0 * (risk_aversion * cov[i, j] / (k * k))

    metadata = {
        "n_assets": n,
        "k": k,
        "risk_aversion": risk_aversion,
        "penalty": penalty,
        "objective": "maximize mu^T x / k - risk_aversion x^T Sigma x / k^2",
        "sign_convention": "minimize energy = -objective + penalty * (sum(x)-k)^2",
    }

    def decoder(bitstring: np.ndarray | list[int]) -> tuple[int, ...]:
        arr = np.asarray(bitstring, dtype=int)
        return tuple(int(v) for v in arr)

    return q, linear, penalty, metadata, decoder


def qubo_energy(x: np.ndarray, qubo: np.ndarray, linear: np.ndarray, penalty: float = 0.0, k: int | None = None) -> float:
    """Compute the QUBO energy including the optional cardinality penalty term."""
    x = np.asarray(x, dtype=int)
    validate_binary_vector(x, len(linear))
    energy = float(np.dot(linear, x))
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            energy += float(qubo[i, j] * x[i] * x[j])
    if penalty and k is not None:
        energy += penalty * (x.sum() - k) ** 2
    return energy


def solve_mvo(mu: np.ndarray, covariance: np.ndarray, risk_aversion: float = 1.0) -> np.ndarray:
    """Solve the long-only MVO problem with a supported convex solver from the current environment."""
    import cvxpy as cp

    mu = np.asarray(mu, dtype=float)
    cov = np.asarray(covariance, dtype=float)
    n = len(mu)
    w = cp.Variable(n)
    objective = cp.Maximize(mu @ w - risk_aversion * cp.quad_form(w, cov))
    constraints = [cp.sum(w) == 1, w >= 0]
    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.SCS, eps=1e-6, max_iters=20000)
    if problem.status not in {"optimal", "optimal_inaccurate"}:
        raise RuntimeError(f"MVO did not converge: {problem.status}")
    return np.asarray(w.value, dtype=float)


def exact_enumeration(mu: np.ndarray, covariance: np.ndarray, k: int, risk_aversion: float = 1.0) -> dict[str, Any]:
    """Enumerate all feasible binary vectors for a small instance and return the optimum."""
    mu = np.asarray(mu, dtype=float)
    cov = np.asarray(covariance, dtype=float)
    best_obj = -np.inf
    best_x = None
    for bits in itertools.product([0, 1], repeat=len(mu)):
        x = np.asarray(bits, dtype=int)
        if x.sum() != k:
            continue
        obj = discrete_objective(x, mu, cov, k, risk_aversion)
        if obj > best_obj:
            best_obj = obj
            best_x = x.copy()
    if best_x is None:
        raise ValueError("No feasible solution found under the cardinality constraint.")
    return {"x": best_x, "objective": float(best_obj), "k": k}


def decode_bitstring(bitstring: np.ndarray | list[int]) -> tuple[int, ...]:
    """Decode a bitstring to a tuple representation."""
    return tuple(int(v) for v in np.asarray(bitstring, dtype=int).ravel())
