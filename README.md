# Quantum Portfolio Optimization Prototype

This repository is a reproducible prototype for benchmarking classical and quantum portfolio optimization algorithms in a research setting.

## Environment

Verified active environment:

- Python: 3.13.9 (Conda)
- Qiskit: 1.4.6
- CVXPY: 1.9.2

## Reproduction

```bash
python -m venv .venv
# activate environment
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# or macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
jupyter lab
```

## Project structure

- [src/portfolio_opt](src/portfolio_opt): reusable optimization logic
- [notebooks](notebooks): staged research notebook workflow
- [tests](tests): unit tests and validation checks
- [results](results): tables, figures, and logs
- [configs/experiment.yaml](configs/experiment.yaml): default experiment configuration

## Default workflow

1. Run the test suite: `pytest`
2. Open the notebooks in order under [notebooks](notebooks)
3. Generate benchmark outputs under [results](results)
4. Keep all algorithm configurations in [configs/experiment.yaml](configs/experiment.yaml)

## Data and methodology notes

- The prototype uses a deterministic, configurable asset universe for fast reproduction.
- The discrete portfolio problem is built around the cardinality-constrained binary selection formulation.
- QAOA is benchmarked against exact enumeration and classical baselines on the same objective, with explicit feasibility checks.
- No look-ahead bias is introduced in the data pipeline or backtest logic.

## Verification

The repository currently passes its validation suite:

```bash
D:\miniconda\python.exe -m pytest -q
```

Result: 7 passed in 1.79s.
