# Исправить publish finalization и ledger model

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`010-core-release-contracts`

## Series Index
`03`

## Source
- Два независимых consumer delivery run подтвердили self-invalidating tracked
  publish metadata.

## Summary
Убрать exact final commit hash и mutable push state из tracked done-card,
разделить payload и published commits в ignored manifest и сделать
card-only finalization whitespace-safe.

## Acceptance
- Tracked done-card не содержит собственный final commit hash.
- Push-enabled flow не оставляет stale pending-push wording в tracked результате.
- Ignored manifest различает `payload_commit` и `published_commit` и хранит
  final remote/branch/status/timestamp.
- После board move manifest содержит final `card.path` и `card.status`.
- `finalize-card` не создает blank line at EOF или иной `git diff --check`
  defect.
- Local bare-remote regression smoke проходит commit, finalize, amend, push и
  publish-update без stale metadata.

## Scope
- Delivery manifest schema/helper.
- `changerail-pub` contract и publish/finalization docs.
- Focused finalization smoke и migration note.

## Non-Goals
- Полная scope reconciliation: карточка `010-04`.
- Remote retry/resume: карточка `020-03`.

## Depends On
- `010-02-establish-supported-python-runtime`

## Implementation Notes
- Tracked card должна содержать только стабильный outcome; exact pushed commit
  доступен из Git history и ignored ledger.
- Финализация после `go` не может менять substantive reviewed payload.

## Change Set
- `fix-publish-finalization-ledger` (archived)

## Change 1: `fix-publish-finalization-ledger`

### Why
Tracked done-card metadata не может заранее содержать собственный final commit
hash, а mutable push state в карточке делает published result self-invalidating.

### Goal
Разделить stable tracked finalization и ignored publish ledger так, чтобы scoped
publish не оставлял stale или impossible metadata в board card.

### Scope
- Delivery manifest schema/helper.
- `changerail-pub` contract и publish/finalization docs.
- Focused finalization regression smoke с local bare remote.

### Acceptance
- Tracked done-card не содержит собственный final commit hash.
- Push-enabled flow не оставляет stale pending-push wording в tracked результате.
- Ignored manifest различает `payload_commit` и `published_commit` и хранит
  final remote/branch/status/timestamp.
- После board move manifest содержит final `card.path` и `card.status`.
- `finalize-card` не создает blank line at EOF или иной `git diff --check`
  defect.
- Local bare-remote regression smoke проходит commit, finalize, amend, push и
  publish-update без stale metadata.

### Depends On
- `establish-supported-python-runtime`

### Related
- `openspec/changes/archive/2026-08-01-fix-publish-finalization-ledger/`

## Verify
- `python3 scripts/smoke-delivery-manifest.py` passed.
- `python3 scripts/smoke-contract-schemas.py` passed: `7` schemas.
- `python3 scripts/smoke-delivery-manifest-derive.py` passed; includes local
  bare-remote payload commit, `finalize-card`, card-only amend, `git show
  --check --oneline HEAD`, push and `publish-update` regression path.
- `./bin/openspec validate changerail-contracts --strict` passed.
- `./bin/openspec validate changerail-agent-methodology --strict` passed.
- `./bin/openspec validate changerail-skill-surface --strict` passed.
- `./bin/openspec validate --all --strict` passed before archive: `15` items.
- `git diff --check` passed before archive.
- `bin/changerail-python scripts/changerail_delivery_manifest.py validate
  .runtime/changerail/delivery-manifests/010-03-fix-publish-finalization-ledger.json
  --json` passed.
- `./bin/openspec validate --all --strict` passed after archive: `14` specs.
- `python3 scripts/public-surface-scan.py` passed: `598` files scanned,
  `0` findings.
- `python3 scripts/run-release-baseline.py` passed: `26/26` steps, including
  contract schema validation, ruff, current/history public-surface scans,
  delivery manifest smokes, generated drift fixture and whitespace check.
- Review cycle 1 returned `no-go` with blocker R1: skipped local-only
  `--no-push` manifest evidence was specified but not enforced or documented.
- R1 fix verification: `python3 scripts/smoke-contract-schemas.py` passed,
  `python3 scripts/smoke-delivery-manifest-derive.py` passed with skipped
  local-only positive/negative fixtures, `python3
  scripts/smoke-delivery-manifest.py` passed, `./bin/openspec validate
  changerail-contracts --strict` passed and `git diff --check` passed.
- R1 final verification: `./bin/openspec validate --all --strict`,
  `python3 scripts/public-surface-scan.py` and
  `python3 scripts/run-release-baseline.py` passed after the rescue; release
  baseline reported `26/26` steps.
- Review cycle 2 existing verdict validated fresh with
  `bin/changerail-review-verdict validate
  .runtime/changerail/reviews/010-03-fix-publish-finalization-ledger.json
  --check-fresh --workspace . --json` and returned `no-go` for blocker R1:
  pushed publish manifests still validated without required ledger fields.
- Cycle 2 R1 rescue verification: `python3 scripts/smoke-contract-schemas.py`
  passed with schema/helper negative coverage for status-only pushed records and
  pushed records missing `pushed_at`; `python3
  scripts/smoke-delivery-manifest-derive.py` passed with validate and
  `publish-update` negative pushed fixtures while keeping skipped/local-only
  positive and negative fixtures passing; `python3
  scripts/smoke-delivery-manifest.py`, `./bin/openspec validate
  changerail-contracts --strict`, `./bin/openspec validate
  changerail-agent-methodology --strict`, `./bin/openspec validate
  changerail-skill-surface --strict`, `./bin/openspec validate --all --strict`,
  `git diff --check`, `python3 scripts/public-surface-scan.py` and
  `python3 scripts/run-release-baseline.py` passed.
- Cycle 2 release baseline reported `26/26` steps, including contract schema
  validation, ruff, current/history public-surface scans, delivery manifest
  smokes, generated drift fixture and whitespace check.
- Test adequacy: the bare-remote smoke asserts tracked card text excludes both
  payload/final commit hashes and stale pending-push wording, manifest
  `payload_commit` differs from `published_commit`, final remote/branch/status
  metadata is recorded, and manifest `card.path`/`card.status` reflect the
  board move. It would fail if the reported regression returned. Separate RED
  output was not retained; the existing helper behavior was confirmed by source
  inspection before the regression smoke was added.
- Cycle 2 test adequacy: the new negative smokes would fail if
  `publish.status: pushed` could validate with only status or without
  `pushed_at`; `publish-update` is also exercised for both incomplete pushed
  forms.

## Archive
- `openspec/changes/archive/2026-08-01-fix-publish-finalization-ledger/`

## Related
- `openspec/board/1.backlog/010-00-core-release-contracts-epic.md`
- `scripts/changerail_delivery_manifest.py`
- `schemas/changerail-delivery-manifest.schema.json`
- `skills/changerail-pub/SKILL.md`
- `openspec/changes/archive/2026-08-01-fix-publish-finalization-ledger/`

## Result
Implemented stable tracked publish finalization and ignored manifest ledger
split. Delivery manifest schema/helper now records distinct `payload_commit`
and `published_commit`, finalization updates ignored manifest `card.path` and
`card.status`, tracked done-card text avoids exact final commit and mutable push
status, and focused local bare-remote smoke covers commit/finalize/amend/push
without stale metadata. Specs synced and OpenSpec change archived; awaiting
fresh independent review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-01T15:07:29Z карточка выделена из двух consumer postmortems.
- 2026-08-01T15:45:00Z карточка переведена в `2.todo` для runner delivery.
- 2026-08-01T18:04:44Z `changerail-ff` создал apply-ready artifacts для
  `fix-publish-finalization-ledger` и перевел карточку в `3.inprogress`.
- 2026-08-01T18:16:39Z `changerail-do` реализовал manifest ledger/finalization
  fix, выполнил focused smokes, public-surface scan и release baseline,
  синхронизировал specs и archived change
  `2026-08-01-fix-publish-finalization-ledger`; карточка оставлена в
  `3.inprogress` для independent review.
- 2026-08-01T18:20:52Z post-archive manifest validation, OpenSpec validation и
  release baseline повторно passed на финальном pre-review payload.
- 2026-08-01T18:36:25Z independent review cycle 1 returned `no-go` for R1;
  scoped rescue enforced/documented skipped local-only publish manifest evidence
  and extended smoke coverage. Requires fresh review cycle 2.
- 2026-08-01T18:40:26Z R1 rescue verification completed: OpenSpec validation,
  public-surface scan and release baseline passed; requesting fresh review
  cycle 2.
- 2026-08-01T19:07:21Z existing fresh review cycle 2 verdict accepted as
  `no-go` for R1; bounded same-card rescue implemented fail-closed pushed
  publish ledger validation and negative smoke coverage.
- 2026-08-01T19:07:21Z cycle 2 R1 rescue verification completed: focused
  smokes, manifest validation, OpenSpec validation, public-surface scan and
  release baseline passed; awaiting external review cycle 3.
- 2026-08-01T19:28:30Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
