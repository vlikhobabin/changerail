# Repository Knowledge Index

Generated from the tracked ChangeRail repository knowledge catalog.

- Catalog: `.changerail/knowledge.yaml`
- Policy: `.changerail/maintenance.yaml`
- Index: `.changerail/KNOWLEDGE.md`

| Path | Status | Type | Owner | Review After | Verify |
| --- | --- | --- | --- | --- | --- |
| `.changerail/KNOWLEDGE.md` | generated | generated | ChangeRail core | none | bin/changerail-maintenance render-index --check |
| `AGENTS.shared.md` | active | reference | ChangeRail core | none | ./bin/openspec validate --all --strict, git diff --check |
| `README.md` | active | explanation | ChangeRail core | none | python3 scripts/public-surface-scan.py |
| `SECURITY.md` | active | reference | ChangeRail core | none | python3 scripts/public-surface-scan.py |
| `docs/board-and-two-agent-feature-flow.md` | active | how-to | ChangeRail core | none | ./bin/openspec validate --all --strict, python3 scripts/public-surface-scan.py |
| `docs/changerail-contracts.md` | active | reference | ChangeRail core | none | python3 scripts/smoke-contract-schemas.py |
| `docs/changerail-source-of-truth-architecture.md` | active | architecture | ChangeRail core | none | ./bin/openspec validate --all --strict |
| `docs/compatibility.md` | active | reference | ChangeRail core | none | python3 scripts/run-release-baseline.py |
| `docs/consumer-adoption-runbook.md` | active | runbook | ChangeRail core | none | python3 scripts/public-surface-scan.py |
| `docs/how-it-works.md` | active | explanation | ChangeRail core | none | python3 scripts/public-surface-scan.py |
| `docs/maintenance-operations-runbook.md` | active | runbook | ChangeRail core | none | python3 scripts/public-surface-scan.py, python3 scripts/smoke-contract-schemas.py |
| `docs/migration-guide.md` | active | how-to | ChangeRail core | none | python3 scripts/public-surface-scan.py |
| `docs/openspec-lifecycle.md` | active | reference | ChangeRail core | none | ./bin/openspec validate --all --strict |
| `docs/release-discipline.md` | active | runbook | ChangeRail core | none | python3 scripts/run-release-baseline.py, python3 scripts/public-surface-scan.py |
| `docs/wiring-discovery.md` | active | reference | ChangeRail core | none | python3 -m json.tool .mcp.json, python3 scripts/public-surface-scan.py |
