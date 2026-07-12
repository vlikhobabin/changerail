## 1. Smoke Coverage

- [x] 1.1 Extend `scripts/smoke-bootstrap-project.py` to inspect generated
  `AGENTS.md`.
- [x] 1.2 Extend the smoke to inspect generated `openspec/board/README.md`.
- [x] 1.3 Check lifecycle, role model, fresh review gate and
  `3.inprogress -> 4.done` guidance.

## 2. Verification

- [x] 2.1 Run `python3 scripts/smoke-bootstrap-project.py`.
- [x] 2.2 Run `./bin/openspec validate "add-bootstrap-workflow-guidance-smoke" --strict`.
- [x] 2.3 Run `./bin/openspec validate --all --strict`.
- [x] 2.4 Run `git diff --check`.

## Verification Notes

- `python3 scripts/smoke-bootstrap-project.py` passed.
- `python3 scripts/smoke-release-ci.py` passed and now checks the bootstrap
  smoke remains in CI.
- `./bin/openspec validate add-bootstrap-workflow-guidance-smoke --strict` passed.
- `./bin/openspec validate --all --strict` passed with 18 items before archive.
- `git diff --check` passed.
