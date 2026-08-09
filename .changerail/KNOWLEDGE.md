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
| `docs/changerail-contracts.md` | active | reference | ChangeRail core | none | python3 scripts/smoke-contract-schemas.py |
| `docs/changerail-source-of-truth-architecture.md` | active | architecture | ChangeRail core | none | ./bin/openspec validate --all --strict |
