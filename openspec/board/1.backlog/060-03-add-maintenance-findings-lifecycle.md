# Добавить lifecycle maintenance findings

## Status
1.backlog

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`060-repository-knowledge-maintenance`

## Series Index
`03`

## Planning State
blocked on stable scan output from `060-02`

## Source
- `060-00-repository-knowledge-maintenance-program-epic.md`
- Existing ChangeRail review verdict, review history, evidence and delivery-run
  runtime contract patterns.

## Summary
Опубликовать maintenance report contract, разделить finding identity и evidence,
сохранить bounded runtime history, добавить tracked baseline/waivers и безопасный
preview/upsert bridge в ChangeRail board.

## Acceptance
- Опубликована schema `changerail.maintenance-report.v1` с run metadata,
  detector summary и normalized findings.
- Finding содержит `fingerprint`, `evidence_fingerprint`, `detector`, `rule`,
  `severity`, `confidence`, `path`, `evidence_refs`, `remediation`, `first_seen`,
  `owner`, `risk_class` и lifecycle `status`.
- Severity vocabulary согласован с ChangeRail integration и включает
  `blocker`, `major`, `minor`, `info`; deterministic findings имеют confidence
  `1.0`, если detector contract не объявляет более слабую семантику.
- Identity fingerprint строится из versioned detector/rule/normalized subject,
  но не из volatile evidence text или timestamp.
- Evidence fingerprint меняется при новом material evidence; повторный scan с
  тем же state сохраняет identity и `first_seen`.
- Runtime state и reports пишутся atomically под
  `.runtime/changerail/maintenance/`; raw evidence остается indirect reference,
  а не inline tracked content.
- Документация явно ограничивает runtime continuity: ephemeral runner должен
  восстановить state, если ему нужна сохранность `first_seen` между runs.
- Schema-backed tracked `.changerail/maintenance-baseline.yaml` различает
  baseline acceptance и waiver; waiver требует owner, reason и expiry/review
  boundary.
- `accept-baseline` работает как preview по умолчанию и меняет только baseline
  file при explicit `--write`.
- `triage` принимает schema-bound agent annotations, но не вызывает LLM.
- Card bridge делает preview в runtime state по умолчанию; explicit write
  создает или обновляет card с `Maintenance Origin` fingerprint marker.
- Перед card write bridge сканирует все board lanes по identity fingerprint и
  не создает duplicate card; новое evidence обновляет origin/evidence summary.
- Tracked card не содержит raw output, absolute consumer paths, credentials или
  unredacted private snippets.

## Depends On
- `060-01-establish-repository-knowledge-contract`
- `060-02-add-deterministic-knowledge-integrity-gate`

## Change Set
- none yet

## Verify
- Valid/invalid report and baseline/waiver schema fixtures.
- Fingerprint identity stability and evidence-change tests.
- Atomic state write and corrupt-state fail-closed tests.
- Same-state and ephemeral-state semantics tests.
- Board dedup across all lanes and evidence update smoke.
- Preview/default no-mutation and explicit-write scope tests.
- Public-safety redaction and path-neutrality fixtures.

## Related
- `openspec/board/1.backlog/060-00-repository-knowledge-maintenance-program-epic.md`
- `openspec/board/1.backlog/060-02-add-deterministic-knowledge-integrity-gate.md`
- `schemas/changerail-review-verdict.schema.json`
- `schemas/changerail-review-cycle-history.schema.json`
- `schemas/changerail-evidence-index.schema.json`

## Change 1: `add-maintenance-report-and-finding-state`

### Why
Scan output needs a stable wire contract and identity model before schedulers,
agents or metrics can consume it safely.

### Goal
Add report schema, identity/evidence fingerprints and atomic ignored state with
explicit continuity limits.

### Acceptance
- Report and finding shapes satisfy the acceptance above.
- State corruption or version mismatch fails closed without overwriting evidence.
- Raw evidence remains under ignored runtime storage.

### Depends On
- `060-02-add-deterministic-knowledge-integrity-gate`

### Related
- `openspec/changes/add-maintenance-report-and-finding-state/`

## Change 2: `add-maintenance-baseline-and-card-dedup`

### Why
Consumers need reviewed suppression and durable duplicate-card prevention that
does not depend only on process-local scheduler state.

### Goal
Add tracked baseline/waiver semantics and explicit preview/write card bridge.

### Acceptance
- Baseline and waiver lifecycle is schema-backed and reviewable in Git.
- Board fingerprint markers prevent duplicate cards across clean clones.
- All default operations remain read-only.

### Depends On
- `add-maintenance-report-and-finding-state`

### Related
- `openspec/changes/add-maintenance-baseline-and-card-dedup/`

## Result
Not started.

## Next
- Refresh after `060-02`; completion of this story closes the series MVP gate.

## Log
- `2026-08-09T12:35:25Z` — story extracted with durable board dedup boundary.
