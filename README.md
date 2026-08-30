# Quantum Portfolio Optimization Prototype Kit

This kit contains instructions and prompts for building the capstone prototype described in the research proposal.

## Files

- `SKILL.md` — persistent engineering/research rules for the coding agent.
- `PROTOTYPE_SPEC.md` — mathematical and experimental specification.
- `MASTER_PROMPT.md` — complete start-to-finish Codex prompt.
- `CODEX_EXECUTION_PLAN.md` — safer milestone-by-milestone prompts.

## Recommended workflow

1. Create a new Git repository.
2. Copy these four files into the repository.
3. Start Codex.
4. Give it `MASTER_PROMPT.md`.
5. Prefer executing the milestone prompts one at a time.
6. Commit after each successful milestone.
7. Never accept a QAOA result before comparing it with exact enumeration on a tiny instance.

## Most important design decision

The project should not force continuous MVO directly into a binary quantum formulation without explaining the mismatch.

Use:

- MVO → continuous allocation baseline.
- GA / SA / QAOA → identical binary asset-selection problem.
- Exact enumeration → ground truth for small instances.

An optional second experiment can apply common MVO allocation after GA/SA/QAOA select the assets.

## Prototype philosophy

Start with 4–8 assets and an ideal simulator.

Only scale after:
- the mathematics is validated,
- QUBO mapping is validated,
- QAOA decoding is validated,
- exact enumeration agrees with the formulation.

The purpose is to produce defensible empirical evidence, not a marketing demonstration of quantum computing.
