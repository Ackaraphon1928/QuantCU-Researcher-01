from __future__ import annotations

import numpy as np

from .portfolio import discrete_objective


def genetic_algorithm(
    mu: np.ndarray,
    covariance: np.ndarray,
    k: int,
    seed: int = 0,
    population_size: int = 20,
    generations: int = 50,
    mutation_rate: float = 0.1,
    elite_fraction: float = 0.2,
    risk_aversion: float = 1.0,
) -> dict:
    """A minimalist binary genetic algorithm for K-asset selection.

    The notebook passes ``mutation_rate``, ``elite_fraction``, and ``risk_aversion``;
    they are accepted here for API compatibility and used to tune the search.
    """
    rng = np.random.default_rng(seed)
    n = len(mu)
    population = rng.integers(0, 2, size=(population_size, n), endpoint=False)
    for row in population:
        if row.sum() != k:
            indices = rng.choice(n, size=k, replace=False)
            row[:] = 0
            row[indices] = 1

    elite_count = max(1, int(population_size * elite_fraction))
    best = None
    history = []
    for _ in range(generations):
        scores = np.array(
            [discrete_objective(ind, mu, covariance, k, risk_aversion=risk_aversion) for ind in population],
            dtype=float,
        )
        order = np.argsort(scores)[::-1]
        elite = population[order[:elite_count]]
        if best is None or scores[order[0]] > best["objective"]:
            best = {"x": population[order[0]].copy(), "objective": float(scores[order[0]])}
        history.append(best["objective"])

        new_population = [ind.copy() for ind in elite]
        while len(new_population) < population_size:
            parent_a = population[rng.integers(0, population_size)]
            parent_b = population[rng.integers(0, population_size)]
            mask = rng.random(n) < 0.5
            child = np.where(mask, parent_a, parent_b)
            if rng.random() < mutation_rate:
                mutate_idx = rng.choice(n, size=max(1, n // 10), replace=False)
                child[mutate_idx] = 1 - child[mutate_idx]
            if child.sum() != k:
                one_idx = np.flatnonzero(child == 1)
                zero_idx = np.flatnonzero(child == 0)
                if child.sum() > k:
                    remove_idx = rng.choice(one_idx, size=int(child.sum() - k), replace=False)
                    child[remove_idx] = 0
                else:
                    add_idx = rng.choice(zero_idx, size=int(k - child.sum()), replace=False)
                    child[add_idx] = 1
            new_population.append(child)
        population = np.asarray(new_population, dtype=int)

    final = max(population, key=lambda ind: discrete_objective(ind, mu, covariance, k, risk_aversion=risk_aversion))
    objective = float(discrete_objective(final, mu, covariance, k, risk_aversion=risk_aversion))
    return {
        "x": final.astype(int),
        "objective": objective,
        "history": history,
        "population_size": population_size,
        "generations": generations,
        "mutation_rate": mutation_rate,
        "elite_fraction": elite_fraction,
        "risk_aversion": risk_aversion,
    }
