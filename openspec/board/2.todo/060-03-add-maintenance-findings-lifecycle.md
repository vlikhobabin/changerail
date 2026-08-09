# Добавить lifecycle maintenance findings

## Status
2.todo

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`060-repository-knowledge-maintenance`

## Series Index
`03`

## Planning State
deliver-ready; dependency `060-02` published as commit `dd9fb3e`

## Source
- `060-00-repository-knowledge-maintenance-program-epic.md`
- Existing ChangeRail review verdict, review history, evidence and delivery-run
  runtime contract patterns.

## Summary
Опубликовать maintenance report contract, разделить finding identity и evidence,
сохранить bounded runtime history, добавить tracked baseline/waivers и безопасный
preview/upsert bridge в ChangeRail board.

## Delivered Dependency Contract
- `bin/changerail-maintenance scan --json` emits validated
  `changerail.maintenance-scan-report.v1`; invalid detector output is rejected
  before core normalization.
- Each detector result is `changerail.maintenance-detector-result.v1`; a raw
  finding has stable producer fields `id`, `severity`, `code`, `message` and
  optional repository-relative subject/evidence fields.
- Scan exit codes are `0` below threshold, `1` at or above threshold and `2` for
  invalid configuration or an incomplete/invalid report.
- Adapter execution is shell-free, repository-root scoped and timeout bounded.
  Lifecycle processing consumes this public output instead of importing scan
  internals.

## Frozen Implementation Contract
- `changerail.maintenance-report.v1` is a normalized lifecycle report distinct
  from `changerail.maintenance-scan-report.v1`; normalization MUST reject an
  incomplete or schema-invalid source scan.
- Public supporting schemas are versioned independently for lifecycle state,
  baseline/waivers and triage annotations. Existing scan schema ids stay
  unchanged.
- Identity material is canonical JSON over `identity_version`, detector result
  id, finding code/rule and a normalized repository-relative subject. Message,
  evidence, severity, timestamps and absolute workspace root do not participate
  in identity. The public fingerprint form is `sha256:<lowercase-hex>`.
- Evidence fingerprint is canonical JSON over sanitized material evidence and
  changes without changing identity. Unknown absolute paths or secret-like raw
  values fail closed instead of being copied into lifecycle output.
- Runtime state is stored atomically below
  `.runtime/changerail/maintenance/state.json`; reports, previews and retained
  evidence remain below the same ignored root. A corrupt or unsupported state
  version is an error and is not replaced implicitly.
- Lifecycle normalization is read-only by default. Updating durable runtime
  state requires explicit `--write-state`; without restored state, `first_seen`
  is the current observation and no cross-run continuity is claimed.
- `.changerail/maintenance-baseline.yaml` has separate `accepted` and `waivers`
  collections. Acceptance is keyed by identity fingerprint. A waiver also
  requires `owner`, `reason` and an ISO-8601 `expires_at` or `review_after`
  boundary; expired entries do not suppress an open finding.
- `accept-baseline` and `cards` emit schema-valid preview artifacts by default.
  Only explicit `--write` may change their declared tracked target; `triage`
  only validates/normalizes supplied annotations and never invokes an LLM.
- Written cards carry exactly one machine-readable line
  `Maintenance Origin: <sha256 fingerprint>`. Before create/update, the bridge
  scans `1.backlog` through `5.canceled`; the same identity updates the existing
  card evidence summary and never creates another card.
- Card paths, titles and summaries contain only sanitized repository-relative
  metadata. Raw detector output, source snippets and absolute consumer paths
  remain indirect runtime references.

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
  создает или обновляет card с exact `Maintenance Origin: <sha256 fingerprint>`
  marker.
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
- `openspec/board/4.done/060-02-add-deterministic-knowledge-integrity-gate.md`
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
Dependency contract refreshed; accepted for implementation.

## Next
- Run this single card through supervised `$chrl-deliver`; after publication,
  execute the series MVP exit audit before admitting `060-04`.

## Log
- `2026-08-09T12:35:25Z` — story extracted with durable board dedup boundary.
- `2026-08-09T15:40:00Z` — refreshed against delivered `060-02` scan and adapter
  contracts; lifecycle schemas, identity material, explicit writes and durable
  board marker were frozen, and the story moved to `2.todo`.
