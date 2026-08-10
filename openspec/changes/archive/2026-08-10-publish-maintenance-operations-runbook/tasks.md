## 1. Runbook

- [x] 1.1 Add a public Russian maintenance operations runbook for new and existing consumers.
- [x] 1.2 Document catalog, policy, generated index, first scan, state, baseline/waiver, audit, triage and card handoff.
- [x] 1.3 Document scheduler, feedback and quality flows with public-safe POSIX and supported native Windows examples.
- [x] 1.4 Separate read-only/default commands from explicit write operations and publication authority.

## 2. Documentation Indexing

- [x] 2.1 Link the runbook from `README.md`.
- [x] 2.2 Link the runbook from `docs/consumer-adoption-runbook.md`.
- [x] 2.3 Index scheduler examples with prerequisites and least-privilege notes.
- [x] 2.4 Update `docs/changerail-contracts.md` schema inventory and feedback/quality references.

## 3. Verification

- [x] 3.1 Run `python3 -m json.tool .mcp.json`.
- [x] 3.2 Run TOML parsing for `.codex/config.toml`.
- [x] 3.3 Run `./bin/openspec validate publish-maintenance-operations-runbook --strict`.
- [x] 3.4 Run `python3 scripts/smoke-contract-schemas.py`.
- [x] 3.5 Run `python3 scripts/public-surface-scan.py`.
- [x] 3.6 Run `git diff --check`.
