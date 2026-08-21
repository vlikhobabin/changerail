## 1. Runtime isolation

- [x] 1.1 Add default ignored runtime-home resolution, private atomic trust config preparation and auth-marker linking without credential reads or copies.
- [x] 1.2 Split default preflight across project policy and runtime state while preserving explicit `CODEX_HOME` behavior and project-local stale-link diagnostics.

## 2. Regression coverage

- [x] 2.1 Update existing environment/preflight smoke expectations for the isolated default home.
- [x] 2.2 Add a mutation-regression smoke that simulates persisted absolute trust and proves tracked project config remains byte-identical, ignored and git-clean.

## 3. Documentation and verification

- [x] 3.1 Update delivery contracts, workflow and consumer adoption docs with the configuration-layer boundary and remediation paths.
- [x] 3.2 Run `python3 scripts/smoke-delivery-runner.py`, `python3 scripts/run-release-baseline.py`, `bin/openspec validate --all --strict`, `python3 scripts/public-surface-scan.py` and `git diff --check`; retain concise outcomes and complete the card artifacts.

## 4. Review rescue

- [x] 4.1 Reject symlinks in the runner-owned runtime-home directory chain before any chmod or file reconciliation.
- [x] 4.2 Add a negative smoke proving a directory alias cannot change tracked project config or launch a child, then rerun the mandatory verification floor.
