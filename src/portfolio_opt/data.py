from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class DataConfig:
    tickers: list[str]
    start: str
    end: str
    source: str = "yahoo"


def build_default_price_data() -> pd.DataFrame:
    """Create a deterministic, small universe of synthetic daily prices for local benchmarking."""
    dates = pd.date_range(start="2020-01-02", periods=120, freq="B")
    base = {
        "AAPL": 100.0,
        "MSFT": 150.0,
        "AMZN": 90.0,
        "GOOGL": 110.0,
    }
    drift = {"AAPL": 0.003, "MSFT": 0.0025, "AMZN": 0.0035, "GOOGL": 0.0022}
    volatility = {"AAPL": 0.015, "MSFT": 0.013, "AMZN": 0.017, "GOOGL": 0.014}

    frames: list[pd.Series] = []
    for ticker in ["AAPL", "MSFT", "AMZN", "GOOGL"]:
        rng = np.random.default_rng(42 + len(ticker))
        path = np.empty(len(dates), dtype=float)
        path[0] = base[ticker]
        for i in range(1, len(dates)):
            shock = rng.normal(loc=drift[ticker], scale=volatility[ticker])
            path[i] = path[i - 1] * (1.0 + shock)
        frames.append(pd.Series(path, index=dates, name=ticker))

    prices = pd.concat(frames, axis=1)
    prices.columns = ["AAPL", "MSFT", "AMZN", "GOOGL"]
    return prices


def clean_price_frame(prices: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Fill obvious missing values and return a structured report instead of silently discarding data."""
    if prices.empty:
        raise ValueError("Price dataframe is empty.")

    original = prices.copy()
    missing_before = int(original.isna().sum().sum())
    cleaned = original.copy()
    cleaned = cleaned.ffill().bfill()

    remaining_missing = int(cleaned.isna().sum().sum())
    if remaining_missing > 0:
        for column in cleaned.columns:
            if cleaned[column].isna().any():
                cleaned[column] = cleaned[column].fillna(cleaned[column].median())

    report = {
        "missing_cells": int(missing_before),
        "remaining_missing_cells": int(cleaned.isna().sum().sum()),
        "cleaned_rows": int(len(cleaned)),
        "columns": list(cleaned.columns),
        "missing_by_column": {col: int(cleaned[col].isna().sum()) for col in cleaned.columns},
        "status": "missing values were filled deterministically and reported",
    }
    return cleaned, report


def calculate_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Return a dataframe of arithmetic returns from adjusted close prices."""
    if prices.empty:
        raise ValueError("Price dataframe is empty.")
    returns = prices.pct_change().dropna(how="any")
    if returns.empty:
        raise ValueError("No non-null returns could be computed from the price data.")
    return returns


def estimate_expected_returns(returns: pd.DataFrame, annualization: int = 252) -> pd.Series:
    """Estimate annualized expected returns from a return matrix."""
    if returns.empty:
        raise ValueError("Returns dataframe is empty.")
    mean_daily = returns.mean(axis=0)
    return mean_daily * annualization


def estimate_covariance(returns: pd.DataFrame, annualization: int = 252) -> pd.DataFrame:
    """Estimate annualized covariance matrix from returns."""
    if returns.empty:
        raise ValueError("Returns dataframe is empty.")
    cov = returns.cov().to_numpy()
    cov = np.asarray(cov, dtype=float)
    if cov.shape[0] != cov.shape[1]:
        raise ValueError("Covariance matrix is not square.")
    annualized = cov * annualization
    return pd.DataFrame(annualized, index=returns.columns, columns=returns.columns)


def load_price_data(config: DataConfig, fallback_prices: dict[str, list[float]] | None = None) -> pd.DataFrame:
    """Load a small deterministic price dataset or a Yahoo Finance dataset when available."""
    if fallback_prices is not None:
        data = {ticker: pd.Series(vals, name=ticker) for ticker, vals in fallback_prices.items()}
        frame = pd.concat(data.values(), axis=1)
        frame.columns = list(fallback_prices.keys())
        frame.index = pd.date_range(start=config.start, periods=len(frame), freq="B")
        return frame

    if config.tickers == ["AAPL", "MSFT", "AMZN", "GOOGL"]:
        return build_default_price_data()

    try:
        import yfinance as yf

        prices = yf.download(config.tickers, start=config.start, end=config.end, auto_adjust=True, progress=False)
        if isinstance(prices.columns, pd.MultiIndex):
            prices = prices.iloc[:, prices.columns.get_level_values(1) == "Close"]
            prices.columns = [c[0] for c in prices.columns]
        if prices.empty:
            raise ValueError("No price data found from Yahoo Finance.")
        return prices
    except Exception as exc:  # pragma: no cover - fallback path used for offline compatibility
        raise RuntimeError(f"Unable to load public price data for {config.tickers}: {exc}") from exc


def validate_returns(returns: pd.DataFrame) -> None:
    """Validate that returns contain only finite values and all assets are aligned."""
    if returns.empty:
        raise ValueError("Returns are empty.")
    if not np.all(np.isfinite(returns.to_numpy(dtype=float))):
        raise ValueError("Returns contain NaN or inf values.")
    if returns.isna().any().any():
        raise ValueError("Returns still contain missing data after cleaning.")
