# Prototype Specification

## Project title

Benchmarking Classical and Quantum Optimization Algorithms for Portfolio Selection

## Goal

Create a research-grade but manageable prototype comparing MVO, GA, SA and QAOA for long-only portfolio selection.

## Key design decision

Use **two related formulations**:

### Track A — Continuous portfolio allocation
MVO solves:

max μᵀw - λ wᵀΣw

s.t.:
- sum(w) = 1
- w >= 0
- optional upper bounds

### Track B — Discrete portfolio selection
GA, SA and QAOA solve the same binary selection problem:

x_i ∈ {0,1}
sum(x_i) = K

with equal-weight selected assets:

w_i = x_i / K

Objective:

maximize expected return minus risk penalty.

This avoids pretending that a binary QAOA solution directly solves the same continuous allocation problem as MVO.

## Fair benchmark

The most important comparison is:

**GA vs SA vs QAOA on the same discrete QUBO**

MVO is a complementary continuous benchmark.

Optionally, after selecting K assets, run a common continuous allocator over those assets. This creates a useful two-stage experiment:

1. selection: GA / SA / QAOA
2. allocation: common MVO allocator

That experiment should be labeled separately from the pure equal-weight experiment.

## Minimum experiment

Universe:
- 6 assets
- K = 3
- one training period
- one out-of-sample period

Algorithms:
- exact enumeration
- MVO
- GA
- SA
- QAOA

Quantum:
- ideal simulator
- p = 1 initially
- then p = 2 if feasible

The exact enumeration result is the ground truth for the discrete problem.

## Scaling experiment

Increase N gradually:

6 → 8 → 10 → 12

Do not jump directly to large universes.

Measure:
- objective gap
- runtime
- feasibility
- financial metrics
- quantum circuit size / qubit count

## Recommended notebook storyline

### 01 — Data
Load prices, clean, visualize, calculate returns.

### 02 — Formulation
Explain MPT, μ, Σ, variance, λ, K, binary encoding and QUBO.

### 03 — Exact + MVO
Use brute force for tiny discrete instances and CVXPY for MVO.

### 04 — GA
Implement and validate.

### 05 — SA
Implement and validate.

### 06 — QAOA
Build QUBO, convert to quantum operator, run QAOA, decode bitstrings.

### 07 — Backtest
Walk-forward/out-of-sample evaluation.

### 08 — Benchmark
Aggregate results, statistical tests, figures, conclusions.

## Acceptance criteria

Every algorithm must return a normalized, interpretable portfolio.

Every discrete algorithm must be checked against exact enumeration for small N.

The notebook must contain assertions for:
- budget
- long-only constraint
- cardinality
- finite objective
- no NaNs

All results must be saved.

## Suggested first dataset

Use a small manually specified set of liquid equities/ETFs for the first proof-of-concept. The exact universe should be configurable rather than hard-coded.

The full S&P 500 / NASDAQ-100 experiment is a later scaling study, not the first prototype.
