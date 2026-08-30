from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class BacktestConfig:
    train_window: int = 120
    test_window: int = 30
    rebalance_frequency: str = "M"


def train_test_split(returns: pd.DataFrame, train_window: int, test_window: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a return matrix into train and test windows with a simple chronological cut."""
    if train_window <= 0 or test_window <= 0:
        raise ValueError("Window sizes must be positive.")
    if len(returns) < train_window + test_window:
        raise ValueError("Return series is too short for the requested train/test split.")
    train = returns.iloc[:train_window]
    test = returns.iloc[train_window:train_window + test_window]
    return train, test


def walk_forward_backtest(returns: pd.DataFrame, strategy_fn: Any, train_window: int = 120, test_window: int = 30) -> list[dict[str, Any]]:
    """Run a simple walk-forward evaluation with the same windowing convention across methods."""
    results: list[dict[str, Any]] = []
    for start in range(0, len(returns) - train_window - test_window + 1, test_window):
        train = returns.iloc[start:start + train_window]
        test = returns.iloc[start + train_window:start + train_window + test_window]
        result = strategy_fn(train, test)
        result["window_start"] = start
        result["window_end"] = start + train_window + test_window
        results.append(result)
    return results
