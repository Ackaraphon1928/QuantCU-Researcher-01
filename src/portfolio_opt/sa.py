from __future__ import annotations

import numpy as np

from .portfolio import discrete_objective


def simulated_annealing(mu: np.ndarray, covariance: np.ndarray, k: int, seed: int = 0, iterations: int = 200, initial_temp: float = 1.0, cooling: float = 0.995) -> dict:
    """Simulated annealing on a binary K-cardinality portfolio selection problem."""
    rng = np.random.default_rng(seed)
    n = len(mu)
    current = np.zeros(n, dtype=int)
    selected = rng.choice(n, size=k, replace=False)
    current[selected] = 1

    current_obj = discrete_objective(current, mu, covariance, k)
    best = current.copy()
    best_obj = current_obj
    temperature = initial_temp
    history = []

    for step in range(iterations):
        candidate = current.copy()
        chosen = rng.choice(np.arange(n), size=2, replace=False)
        selected_idx = chosen[0]
        unselected_idx = chosen[1]
        if current[selected_idx] == 1 and current[unselected_idx] == 0:
            candidate[selected_idx] = 0
            candidate[unselected_idx] = 1
        else:
            candidate[selected_idx] = 1
            candidate[unselected_idx] = 0
        if candidate.sum() != k:
            continue
        candidate_obj = discrete_objective(candidate, mu, covariance, k)
        delta = candidate_obj - current_obj
        if delta > 0 or rng.random() < np.exp(delta / max(temperature, 1e-12)):
            current = candidate
            current_obj = candidate_obj
        if candidate_obj > best_obj:
            best = candidate.copy()
            best_obj = candidate_obj
        history.append(best_obj)
        temperature *= cooling

    return {"x": best.astype(int), "objective": float(best_obj), "history": history, "iterations": iterations}
