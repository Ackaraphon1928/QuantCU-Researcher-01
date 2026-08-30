import numpy as np
import pandas as pd
import pytest

from portfolio_opt.data import (
    build_default_price_data,
    calculate_returns,
    clean_price_frame,
    estimate_covariance,
    estimate_expected_returns,
)
from portfolio_opt.metrics import (
    calmar_ratio,
    max_drawdown,
    portfolio_return,
    portfolio_variance,
    portfolio_volatility,
    sharpe_ratio,
    sortino_ratio,
)
from portfolio_opt.portfolio import (
    discrete_objective,
    exact_enumeration,
    solve_mvo,
    build_discrete_qubo,
    decode_bitstring,
)
from portfolio_opt.ga import genetic_algorithm
from portfolio_opt.runner import run_experiment
from portfolio_opt.qa import run_qaoa_on_qubo
from portfolio_opt.backtest import walk_forward_backtest, train_test_split
from portfolio_opt.sa import simulated_annealing


@pytest.fixture
def synthetic_data():
    returns = np.array(
        [
            [0.010, 0.020, -0.010, 0.015],
            [0.015, 0.018, -0.005, 0.012],
            [0.008, 0.022, -0.012, 0.014],
            [0.012, 0.017, -0.008, 0.011],
        ],
        dtype=float,
    )
    cov = np.cov(returns, rowvar=False)
    mu = returns.mean(axis=0)
    return mu, cov


def test_returns_and_covariance_are_finite(synthetic_data):
    mu, cov = synthetic_data
    assert mu.shape == (4,)
    assert cov.shape == (4, 4)
    assert np.all(np.isfinite(mu))
    assert np.all(np.isfinite(cov))
    assert np.allclose(cov, cov.T)


def test_mvo_returns_valid_weights(synthetic_data):
    mu, cov = synthetic_data
    weights = solve_mvo(mu, cov, risk_aversion=1.0)
    assert weights.shape == mu.shape
    assert np.isclose(weights.sum(), 1.0)
    assert np.all(weights >= -1e-8)


def test_discrete_qubo_matches_portfolio_objective(synthetic_data):
    mu, cov = synthetic_data
    k = 2
    qubo, linear, penalty, meta, decoder = build_discrete_qubo(mu, cov, k, risk_aversion=1.0)
    x = np.array([1, 1, 0, 0], dtype=int)
    objective = discrete_objective(x, mu, cov, k, risk_aversion=1.0)
    energy = 0.0
    for i in range(len(x)):
        energy += linear[i] * x[i]
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            energy += qubo[i, j] * x[i] * x[j]
    assert np.isclose(energy + penalty * (x.sum() - k) ** 2, -objective)
    assert decoder(x) == tuple(x.tolist())


def test_exact_enumeration_finds_valid_solution(synthetic_data):
    mu, cov = synthetic_data
    best = exact_enumeration(mu, cov, k=2, risk_aversion=1.0)
    assert len(best["x"]) == len(mu)
    assert best["x"].sum() == 2
    assert np.isfinite(best["objective"])


def test_ga_and_sa_return_valid_bitstrings(synthetic_data):
    mu, cov = synthetic_data
    ga = genetic_algorithm(mu, cov, k=2, seed=123, population_size=20, generations=30)
    sa = simulated_annealing(mu, cov, k=2, seed=123, iterations=200)
    assert ga["x"].sum() == 2
    assert sa["x"].sum() == 2
    assert np.isfinite(ga["objective"])
    assert np.isfinite(sa["objective"])


def test_portfolio_metrics_are_finite():
    weights = np.array([0.5, 0.5])
    returns = np.array([0.01, 0.02])
    cov = np.array([[0.04, 0.01], [0.01, 0.025]])
    assert np.isfinite(portfolio_return(weights, returns))
    assert np.isfinite(portfolio_variance(weights, cov))
    assert np.isfinite(portfolio_volatility(weights, cov))
    assert np.isfinite(sharpe_ratio(weights, returns, cov, risk_free=0.01))
    assert np.isfinite(sortino_ratio(weights, returns, cov, risk_free=0.01))
    assert np.isfinite(max_drawdown(np.array([1.0, 1.02, 0.98, 1.03])))
    assert np.isfinite(calmar_ratio(np.array([1.0, 1.02, 0.98, 1.03]), 252))


def test_decode_bitstring_handles_lists():
    arr = np.array([1, 0, 1])
    assert decode_bitstring(arr) == (1, 0, 1)


def test_experiment_runner_saves_results(tmp_path):
    config = {"asset_count": 4, "selected_assets": 2, "risk_aversion": 1.0, "random_seed": 42, "qaoa": {"depth": 1, "shots": 128}}
    results = run_experiment(config=config, output_dir=tmp_path)
    assert any(item["algorithm"] == "exact" for item in results)
    assert (tmp_path / "tables" / "benchmark_results.csv").exists()
    assert (tmp_path / "logs" / "benchmark_summary.json").exists()


def test_qaoa_returns_feasible_solution(synthetic_data):
    mu, cov = synthetic_data
    k = 2
    result = run_qaoa_on_qubo(mu, cov, k, depth=1, shots=512, seed=123)
    assert result["feasible"]
    assert result["x"].sum() == k
    assert np.isfinite(result["objective"])


def test_walk_forward_backtest_splits_correctly():
    returns = pd.DataFrame(np.random.randn(100, 2), columns=["A", "B"])
    train, test = train_test_split(returns, train_window=60, test_window=20)
    assert len(train) == 60
    assert len(test) == 20
    assert train.index[0] < test.index[0]


def test_default_price_data_is_deterministic_and_complete():
    prices = build_default_price_data()
    assert list(prices.columns) == ["AAPL", "MSFT", "AMZN", "GOOGL"]
    assert prices.notna().all().all()
    returns = calculate_returns(prices)
    assert returns.notna().all().all()
    mu = estimate_expected_returns(returns, annualization=252)
    cov = estimate_covariance(returns, annualization=252)
    assert mu.shape == (4,)
    assert cov.shape == (4, 4)
    assert np.all(np.isfinite(mu.to_numpy()))
    assert np.all(np.isfinite(cov.to_numpy()))


def test_missing_prices_are_cleaned_and_reported():
    raw = pd.DataFrame(
        {
            "AAPL": [100.0, np.nan, 101.5, 102.0],
            "MSFT": [200.0, 201.0, 202.0, 203.0],
            "AMZN": [90.0, 91.0, np.nan, 93.0],
            "GOOGL": [150.0, 151.0, 152.0, 153.0],
        }
    )
    cleaned, report = clean_price_frame(raw)
    assert cleaned.notna().all().all()
    assert report["missing_cells"] >= 1
    assert report["cleaned_rows"] == len(cleaned)
    returns = calculate_returns(cleaned)
    assert returns.notna().all().all()
