## 1. Harness

- [x] 1.1 Add `scripts/windows-runtime-wiring-probe.py` with sample dry-run,
  ignored inventory validation and sanitized live report generation.
- [x] 1.2 Implement disposable Windows fixture checks for directory symlink,
  file symlink, junction, generated copy drift/source update, wrapper launch
  variants and Git traversal/index behavior.
- [x] 1.3 Retain raw live output only under ignored `.runtime/changerail/`
  evidence paths and sanitize printed/report diagnostics.

## 2. Verification

- [x] 2.1 Run `python3 scripts/windows-runtime-wiring-probe.py dry-run --sample --json`.
- [x] 2.2 Run `python3 -m py_compile scripts/windows-runtime-wiring-probe.py`.
- [x] 2.3 Run `./bin/openspec validate add-windows-runtime-wiring-probe --strict`.
- [x] 2.4 Run `git diff --check`, covering the new untracked script.
