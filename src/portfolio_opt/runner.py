from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .data import build_default_price_data, calculate_returns, estimate_covariance, estimate_expected_returns
from .portfolio import exact_enumeration, solve_mvo, build_discrete_qubo, discrete_objective
from .ga import genetic_algorithm
from .sa import simulated_annealing


def run_experiment(config: dict[str, Any] | None = None, output_dir: str | Path | None = None) -> list[dict[str, Any]]:
    """Run a minimal benchmark for exact, MVO, GA, and SA against the same synthetic default data."""
    config = config or {
        "asset_count": 4,
        "selected_assets": 2,
        "risk_aversion": 1.0,
        "random_seed": 42,
        "qaoa": {"depth": 1, "shots": 128},
    }
    out = Path(output_dir) if output_dir is not None else Path("results")
    tables_dir = out / "tables"
    logs_dir = out / "logs"
    tables_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    prices = build_default_price_data()
    returns = calculate_returns(prices)
    mu = estimate_expected_returns(returns, annualization=252)
    cov = estimate_covariance(returns, annualization=252)
    mu = mu.to_numpy()
    cov = cov.to_numpy()

    selected = int(config.get("selected_assets", 2))
    risk_aversion = float(config.get("risk_aversion", 1.0))
    seed = int(config.get("random_seed", 42))

    results: list[dict[str, Any]] = []
    exact = exact_enumeration(mu, cov, k=selected, risk_aversion=risk_aversion)
    results.append({
        "algorithm": "exact",
        "objective": exact["objective"],
        "feasibility": True,
        "selected_assets": list(np.where(exact["x"] == 1)[0].tolist()),
    })

    weights = solve_mvo(mu, cov, risk_aversion=risk_aversion)
    results.append({
        "algorithm": "mvo",
        "objective": float(np.dot(weights, mu) - risk_aversion * (weights @ cov @ weights)),
        "feasibility": bool(np.isclose(weights.sum(), 1.0) and np.all(weights >= -1e-8)),
        "selected_assets": list(np.argsort(weights)[-selected:]),
    })

    ga = genetic_algorithm(mu, cov, k=selected, seed=seed, population_size=24, generations=40)
    results.append({
        "algorithm": "ga",
        "objective": float(ga["objective"]),
        "feasibility": bool(ga["x"].sum() == selected),
        "selected_assets": list(np.where(ga["x"] == 1)[0].tolist()),
    })

    sa = simulated_annealing(mu, cov, k=selected, seed=seed, iterations=300)
    results.append({
        "algorithm": "sa",
        "objective": float(sa["objective"]),
        "feasibility": bool(sa["x"].sum() == selected),
        "selected_assets": list(np.where(sa["x"] == 1)[0].tolist()),
    })

    q = build_discrete_qubo(mu, cov, selected, risk_aversion=risk_aversion)
    results.append({
        "algorithm": "qubo",
        "objective": float(-q[1].sum()),
        "feasibility": True,
        "selected_assets": list(np.argsort(q[1])[:selected]),
    })

    table_path = tables_dir / "benchmark_results.csv"
    with open(table_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["algorithm", "objective", "feasibility", "selected_assets"])
        writer.writeheader()
        for row in results:
            writer.writerow({**row, "selected_assets": str(row["selected_assets"])})

    def to_native(value: Any) -> Any:
        if isinstance(value, np.integer):
            return int(value)
        if isinstance(value, np.floating):
            return float(value)
        if isinstance(value, np.ndarray):
            return [to_native(v) for v in value.tolist()]
        if isinstance(value, list):
            return [to_native(v) for v in value]
        if isinstance(value, tuple):
            return [to_native(v) for v in value]
        return value

    summary_path = logs_dir / "benchmark_summary.json"
    json_payload = {"results": [], "config": config}
    for row in results:
        json_payload["results"].append({key: to_native(value) for key, value in row.items()})
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(json_payload, fh, indent=2)

    return results


if __name__ == "__main__":
    run_experiment()
