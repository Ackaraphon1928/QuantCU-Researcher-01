# Skill: Quantum Portfolio Optimization Prototype

## Purpose

Build a reproducible research prototype for the project:

**Benchmarking Classical and Quantum Optimization Algorithms for Portfolio Selection:
A Comparative Study of Performance, Risk, and Computational Efficiency**

The prototype must compare:
1. Mean-Variance Optimization (MVO)
2. Genetic Algorithm (GA)
3. Simulated Annealing (SA)
4. Quantum Approximate Optimization Algorithm (QAOA)

The project is a research benchmark, not a claim that quantum computing is superior.

---

## 1. Non-negotiable research framing

Keep the experimental comparison fair.

All algorithms should solve the same portfolio-selection problem as closely as their mathematical representations permit.

Primary questions:
- Which method produces the best risk-adjusted portfolio?
- How does QAOA compare with classical methods in solution quality?
- What is the trade-off between quality and computational cost?
- At what portfolio sizes, if any, does QAOA become competitive?

Never report a quantum advantage merely because a quantum circuit returns a solution. Compare against strong classical baselines under the same data, objective, constraints, and evaluation protocol.

---

## 2. Recommended prototype architecture

Use a Python repository with Jupyter notebooks for exploration and Python modules for reusable logic.

```text
quantum-portfolio-optimization/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .gitignore
├── configs/
│   └── experiment.yaml
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_portfolio_formulation.ipynb
│   ├── 03_mvo_baseline.ipynb
│   ├── 04_genetic_algorithm.ipynb
│   ├── 05_simulated_annealing.ipynb
│   ├── 06_qaoa_portfolio.ipynb
│   ├── 07_backtest_and_metrics.ipynb
│   └── 08_final_benchmark.ipynb
├── src/
│   └── portfolio_opt/
│       ├── data.py
│       ├── portfolio.py
│       ├── metrics.py
│       ├── baselines.py
│       ├── ga.py
│       ├── sa.py
│       ├── quantum.py
│       ├── backtest.py
│       ├── experiments.py
│       └── plotting.py
├── tests/
└── results/
    ├── tables/
    ├── figures/
    └── logs/
```

For the first prototype, it is acceptable to start with one notebook. Refactor into modules once the mathematics works.

---

## 3. Start small

Do NOT begin with 50–100 assets.

Start with a tiny controlled experiment:
- 4–8 assets
- fixed historical period
- weekly or monthly rebalancing for the first prototype
- long-only
- fully invested
- cardinality constraint if required by the QAOA encoding

Then scale to 8–12 or more assets.

The quantum representation is the main bottleneck. Do not design the first experiment around an unrealistically large universe.

---

## 4. Data pipeline

Preferred initial data:
- publicly available historical daily adjusted-close prices
- a small, liquid and stable asset universe

Pipeline:
1. Download prices.
2. Align trading dates.
3. Handle missing observations explicitly.
4. Calculate returns.
5. Estimate expected returns.
6. Estimate covariance matrix.
7. Split data chronologically into train/validation/test or rolling windows.
8. Never use future test information to estimate parameters.

Use a deterministic seed for all stochastic algorithms.

---

## 5. Portfolio formulation

Classical continuous portfolio:

Let:
- w_i = portfolio weight of asset i
- μ_i = estimated expected return
- Σ = covariance matrix

Basic mean-variance objective:

maximize

    μᵀw - λ wᵀΣw

subject to:

    Σ_i w_i = 1
    w_i >= 0

Optionally:

    w_i <= w_max

and/or:

    ||w||_0 <= K

where K is the maximum number of selected assets.

Clearly distinguish:
- asset selection
- capital allocation

QAOA is naturally suited to a discrete formulation, so the prototype should first formulate a binary asset-selection problem.

---

## 6. Recommended QAOA formulation

Use binary variables:

    x_i ∈ {0,1}

where x_i = 1 means asset i is selected.

For an equal-weight K-asset portfolio:

    w_i = x_i / K

with:

    Σ_i x_i = K

A simple discrete objective can be written as:

    maximize  (1/K) Σ_i μ_i x_i
              - λ/K² Σ_i,j Σ_ij x_i x_j

subject to:

    Σ_i x_i = K

Convert the constrained maximization into a QUBO minimization by:
- changing sign where necessary
- adding a penalty such as

    A(Σ_i x_i - K)^2

The exact scaling of λ and the penalty A must be documented and tested.

Important:
- Keep the QUBO coefficients numerically well-scaled.
- Test that the penalty is strong enough to discourage infeasible selections.
- Check feasibility of sampled bitstrings instead of assuming the optimizer always returns a valid solution.

---

## 7. Quantum implementation strategy

Prefer a modern Qiskit-compatible implementation.

Before coding, inspect the currently installed versions and current official Qiskit APIs. Do not blindly copy old tutorials.

Prototype order:
1. Construct the binary optimization problem.
2. Convert it to QUBO/Ising form.
3. Solve the QUBO exactly by brute force for tiny N.
4. Solve with a classical QUBO optimizer.
5. Run QAOA on an ideal simulator.
6. Compare QAOA against the exact optimum.
7. Only then consider noisy simulation or real hardware.

This gives a ground-truth experiment.

---

## 8. Mandatory sanity checks

Before benchmarking:

### Mathematical checks
- weights sum to one
- no negative weights
- selected asset count equals K
- objective values agree between equivalent formulations
- QUBO energy maps correctly to the portfolio objective
- brute-force optimum matches the expected optimum

### Algorithm checks
- GA returns valid chromosomes
- SA returns valid states
- QAOA samples are decoded correctly
- infeasible quantum samples are handled explicitly

### Financial checks
- returns are aligned correctly
- covariance matrix is symmetric
- annualization convention is consistent
- no look-ahead bias
- transaction costs are either included for every method or excluded for every method

---

## 9. Classical baselines

### MVO
Use CVXPY/SciPy for the continuous constrained problem.

This is the strongest reference for the continuous version.

If QAOA solves a discrete equal-weight problem, also create a fair discrete classical baseline for the same QUBO.

### Genetic Algorithm
Use a binary chromosome for asset selection.

Recommended:
- chromosome length = N
- exactly K selected assets
- tournament or rank selection
- crossover
- mutation
- repair operator to maintain K selections
- fixed random seed
- multiple independent runs

### Simulated Annealing
Use the same binary representation as GA.

A simple neighborhood:
- swap one selected asset with one unselected asset

This preserves exactly K assets and makes the comparison cleaner.

---

## 10. Evaluation protocol

Separate optimization quality from investment performance.

### Optimization-level metrics
- objective value
- optimality gap when exact optimum is available
- feasibility rate
- convergence behavior
- runtime
- number of objective evaluations
- memory usage where practical

### Portfolio-level metrics
- annualized return
- annualized volatility
- Sharpe ratio
- Sortino ratio
- maximum drawdown
- Calmar ratio

Also report:
- turnover
- number of selected assets
- concentration metrics if relevant

Do not compare only Sharpe ratio.

---

## 11. Experimental design

For every algorithm use:
- identical data
- identical return/covariance estimates
- identical constraints
- identical K
- same evaluation horizon
- fixed but algorithm-appropriate random seeds
- multiple independent stochastic runs

Recommended first benchmark matrix:

```text
N assets:       4, 6, 8, 10
K selected:     2, 3, 4
Algorithms:     MVO, GA, SA, QAOA
Quantum mode:   ideal statevector/sampling simulator first
Runs:           >= 10 for GA/SA/QAOA where practical
```

For very small N, enumerate every bitstring to obtain the exact discrete optimum.

---

## 12. Backtesting

Do not tune parameters on the test set.

Minimum viable workflow:

```text
train window
    ↓
estimate μ and Σ
    ↓
optimize portfolio
    ↓
hold during test window
    ↓
calculate realized return/risk
    ↓
move window forward
    ↓
repeat
```

Use a rolling or walk-forward backtest when the prototype is mature.

---

## 13. Statistical comparison

For repeated experiments, compare paired observations across identical windows/seeds.

Use:
- paired t-test when assumptions are reasonably satisfied
- Wilcoxon signed-rank test as a non-parametric alternative
- confidence intervals

Do not use a statistical test simply because it appears in the proposal. Explain what is paired and what constitutes one observation.

Report effect sizes where possible.

---

## 14. Visualization requirements

Create at least:
1. cumulative wealth curves
2. drawdown curves
3. risk-return scatter
4. Sharpe-ratio comparison
5. runtime vs number of assets
6. objective value vs number of assets
7. convergence curves for GA/SA/QAOA where meaningful
8. feasibility rate for QAOA

Use consistent labels and units.

---

## 15. Reproducibility

Record:
- Python version
- Qiskit version
- package versions
- dataset source
- download date
- asset universe
- date ranges
- random seeds
- all hyperparameters
- QAOA depth p
- simulator/backend
- number of shots
- optimizer used by QAOA
- penalty coefficient
- risk-aversion λ
- K
- transaction-cost assumption

Save experiment configurations and results to CSV/JSON.

---

## 16. Research integrity rules

The prototype must explicitly distinguish:

### What is actually measured
- solution quality
- financial metrics
- runtime
- scalability
- feasibility

### What is not demonstrated
A simulator experiment does NOT demonstrate practical quantum advantage.

If QAOA is slower than classical methods, report it honestly.

If QAOA performs worse, that is a valid result.

If QAOA performs competitively for a small instance, describe the conditions rather than generalizing.

---

## 17. Definition of done

The prototype is complete when a fresh environment can:

1. install dependencies
2. download/load data
3. preprocess data
4. construct the portfolio problem
5. solve the exact tiny instance
6. run MVO
7. run GA
8. run SA
9. build QUBO
10. run QAOA on a simulator
11. decode solutions
12. backtest all methods
13. calculate all core metrics
14. produce comparison tables
15. produce comparison figures
16. save results
17. reproduce the same experiment using a config file

The final notebook should tell the story from problem → formulation → algorithms → experiment → results → limitations.
