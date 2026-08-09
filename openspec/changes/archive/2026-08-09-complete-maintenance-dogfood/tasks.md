## 1. Dogfood Configuration

- [x] 1.1 Extend `.changerail/knowledge.yaml` with the accepted canonical ChangeRail knowledge scope.
- [x] 1.2 Extend `.changerail/maintenance.yaml` with explicit include/exclude globs and enabled deterministic detectors.
- [x] 1.3 Regenerate `.changerail/KNOWLEDGE.md` with `bin/changerail-maintenance render-index --write`.
- [x] 1.4 Ensure root `bin/changerail-maintenance scan --json` has non-zero detector coverage and does not mutate tracked files.

## 2. Boundary Fixtures

- [x] 2.1 Add or update fixtures for broken local links and stale anchors with stable detector codes.
- [x] 2.2 Add or update fixtures for stale generated index behavior without check-mode mutation.
- [x] 2.3 Add optional instruction-producer/quality fixture coverage that leaves instruction bytes as `unknown`.
- [x] 2.4 Add contradiction annotation fixture coverage that remains annotation-only and not a deterministic scan gate.

## 3. Smoke Coverage

- [x] 3.1 Extend `scripts/smoke-repository-knowledge.py` for dogfood detector coverage and new boundary fixtures.
- [x] 3.2 Ensure feedback/runtime-dependent adapters are exercised only through fixtures and do not require pre-existing ignored history.
- [x] 3.3 Confirm public-safe fixture content contains only generic paths and no local runtime traces.

## 4. Verification

- [x] 4.1 Run `./bin/openspec validate complete-maintenance-dogfood --strict`.
- [x] 4.2 Run `bin/changerail-maintenance validate-catalog`.
- [x] 4.3 Run `bin/changerail-maintenance render-index --check`.
- [x] 4.4 Run `bin/changerail-maintenance scan --json`.
- [x] 4.5 Run `python3 scripts/smoke-repository-knowledge.py`.
- [x] 4.6 Run `python3 scripts/smoke-contract-schemas.py`.
- [x] 4.7 Run `git diff --check`.
- [x] 4.8 Run `python3 scripts/public-surface-scan.py`.
