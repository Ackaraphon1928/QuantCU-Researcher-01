from __future__ import annotations

import numpy as np


def portfolio_return(weights: np.ndarray, expected_returns: np.ndarray) -> float:
    """Compute portfolio expected return."""
    w = np.asarray(weights, dtype=float)
    r = np.asarray(expected_returns, dtype=float)
    return float(np.dot(w, r))


def portfolio_variance(weights: np.ndarray, covariance: np.ndarray) -> float:
    """Compute portfolio variance."""
    w = np.asarray(weights, dtype=float)
    cov = np.asarray(covariance, dtype=float)
    if cov.shape != (len(w), len(w)):
        raise ValueError("Covariance matrix must match the weight vector length.")
    return float(w @ cov @ w)


def portfolio_volatility(weights: np.ndarray, covariance: np.ndarray) -> float:
    """Compute annualized portfolio volatility using the square root of variance."""
    return float(np.sqrt(max(portfolio_variance(weights, covariance), 0.0)))


def sharpe_ratio(weights: np.ndarray, expected_returns: np.ndarray, covariance: np.ndarray, risk_free: float = 0.0) -> float:
    """Compute the Sharpe ratio for a portfolio."""
    expected = portfolio_return(weights, expected_returns)
    vol = portfolio_volatility(weights, covariance)
    if vol == 0:
        return 0.0
    return float((expected - risk_free) / vol)


def sortino_ratio(weights: np.ndarray, expected_returns: np.ndarray, covariance: np.ndarray, risk_free: float = 0.0) -> float:
    """Compute the Sortino ratio using downside volatility."""
    expected = portfolio_return(weights, expected_returns)
    sigma = np.asarray(covariance, dtype=float)
    downside = np.diag(sigma)
    downside_vol = float(np.sqrt(max(np.dot(weights * weights, downside), 0.0)))
    if downside_vol == 0:
        return 0.0
    return float((expected - risk_free) / downside_vol)


def max_drawdown(values: np.ndarray) -> float:
    """Compute the maximum drawdown from a cumulative wealth path."""
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return 0.0
    peak = np.maximum.accumulate(arr)
    drawdown = (arr - peak) / peak
    return float(np.min(drawdown))


def calmar_ratio(values: np.ndarray, annualization: int = 252) -> float:
    """Compute the Calmar ratio using annualized return over max drawdown."""
    arr = np.asarray(values, dtype=float)
    if arr.size < 2:
        return 0.0
    total_return = arr[-1] / arr[0] - 1.0
    annualized_return = (1.0 + total_return) ** (annualization / max(len(arr) - 1, 1)) - 1.0
    mdd = abs(max_drawdown(arr))
    if mdd == 0:
        return 0.0
    return float(annualized_return / mdd)
