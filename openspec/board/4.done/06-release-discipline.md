# Версионирование и релизная дисциплина (Фаза 6)

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- OPSX roadmap, раздел 12, Фаза 6 (`docs/opsx-source-of-truth-architecture.md`).
- Раздел 14 (риск always-latest symlink) и раздел 15 (открытые решения).

## Summary
Сделать OPSX самостоятельной поддерживаемой технологией: ввести semver,
changelog с breaking-маркерами, compatibility notes для Codex CLI, Claude Code и
OpenSpec CLI, migration notes между версиями и CI для templates, bootstrap,
verify, drift и wiring smoke.

## Acceptance
- Введена и задокументирована semver-схема.
- Есть changelog с явными breaking-маркерами.
- Compatibility notes покрывают Codex CLI, Claude Code и OpenSpec CLI.
- Есть migration notes между версиями OPSX.
- CI прогоняет templates, bootstrap, verify, drift и wiring smoke; красно-зеленый.

## Change Set
- `add-release-versioning-docs`
- `add-release-ci-gate`

## Verify
- passed: `openspec validate add-release-versioning-docs --strict`
- passed: `openspec validate add-release-ci-gate --strict`
- passed: `openspec validate opsx-release-discipline --strict`
- passed: `openspec validate opsx-release-ci --strict`
- passed: `openspec validate --all --strict`
- passed: `./bin/openspec validate --all --strict`
- passed: `python3 -m json.tool .mcp.json`
- passed: TOML parse for `.codex/config.toml`
- passed: `git diff --check`
- passed: `python3 -m py_compile scripts/smoke-release-ci.py`
- passed: `python3 scripts/smoke-release-ci.py` (21/21)
- passed: `python3 -m py_compile bin/bootstrap-project bin/verify-project scripts/opsx_review_verdict.py scripts/smoke-bootstrap-project.py scripts/smoke-drift.py scripts/smoke-release-ci.py scripts/smoke-verify-project.py scripts/smoke-wiring-discovery.py`
- passed: `python3 scripts/smoke-wiring-discovery.py` (118/118)
- passed: `python3 scripts/smoke-verify-project.py` (2/2)
- passed: `python3 scripts/smoke-bootstrap-project.py` (4/4)
- passed: generated-fixture drift check with `scripts/smoke-drift.py --project .runtime/opsx/ci-drift/example-project` (1/1)

## Archive
- `openspec/changes/archive/2026-07-08-add-release-versioning-docs/`
- `openspec/changes/archive/2026-07-08-add-release-ci-gate/`

## Related
- `openspec/changes/archive/2026-07-08-add-release-versioning-docs/`
- `openspec/changes/archive/2026-07-08-add-release-ci-gate/`
- `docs/opsx-source-of-truth-architecture.md`
- `docs/release-discipline.md`
- `docs/compatibility.md`
- `docs/migration-guide.md`
- `.github/workflows/opsx-ci.yml`
- `scripts/smoke-release-ci.py`
- `scripts/smoke-wiring-discovery.py`
- `bin/openspec` (compatibility pin из Фазы 1)

## Result
Implemented and archived `add-release-versioning-docs` and
`add-release-ci-gate`. External review cycle 1 returned a fresh `go` verdict;
publish proceeds with ignored runtime artifacts excluded.

## Next
- Continue with `openspec/board/1.backlog/04-migrate-existing-consumers.md`.

## Change 1: `add-release-versioning-docs`

### Why
OPSX consumers need a public release contract before `/opt/opsx` can be treated
as a maintained technology instead of an always-latest local checkout.

### Goal
Add semver, changelog, compatibility and migration documentation that is safe
for public consumption and useful for consumer update decisions.

### Scope
- Add root version/changelog files.
- Add release discipline, compatibility and migration docs.
- Update README and architecture references.

### Acceptance
- `VERSION` contains a semver value.
- `CHANGELOG.md` documents breaking marker policy.
- Compatibility notes cover Codex CLI, Claude Code and OpenSpec CLI.
- Migration notes describe version-to-version update checks.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-08-add-release-versioning-docs/`

## Change 2: `add-release-ci-gate`

### Why
Release docs need an enforceable red/green gate so workflow, template and drift
regressions are caught before publication.

### Goal
Add a tracked CI workflow and local smoke validator that run OPSX release
verification for templates, bootstrap, verify, drift and wiring smoke.

### Scope
- Add `.github/workflows/opsx-ci.yml`.
- Add `scripts/smoke-release-ci.py`.
- Document CI in release docs or README.

### Acceptance
- CI workflow includes OpenSpec validation, docs/config checks and Python
  syntax checks.
- CI workflow runs wiring, verify-project, bootstrap and drift smoke.
- Drift CI uses generated generic runtime fixtures only.
- Local CI contract smoke passes.

### Depends On
- `add-release-versioning-docs`

### Related
- `openspec/changes/archive/2026-07-08-add-release-ci-gate/`

## Log
- 2026-07-08T14:05:27Z card created from roadmap phase 6 scope.
- 2026-07-08T18:10:03Z `$opsx-ff` decomposed story into release docs and CI gate changes.
- 2026-07-08T18:10:03Z `$opsx-ff` completed artifacts and moved card to `3.inprogress`.
- 2026-07-08T18:18:00Z `$opsx-do` implemented release docs, semver/changelog, compatibility notes and migration guide.
- 2026-07-08T18:19:00Z `$opsx-do` implemented release CI workflow and CI contract smoke.
- 2026-07-08T18:19:30Z `$opsx-do` synced specs and archived both planned changes.
- 2026-07-08T18:19:30Z delivery stopped before review by operator instruction; awaiting external fresh-context review.
- 2026-07-08T18:26:34Z external review cycle 1 returned `go`; verdict
  validated fresh against HEAD `69a24ede9b4a949a46b779872f1daa0abd7cc5bb`
  with fingerprint
  `sha256:83fcacc8ae09d76e2291c261099b2d40f320aafe9726de7269e505fa087b06bf`.
- 2026-07-08T18:26:34Z card moved to `4.done` for scoped publish; runtime
  review verdict and delivery manifest remain excluded from commit.
