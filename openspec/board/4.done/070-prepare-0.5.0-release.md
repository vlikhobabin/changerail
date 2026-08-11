# Подготовить и опубликовать релиз 0.5.0

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Planning State
release metadata prepared; awaiting release verification, independent review
and publish

## Series
- none

## Series Index
- none

## Source
- Release readiness audit on 2026-08-11.
- Diff since `v0.4.0`.

## Summary
Оформить `0.5.0` как следующий pre-stable release после `v0.4.0`, включив
repository knowledge/maintenance surface, consumer bootstrap hardening,
runtime diagnostics, generated consumer CI и release baseline updates.

## Acceptance
- `VERSION` содержит `0.5.0`.
- `CHANGELOG.md` содержит раздел `0.5.0 - 2026-08-11` с основными Added,
  Changed, Fixed и Breaking entries; `Unreleased` сброшен в `none`.
- Compatibility notes, migration guide, release discipline и security policy
  соответствуют `0.5.0`.
- Card-owned release-prep OpenSpec artifacts архивированы и не оставляют
  active OpenSpec changes.
- Full release baseline, public-surface current/history scans, OpenSpec strict
  validation and whitespace check pass before publish.
- Fresh independent review returns `go` for the release payload.
- Release is published through a scoped commit, tag `v0.5.0`, push to
  `origin/main` and GitHub release when the authenticated `gh` surface is
  available.

## Change Set
- `prepare-0-5-0-release`

## Verify
- `bin/changerail-python scripts/changerail_delivery_manifest.py derive
  openspec/board/3.inprogress/070-prepare-0.5.0-release.md --workspace .
  --write --json` -> wrote ignored manifest
  `.runtime/changerail/delivery-manifests/070-prepare-0.5.0-release.json`.
- `bin/changerail-python scripts/changerail_delivery_manifest.py scope-check
  .runtime/changerail/delivery-manifests/070-prepare-0.5.0-release.json
  --target working-tree --json` -> `ok: true`, no missing, extra or mismatched
  paths.
- `./bin/openspec list --json` -> `{"changes":[]}`.
- `./bin/openspec validate --all --strict` -> `23` passed, `0` failed.
- `python3 scripts/run-release-baseline.py` -> pass `33/33`; included
  OpenSpec strict validation, JSON/TOML parsing, contract schema validation,
  Python syntax inventory, runtime smoke, Windows deterministic smokes, ruff,
  CI workflow smoke, public-surface current/history scans, wiring discovery,
  verify-project, runtime diagnostics, bootstrap, consumer CI, review/verdict,
  retained evidence, maintenance runner, delivery manifest/runner/metrics,
  archive diagnostics, generated drift fixture and git checks.
- `python3 scripts/public-surface-scan.py` inside baseline -> pass `936` files
  scanned, `0` findings.
- `python3 scripts/public-surface-scan.py --history` inside baseline -> pass
  `936` files scanned, `0` findings.
- `python3 scripts/smoke-windows-matrix.py` inside baseline -> pass `6/7`,
  `0` failed, `1` not-run; live two-host smoke was not requested, so this
  release does not claim fresh live two-host coverage beyond existing
  compatibility evidence.
- `git diff --check` inside baseline -> passed.

## Archive
- `openspec/changes/archive/2026-08-11-prepare-0-5-0-release/`

## Related
- `VERSION`
- `CHANGELOG.md`
- `docs/compatibility.md`
- `docs/migration-guide.md`
- `docs/release-discipline.md`
- `SECURITY.md`

## Change 1: `prepare-0-5-0-release`

### Why
The repository has green release verification after 15 commits since `v0.4.0`,
but release metadata still describes `0.4.0` and does not expose the new
maintenance/bootstrap surface as a published version.

### Goal
Prepare and publish a reviewed `0.5.0` release with accurate release metadata,
migration guidance and operator-facing release notes.

### Acceptance
- Release metadata and migration docs are updated for `0.5.0`.
- Mandatory release checks pass.
- Fresh review and publish gates complete before tag/release publication.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-08-11-prepare-0-5-0-release/`

## Result
release metadata prepared and verified; awaiting fresh review and publish

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- `2026-08-11T10:10:00Z` release-prep card created from readiness audit.
- `2026-08-11T10:36:00Z` release-prep metadata verified by full release
  baseline, public-surface scans and manifest scope check.
- `2026-08-11T10:56:00Z` review cycle 1 returned `no-go` for invalid
  dotted change slug and unsynced release-discipline delta spec; slug changed
  to `prepare-0-5-0-release` and the requirement was synced before re-review.
- `2026-08-11T11:12:00Z` after R1/R2 fixes, delivery manifest classified
  `prepare-0-5-0-release` as archived and full release baseline passed `33/33`.
- 2026-08-11T11:22:40Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
