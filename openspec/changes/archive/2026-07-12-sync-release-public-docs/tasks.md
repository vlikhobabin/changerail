## 1. Public docs sync
- [x] Update `AGENTS.md` current/planned surface lists.
- [x] Update `README.md` current status and next directions for runner,
  metrics, schemas, public-safety helper, release gate and baseline command.
- [x] Update `docs/release-discipline.md`, `docs/compatibility.md` and
  `docs/migration-guide.md` for current release checks and user-facing
  post-`0.1.0` changes.
- [x] Update `CHANGELOG.md` Unreleased entries for runner, metrics, manifest,
  review history/fingerprint, aliases, public scans, finalization and release
  baseline work.

## 2. Public safety
- [x] Ensure examples remain generic (`/opt/changerail`,
  `/opt/example-project`, `/opt/example-a`, `/opt/example-b`).
- [x] Keep private migration notes and runtime evidence out of tracked docs.

## 3. Verification
- [x] Run Markdown/link or relevant docs checks available in the repo.
  Outcome: no dedicated markdown/link checker is tracked; relevant docs checks
  ran through `python3 scripts/run-release-baseline.py` and passed 25/25 steps.
- [x] Run `python3 scripts/public-surface-scan.py`.
  Outcome: pass, 416 files scanned, 0 findings.
- [x] Run `openspec validate sync-release-public-docs --strict`.
  Outcome: pass.
