## 1. Bootstrap And Templates

- [x] 1.1 Add bootstrap `--config-mode portable|local` with portable default.
- [x] 1.2 Update templates to avoid machine-local absolute target paths in
  default tracked output.
- [x] 1.3 Print explicit local-config warning before suggested staging when
  local mode is selected.

## 2. Verification

- [x] 2.1 Update `bin/verify-project` to validate portable relative scope.
- [x] 2.2 Update bootstrap and verify smoke fixtures for portable default and
  local opt-in warning.

## 3. Docs And Checks

- [x] 3.1 Update template/bootstrap docs with portable/local config model.
- [x] 3.2 Run `python3 scripts/smoke-bootstrap-project.py`.
- [x] 3.3 Run `python3 scripts/smoke-verify-project.py`.
- [x] 3.4 Run `./bin/openspec validate add-portable-bootstrap-config --strict`.
- [x] 3.5 Run `git diff --check`.

## Verification Notes

- `python3 -m py_compile bin/bootstrap-project bin/verify-project scripts/smoke-bootstrap-project.py scripts/smoke-verify-project.py` passed.
- `python3 scripts/smoke-bootstrap-project.py` passed with 5/5 checks.
- `python3 scripts/smoke-verify-project.py` passed with 6/6 checks.
- `./bin/openspec validate add-portable-bootstrap-config --strict` passed.
- `git diff --check` passed.
- RED evidence is not applicable: this is bootstrap/config hardening. The
  added smoke coverage renders real fixtures and would fail if portable config
  leaked the generated project path or if unsafe relative scope passed
  verification.
