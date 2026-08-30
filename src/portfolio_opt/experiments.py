from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import yaml


def load_experiment_config(path: str | Path) -> dict[str, Any]:
    """Load the experiment configuration from a YAML file."""
    with open(path, "r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)
    if config is None:
        return {}
    return config


def save_results(path: str | Path, payload: dict[str, Any]) -> None:
    """Write experiment payloads to JSON using a reproducible structure."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)


def make_seed_list(seed: int, count: int) -> list[int]:
    """Create a deterministic list of random seeds."""
    rng = np.random.default_rng(seed)
    return [int(v) for v in rng.integers(0, 10_000, size=count)]
