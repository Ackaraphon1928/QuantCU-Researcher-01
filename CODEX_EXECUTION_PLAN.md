# Codex Execution Plan

Use this sequence rather than asking Codex to build everything in one uncontrolled step.

## Milestone 1 — Skeleton
Prompt:
> Read SKILL.md, PROTOTYPE_SPEC.md and MASTER_PROMPT.md. Inspect the environment and create the repository skeleton only. Do not implement algorithms yet. Verify Python/Qiskit versions and choose compatible dependencies.

## Milestone 2 — Data + metrics
Prompt:
> Implement the data pipeline and portfolio metrics. Create a tiny deterministic dataset for tests. Add tests and make 01_data_exploration.ipynb run end-to-end.

## Milestone 3 — Mathematical formulation
Prompt:
> Implement MVO, binary selection, equal-weight portfolio construction, QUBO construction and exhaustive exact solver. Prove with unit tests that QUBO energy and the original discrete objective are consistent.

## Milestone 4 — GA
Prompt:
> Implement GA using exactly the same discrete objective. Add repair, convergence tracking, tests and a small benchmark against exact enumeration.

## Milestone 5 — SA
Prompt:
> Implement swap-based simulated annealing using the same discrete objective. Add convergence tracking, tests and comparison with exact enumeration.

## Milestone 6 — QAOA
Prompt:
> Implement QAOA using the currently supported Qiskit APIs. Start with N=4 and p=1 on an ideal simulator. Compare against exact enumeration before attempting larger N.

## Milestone 7 — Unified benchmark
Prompt:
> Build a configuration-driven experiment runner for exact/MVO/GA/SA/QAOA. Save structured CSV/JSON results and benchmark N=4,6,8 with multiple seeds where practical.

## Milestone 8 — Backtest
Prompt:
> Implement chronological out-of-sample and then rolling/walk-forward evaluation. Ensure no look-ahead bias and identical windows across algorithms.

## Milestone 9 — Statistics + plots
Prompt:
> Add paired statistical analysis and all required plots. Make every plot traceable to saved result files.

## Milestone 10 — Final notebook
Prompt:
> Build 08_final_benchmark.ipynb as a polished research narrative. Include assumptions, exact ground truth, all algorithms, backtest results, scalability, limitations and honest conclusions.

## Milestone 11 — Reproducibility audit
Prompt:
> Pretend you are a new researcher cloning this repository. Recreate the environment, run tests and execute the prototype. Fix anything that prevents full reproduction.
