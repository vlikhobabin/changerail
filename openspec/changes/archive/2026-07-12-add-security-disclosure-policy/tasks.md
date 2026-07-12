## 1. Policy

- [x] 1.1 Add `SECURITY.md` with supported versions, private disclosure
  channel and report guidelines.
- [x] 1.2 Link the policy from `README.md` and release docs.

## 2. Verification

- [x] 2.1 Update release discipline spec/docs for security policy checks.
- [x] 2.2 Run `python3 scripts/public-surface-scan.py --history`.
- [x] 2.3 Run `./bin/openspec validate add-security-disclosure-policy --strict`.
- [x] 2.4 Run `git diff --check`.

## Verification Notes

- `python3 scripts/public-surface-scan.py --json` passed with 0 findings.
- `python3 scripts/public-surface-scan.py --history --json` passed with 0
  findings.
- `./bin/openspec validate add-security-disclosure-policy --strict` passed.
- `./bin/openspec validate changerail-release-discipline --strict` passed.
- `git diff --check` passed.
- RED evidence is not applicable: this is policy/docs/spec work. The
  public-surface scan verifies the tracked policy and final public payload do
  not introduce secrets, private workspace names or machine-local paths.
