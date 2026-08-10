## 1. Starter Maintenance Output

- [x] 1.1 Extend maintenance starter catalog records for `.changerail/knowledge.yaml`, `.changerail/maintenance.yaml` and `openspec/board/card-template.md`.
- [x] 1.2 Generate a deterministic `.changerail/KNOWLEDGE.md` for fresh `--with-maintenance` bootstrap output.
- [x] 1.3 Preserve default bootstrap output when `--with-maintenance` is absent.
- [x] 1.4 Preserve project-owned catalog and policy customization on repeat bootstrap or refresh.

## 2. First-Run Regression Coverage

- [x] 2.1 Add or extend disposable consumer smoke coverage for first-run `validate-catalog --json`.
- [x] 2.2 Add or extend disposable consumer smoke coverage for first-run `render-index --check`.
- [x] 2.3 Add or extend disposable consumer smoke coverage for first-run `scan --json` below the configured threshold.
- [x] 2.4 Record why the smoke would fail for the missing-index/uncovered starter regression.

## 3. Verification

- [x] 3.1 Run `python3 -m py_compile bin/bootstrap-project scripts/smoke-bootstrap-project.py scripts/smoke-repository-knowledge.py`.
- [x] 3.2 Run `python3 scripts/smoke-bootstrap-project.py`.
- [x] 3.3 Run `python3 scripts/smoke-repository-knowledge.py`.
- [x] 3.4 Run a fresh disposable `--with-maintenance` validate/index/scan command sequence.
- [x] 3.5 Run `./bin/openspec validate make-maintenance-bootstrap-first-run-green --strict`.
- [x] 3.6 Run `git diff --check`.
