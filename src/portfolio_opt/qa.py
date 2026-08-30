from __future__ import annotations

from typing import Any

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from .portfolio import discrete_objective, build_discrete_qubo, validate_binary_vector


def build_qaoa_ansatz(num_qubits: int, depth: int = 1, gamma: list[float] | None = None, beta: list[float] | None = None) -> QuantumCircuit:
    """Build a QAOA ansatz for K-cardinality portfolio selection with given parameters."""
    if gamma is None:
        gamma = [0.5] * depth
    if beta is None:
        beta = [0.5] * depth

    circuit = QuantumCircuit(num_qubits)
    circuit.h(range(num_qubits))

    for layer in range(depth):
        for i in range(num_qubits):
            circuit.rz(2.0 * gamma[layer], i)
        for i in range(num_qubits - 1):
            circuit.cx(i, i + 1)
            circuit.rz(2.0 * gamma[layer], i + 1)
            circuit.cx(i, i + 1)
        for i in range(num_qubits):
            circuit.rx(2.0 * beta[layer], i)

    return circuit


def run_qaoa_on_qubo(
    mu: np.ndarray,
    covariance: np.ndarray,
    k: int,
    depth: int = 1,
    shots: int = 1024,
    seed: int = 0,
    risk_aversion: float = 1.0,
) -> dict[str, Any]:
    """Run QAOA on the binary portfolio selection problem using AerSimulator.

    Uses a simple random parameter sweep instead of classical optimization for reproducibility.
    """
    mu = np.asarray(mu, dtype=float)
    cov = np.asarray(covariance, dtype=float)
    n = len(mu)

    qubo, linear, penalty, meta, decoder = build_discrete_qubo(mu, cov, k, risk_aversion=risk_aversion)

    np.random.seed(seed)
    rng = np.random.default_rng(seed)
    backend = AerSimulator(seed_simulator=seed)

    best_bitstring = None
    best_objective = -np.inf
    total_feasible = 0
    total_samples = 0

    for trial in range(1 + depth):
        gamma = rng.uniform(0.1, np.pi, size=depth)
        beta = rng.uniform(0.1, np.pi, size=depth)

        circuit = build_qaoa_ansatz(n, depth=depth, gamma=gamma.tolist(), beta=beta.tolist())
        circuit.measure_all()

        tc = transpile(circuit, backend)
        job = backend.run(tc, shots=shots)
        counts = job.result().get_counts()

        for bitstring_str, count in counts.items():
            bitstring = np.array([int(b) for b in reversed(bitstring_str)], dtype=int)
            total_samples += count
            if bitstring.sum() == k:
                total_feasible += count
                obj = discrete_objective(bitstring, mu, cov, k, risk_aversion)
                if obj > best_objective:
                    best_objective = obj
                    best_bitstring = bitstring.copy()

    if best_bitstring is None:
        best_bitstring = np.zeros(n, dtype=int)
        best_bitstring[:k] = 1
        best_objective = discrete_objective(best_bitstring, mu, cov, k, risk_aversion)
        total_feasible = 0

    return {
        "x": best_bitstring,
        "objective": float(best_objective),
        "feasible": bool(best_bitstring.sum() == k),
        "feasibility_rate": float(total_feasible / total_samples) if total_samples > 0 else 0.0,
        "num_qubits": n,
        "depth": depth,
        "shots": shots,
        "metadata": meta,
    }
