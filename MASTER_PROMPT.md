# MASTER PROMPT FOR CODEX

You are the lead research engineer helping me build a prototype for my capstone research project:

**“Benchmarking Classical and Quantum Optimization Algorithms for Portfolio Selection: A Comparative Study of Performance, Risk, and Computational Efficiency.”**

The project proposal specifies four methods:
- Mean-Variance Optimization (MVO)
- Genetic Algorithm (GA)
- Simulated Annealing (SA)
- Quantum Approximate Optimization Algorithm (QAOA)

The purpose is benchmarking, not proving quantum advantage.

## Your mission

Build the prototype from an empty repository to a reproducible Jupyter-notebook-based research project.

Before writing substantial code:

1. Read `SKILL.md` and `PROTOTYPE_SPEC.md`.
2. Inspect the local Python version and installed packages.
3. Check the currently supported versions/APIs of Qiskit and related packages. Prefer current official documentation over old tutorials.
4. Explain the proposed architecture briefly.
5. Then implement it incrementally.

Do not ask me to manually write code that you can create yourself.

---

# PHASE 0 — Repository setup

Create:

```text
README.md
requirements.txt
pyproject.toml
.gitignore
configs/experiment.yaml
src/portfolio_opt/
notebooks/
tests/
results/tables/
results/figures/
results/logs/
```

Use clean Python packaging.

Pin or record compatible package versions after checking the environment.

---

# PHASE 1 — Data pipeline

Implement a configurable data loader.

Requirements:
- public historical price data
- adjusted prices where available
- configurable ticker list
- configurable start/end dates
- missing-data handling
- return calculation
- annualization convention
- expected return estimator
- covariance estimator

Make the pipeline deterministic and prevent look-ahead bias.

Do not silently drop problematic data. Report what happened.

Create a small default universe so the notebook can run quickly.

---

# PHASE 2 — Portfolio mathematics

Implement and explain:

1. expected return
2. covariance
3. portfolio return
4. portfolio variance
5. portfolio volatility
6. Sharpe ratio
7. Sortino ratio
8. maximum drawdown
9. Calmar ratio

Implement the continuous MVO problem:

maximize

    μᵀw - λ wᵀΣw

subject to:

    sum(w) = 1
    w >= 0

Use CVXPY or an appropriate current solver.

Validate the result with assertions.

---

# PHASE 3 — DISCRETE PORTFOLIO FORMULATION

This is the most important mathematical part.

Use:

    x_i ∈ {0,1}

where x_i indicates whether asset i is selected.

Require:

    sum(x_i) = K

For the first prototype use equal weights:

    w_i = x_i / K

Construct:

    maximize
        (1/K) μᵀx
        - λ/K² xᵀΣx

Convert it into a minimization QUBO by adding a cardinality penalty:

    A(sum(x_i) - K)^2

Be extremely careful with signs and factors of 2 in the quadratic coefficients.

Create a function that returns:
- QUBO matrix
- linear coefficients
- penalty
- metadata
- objective decoder

Add unit tests proving that the QUBO energy corresponds to the intended portfolio objective.

---

# PHASE 4 — EXACT SOLVER

Before GA, SA or QAOA, implement exhaustive enumeration for tiny N.

For every binary vector:
- calculate cardinality
- reject infeasible states
- calculate original portfolio objective
- identify optimum

This is the ground truth.

For N <= 12 this should normally be manageable.

Create a test showing that the QUBO representation and exact portfolio objective agree.

---

# PHASE 5 — GENETIC ALGORITHM

Implement a binary GA for exactly K selected assets.

Requirements:
- fixed random seed
- configurable population size
- configurable generations
- crossover
- mutation
- selection
- repair operator
- elite preservation if useful
- convergence history
- objective evaluations

The GA must use the SAME discrete portfolio objective as SA and QAOA.

Run multiple seeds in the benchmark.

---

# PHASE 6 — SIMULATED ANNEALING

Implement SA using the same binary representation.

Prefer a swap neighborhood:
- choose one selected asset
- choose one unselected asset
- swap them

This guarantees exactly K selections.

Record:
- best objective
- current objective
- iteration
- runtime
- objective evaluations

Use the same objective as GA/QAOA.

---

# PHASE 7 — QAOA

First verify the current Qiskit APIs.

Then implement:

1. QUBO construction
2. conversion to an appropriate quantum Hamiltonian/problem representation
3. QAOA circuit/algorithm
4. classical optimizer
5. simulator backend
6. measurement sampling
7. bitstring decoding
8. feasibility checking
9. best feasible solution selection

Start with:
- ideal simulator
- p = 1
- small N

Then test p = 2 if practical.

Record:
- number of qubits
- circuit depth
- number of shots
- runtime
- optimizer iterations
- best sampled objective
- feasibility rate
- probability/multiplicity of best solution if available

Do NOT claim QAOA solved the problem simply because an optimizer completed. Verify the returned bitstring.

If current Qiskit has changed APIs, adapt to the current version instead of forcing deprecated APIs.

---

# PHASE 8 — QAOA sanity benchmark

For N = 4, 6 and 8 where feasible:

Compare QAOA against exact enumeration.

Report:

    optimality gap =
        (best_known_objective - algorithm_objective)
        / |best_known_objective|

Use a clearly defined sign convention.

Also report:
- feasibility rate
- best-solution frequency if measurable

This is essential for interpreting QAOA.

---

# PHASE 9 — BACKTEST

Implement an out-of-sample evaluation.

Minimum version:

train period
→ estimate μ and Σ
→ optimize
→ hold during test period
→ calculate realized metrics

Then implement rolling/walk-forward evaluation if practical.

All methods must receive the same train/test windows.

Do not tune parameters using the test period.

---

# PHASE 10 — BENCHMARK

Create one experiment runner that can execute:

```text
exact
mvo
ga
sa
qaoa
```

for configurable:

```text
asset_count
K
risk_aversion
seed
date_range
qaoa_depth
shots
```

Save structured results as CSV/JSON.

Include:
- algorithm
- N
- K
- seed
- objective
- optimality gap
- feasibility
- runtime
- annual return
- volatility
- Sharpe
- Sortino
- max drawdown
- Calmar
- selected assets
- weights

---

# PHASE 11 — VISUALIZATION

Create publication-quality but simple figures:

1. efficient/risk-return comparison
2. cumulative wealth
3. drawdown
4. Sharpe comparison
5. objective gap
6. runtime vs N
7. feasibility vs N
8. convergence curves
9. portfolio weights

Use consistent methodology and labels.

Never compare incompatible quantities without explicitly labeling them.

---

# PHASE 12 — STATISTICAL ANALYSIS

For repeated seeds or repeated rolling windows:

- paired t-test where appropriate
- Wilcoxon signed-rank test
- confidence intervals
- effect sizes if practical

Clearly define the paired observations.

Do not manufacture statistical significance.

---

# PHASE 13 — FINAL NOTEBOOK

Create `08_final_benchmark.ipynb` that tells the complete story:

1. Research question
2. Dataset
3. Mathematical formulation
4. Why discrete QUBO is needed for QAOA
5. Exact ground truth
6. MVO
7. GA
8. SA
9. QAOA
10. Backtesting
11. Results
12. Statistical analysis
13. Scalability
14. Limitations
15. Conclusion

The conclusion MUST distinguish:
- empirical findings
- interpretation
- limitations
- future work

Do not write claims such as “quantum is faster” unless the experiments actually demonstrate that under the tested conditions.

---

# PHASE 14 — TESTING

Create unit tests for:

- returns
- covariance
- portfolio metrics
- MVO constraints
- binary encoding
- cardinality
- QUBO construction
- QUBO/objective equivalence
- exact solver
- GA feasibility
- SA feasibility
- QAOA decoding

Run the test suite.

Fix all failures.

---

# PHASE 15 — REPRODUCIBILITY

Create a README explaining exactly:

```bash
python -m venv .venv
# activate environment
pip install -r requirements.txt
jupyter lab
```

Also document:
- Python version
- Qiskit version
- data source
- experiment configuration
- random seeds
- how to reproduce results

---

# IMPORTANT ENGINEERING RULES

1. Do not create a giant monolithic notebook full of duplicated code.
2. Put reusable logic in `src/portfolio_opt`.
3. Keep notebooks focused on explanation and experiments.
4. Use type hints where useful.
5. Use docstrings.
6. Use assertions for financial/optimization constraints.
7. Avoid deprecated Qiskit APIs.
8. Do not silently catch exceptions.
9. Do not fabricate benchmark results.
10. Do not use future information.
11. Make every experiment configurable.
12. Prefer small working experiments before scaling.
13. After each major phase, run the relevant tests.
14. If an implementation choice is mathematically ambiguous, document the convention in the code and README.
15. When QAOA cannot scale to a requested N on the available simulator, report the limitation and continue with the largest reproducible size.

## Development style

Work in small milestones.

After completing each milestone:
- run tests
- run a tiny example
- inspect outputs
- fix errors
- update README if the design changed

At the end, provide:
1. project tree
2. commands to run
3. notebook execution order
4. key assumptions
5. known limitations
6. next experiments I should run
