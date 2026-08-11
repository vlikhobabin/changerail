## 1. Release Metadata

- [x] 1.1 Update `VERSION` to `0.5.0`.
- [x] 1.2 Add `CHANGELOG.md` section `0.5.0 - 2026-08-11`.
- [x] 1.3 Move `Unreleased` migration notes into `0.4.0 -> 0.5.0`.
- [x] 1.4 Update compatibility notes, release discipline and security policy.

## 2. Review Scope

- [x] 2.1 Add release-prep board card.
- [x] 2.2 Add archived release-prep OpenSpec artifacts.
- [x] 2.3 Derive delivery manifest for the release-prep card.
- [x] 2.4 Sync the release metadata requirement into the main
  `changerail-release-discipline` spec.

## 3. Verification And Publish

- [x] 3.1 Run `python3 scripts/run-release-baseline.py`.
- [x] 3.2 Run `./bin/openspec validate --all --strict`.
- [x] 3.3 Run current and history public-surface scans.
- [x] 3.4 Run `git diff --check`.
- [ ] 3.5 Obtain fresh independent review verdict.
- [ ] 3.6 Commit, tag `v0.5.0`, push and create GitHub release.
