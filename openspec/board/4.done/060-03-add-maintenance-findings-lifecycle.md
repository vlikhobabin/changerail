# Добавить lifecycle maintenance findings

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

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
- `add-maintenance-report-and-finding-state`
- `add-maintenance-baseline-and-card-dedup`

## Verify
- `python3 -m py_compile scripts/changerail_repository_knowledge.py scripts/changerail_maintenance.py scripts/smoke-repository-knowledge.py scripts/smoke-contract-schemas.py` — passed.
- `python3 scripts/smoke-contract-schemas.py` — passed,
  `SMOKE_CONTRACT_SCHEMAS_OK (15 schemas)`; covers missing required
  `detectors` rejection for lifecycle reports.
- `python3 scripts/smoke-repository-knowledge.py` — passed,
  `SMOKE_REPOSITORY_KNOWLEDGE_OK`; covers review-fix regressions for blocked
  state writes outside `.runtime/changerail/maintenance/`, active date-only
  waiver normalization, and card bridge rejection for absolute/secret
  report-sourced material, including secret-like `finding.path` values.
- `openspec validate add-maintenance-report-and-finding-state --strict` —
  passed before archive.
- `openspec validate add-maintenance-baseline-and-card-dedup --strict` —
  passed before archive.
- `openspec validate changerail-repository-knowledge --strict` — passed after
  spec sync.
- `openspec validate --all --strict` — passed after spec sync.
- `python3 scripts/public-surface-scan.py` — passed,
  `summary: pass (822 files scanned, 0 findings)`.
- `python3 scripts/public-surface-scan.py --history` — passed,
  `summary: pass (822 files scanned, 0 findings)`.
- `python3 scripts/run-release-baseline.py` — passed all 30 release baseline
  steps.
- `git diff --check` — passed.
- RED evidence is not applicable as a separate first-failing test run because
  this card extends CLI/schema/docs smoke coverage in the existing smoke-test
  harness; the added assertions would fail if lifecycle identity,
  evidence-fingerprint, corrupt-state, baseline preview/write, triage or card
  dedup behavior regressed.

## Archive
- `openspec/changes/archive/2026-08-09-add-maintenance-report-and-finding-state/`
- `openspec/changes/archive/2026-08-09-add-maintenance-baseline-and-card-dedup/`

## Related
- `openspec/board/1.backlog/060-00-repository-knowledge-maintenance-program-epic.md`
- `openspec/board/4.done/060-02-add-deterministic-knowledge-integrity-gate.md`
- `openspec/changes/archive/2026-08-09-add-maintenance-report-and-finding-state/`
- `openspec/changes/archive/2026-08-09-add-maintenance-baseline-and-card-dedup/`
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
- `openspec/changes/archive/2026-08-09-add-maintenance-report-and-finding-state/`

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
- `openspec/changes/archive/2026-08-09-add-maintenance-baseline-and-card-dedup/`

## Result
Implemented, archived, independently reviewed with `go` in review cycle 4 and
finalized through ChangeRail scoped publish; exact payload and published commit
ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- `2026-08-09T12:35:25Z` — story extracted with durable board dedup boundary.
- `2026-08-09T15:40:00Z` — refreshed against delivered `060-02` scan and adapter
  contracts; lifecycle schemas, identity material, explicit writes and durable
  board marker were frozen, and the story moved to `2.todo`.
- `2026-08-09T15:44:16Z` — `$changerail-ff` created apply-ready artifacts for
  `add-maintenance-report-and-finding-state` and
  `add-maintenance-baseline-and-card-dedup`; both changes passed strict
  OpenSpec validation and the story moved to `3.inprogress`.
- `2026-08-09T16:00:33Z` — implemented lifecycle report/state, baseline,
  triage and board-card bridge contracts; schema/repository-knowledge smokes,
  OpenSpec validation and whitespace checks passed; both card-owned changes
  were archived.
- `2026-08-09T16:11:38Z` — public-surface scans and full release baseline
  passed; card is ready for fresh independent review.
- `2026-08-09T16:18:20Z` — fresh independent review cycle 1 returned
  `no-go` with blockers R1/R2/R3 for custom state path scope, unsafe
  report-sourced card material and active date-only waiver normalization.
- `2026-08-09T16:25:48Z` — same-card rescue attempt 1 fixed R1/R2/R3 and added
  focused `smoke-repository-knowledge.py` regression coverage; py_compile,
  schema smoke, repository-knowledge smoke, OpenSpec validation and
  `git diff --check` passed.
- `2026-08-09T16:42:53Z` — post-rescue public-surface scans passed with
  822 files and 0 findings; `scripts/run-release-baseline.py` passed all 30
  steps.
- `2026-08-09T16:55:40Z` — fresh independent review cycle 2 returned
  `no-go` with blocker R1 for secret-like report-sourced `finding.path`
  material reaching generated tracked board cards.
- `2026-08-09T16:58:58Z` — same-card rescue attempt 2 fixed R1 by rejecting
  secret-like `finding.path` before card rendering and added focused smoke
  coverage for the path-only report fixture; py_compile,
  repository-knowledge smoke, public-surface scan and `git diff --check`
  passed.
- `2026-08-09T17:09:51Z` — post-rescue attempt 2 public-surface scans passed
  with 822 files and 0 findings; `scripts/run-release-baseline.py` passed all
  30 steps.
- `2026-08-09T17:25:34Z` — fresh independent review cycle 3 returned
  `no-go` with blocker R1 because `changerail.maintenance-report.v1` defined
  top-level `detectors` but did not require it, despite the card/spec detector
  summary contract.
- `2026-08-09T17:28:11Z` — same-card rescue attempt 3 fixed R1 by requiring
  top-level `detectors` in `schemas/changerail-maintenance-report.schema.json`
  and adding negative schema smoke coverage; py_compile, schema smoke,
  repository-knowledge smoke, focused missing-detectors probe, OpenSpec
  validation, public-surface scan and `git diff --check` passed.
- `2026-08-09T17:38:15Z` — post-rescue attempt 3 public-surface scans passed
  with 822 files and 0 findings; `scripts/run-release-baseline.py` passed all
  30 steps.
- `2026-08-09T17:47:46Z` — fresh independent review cycle 4 returned `go`;
  prior blockers are fixed, including required top-level lifecycle `detectors`.
- 2026-08-09T17:52:11Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
