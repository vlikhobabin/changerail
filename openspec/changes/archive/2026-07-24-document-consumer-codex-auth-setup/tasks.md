## 1. Documentation

- [x] 1.1 Add a canonical consumer Codex auth setup section to
  `docs/consumer-adoption-runbook.md`.
- [x] 1.2 Update `docs/how-it-works.md` and `docs/changerail-contracts.md` to
  point runner auth failures to the canonical setup section.
- [x] 1.3 Verify examples use only public-safe paths such as
  `/opt/example-project` and `$HOME`.

## 2. Verification

- [x] 2.1 Run `./bin/openspec validate "document-consumer-codex-auth-setup" --strict`.
- [x] 2.2 Run `./bin/openspec validate --all --strict`.
- [x] 2.3 Run `git diff --check`.
- [x] 2.4 Run `python3 scripts/public-surface-scan.py`.

## Verification Notes

- `./bin/openspec validate "document-consumer-codex-auth-setup" --strict` passed.
- `./bin/openspec validate --all --strict` passed with 18 items.
- `git diff --check` passed.
- `python3 scripts/public-surface-scan.py` passed with 517 files scanned and 0 findings.
