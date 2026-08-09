# Подключить feedback и quality rollup

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`060-repository-knowledge-maintenance`

## Series Index
`05`

## Planning State
deliver-ready; lifecycle and operational dependencies are published, real
review/run evidence exists, and the missing optional `050` instruction-budget
producer is explicitly non-blocking

## Source
- `060-00-repository-knowledge-maintenance-program-epic.md`
- Existing `changerail.delivery-run.v1` and
  `changerail.review-cycle-history.v1` runtime contracts.
- Existing `changerail-delivery-metrics` structured observability approach.

## Delivered Dependency Contract
- `060-03` is published as commit `275621b`. Schema-valid scan results are
  normalized into `changerail.maintenance-report.v1`; ignored state preserves
  finding identity/evidence continuity, and board dedup uses
  `Maintenance Origin: <sha256 fingerprint>` across every lane.
- `060-04` is published as commit `1726eb6`. Read-only scan and bounded triage
  runs write `changerail.maintenance-run.v1` status and artifact references
  below `.runtime/changerail/maintenance/runs/<run-id>/`.
- Existing delivery runs use `changerail.delivery-run.v1` under
  `.runtime/changerail/delivery-runs/<run-id>/status.json`; review histories use
  `changerail.review-cycle-history.v1` under
  `.runtime/changerail/reviews/<card-id>.history.json`.
- Real series evidence includes multi-cycle `no-go -> go` review history for
  `060-03` and delivered run/review evidence for `060-04`. Fixtures still own
  malformed, legacy and blocked-run boundary cases.
- The generic detector adapter already requires argv-array execution without a
  shell and one schema-valid `changerail.maintenance-detector-result.v1` object
  on stdout.

## Frozen Implementation Contract
- Extend the existing cross-platform `bin/changerail-maintenance` surface with
  `feedback` and `quality` subcommands. Do not add a competing standalone
  helper or modify columns of `bin/changerail-delivery-metrics`.
- `feedback` accepts explicit repository-relative review-history and
  delivery-run record paths and emits one
  `changerail.maintenance-detector-result.v1` for a declared adapter id. It
  validates each input against the existing frozen schema before normalization.
- Review normalization preserves the source record reference, review cycle,
  original finding id, severity and safe affected relative paths. Finding
  detail/prose and raw file content are not copied into normalized evidence;
  stable subject identity includes the original finding id so unrelated review
  findings cannot collapse onto one fingerprint.
- Delivery normalization creates a finding only for a schema-valid terminal
  record whose `result` and `terminal_outcome` are `BLOCKED` and whose
  structured `terminal_reason` is present. Logs, stderr and human diagnostics
  are never parsed for control flow or finding text.
- Malformed, unsafe, legacy prose-only or semantically incomplete inputs produce
  schema-bound `unsupported_*`/validation diagnostics, not inferred findings.
  Mixed input cannot silently discard an invalid record while claiming a
  complete pass.
- Consumer/external producers continue to use the generic detector adapter
  protocol from `060-02`; ChangeRail core does not own consumer-specific
  retrospective logic or external mutation.
- `quality` reads explicit schema-valid lifecycle reports, state, triage and
  optional proposal-decision records and emits human-readable, JSON and stable
  CSV views. JSON uses new schema id
  `changerail.maintenance-quality-rollup.v1`; proposal decisions use a separate
  public `changerail.maintenance-proposal-decision.v1` input contract and remain
  ignored runtime evidence.
- Proposal-decision records live below
  `.runtime/changerail/maintenance/proposals/<proposal-id>.json` and identify the
  proposal, finding fingerprint, transformation class, `accepted`/`rejected`
  decision, decision timestamp and safe evidence references. They are quality
  observations only and do not authorize or perform a fix.
- Latest complete report supplies open/accepted/waived counts. A finding is
  counted as resolved only when it exists in an earlier complete ordered
  snapshot and is absent from the later complete snapshot; insufficient or
  incomplete history yields `unknown`, never an inferred zero.
- Catalog coverage is calculated against the validated tracked catalog.
  Stale/generated findings come from stable detector/rule ids. Board dedup
  metrics inspect fingerprint markers and report represented, missing and
  conflicting identities without creating or updating cards.
- Time-to-triage is derived only when a schema-valid triage annotation can be
  matched to a finding fingerprint and timestamp. Accepted/rejected proposal
  counts require schema-valid proposal-decision records. Missing optional inputs
  render as `unknown` in text, JSON and CSV.
- Stable CSV is a sorted long-form table with columns
  `metric,value,unit,status`; it does not append fields to the existing delivery
  metrics CSV. Text and JSON expose the same metric ids and unknown status.
- Card `050` remains the sole owner of the instruction-budget threshold,
  remediation and producer schema. Until that producer is published, the
  dogfood rollup reports instruction bytes as `unknown`; this card must not
  invent a temporary threshold or producer.
- ChangeRail dogfood enables every applicable built-in deterministic detector
  over an explicit canonical knowledge scope and extends the tracked catalog as
  needed. Feedback/runtime-dependent adapters are exercised by fixtures and are
  not made a default CI dependency on pre-existing ignored history.
- Broken link/anchor, orphan/catalog coverage, stale generated index, optional
  instruction-producer import and contradiction annotation have public-safe
  fixtures. Semantic contradiction remains an agent annotation with retained
  evidence and never becomes a deterministic failure from one model verdict.
- All commands are read-only by default. Feedback and quality do not create
  cards, write baseline/state, commit, push, comment, open PRs or mutate
  external systems.

## Summary
Нормализовать feedback из review/blocked delivery и external producers в
maintenance findings, добавить quality rollup и полное ChangeRail dogfooding без
парсинга свободного текста или централизованной mutation consumer repositories.

## Acceptance
- Feedback adapters читают schema-valid review-cycle history и delivery-run
  records; arbitrary log/prose scraping не является supported input.
- Review finding сохраняет source record reference, original finding id,
  severity и affected relative paths без изменения frozen review schema ids.
- Blocked-run adapter использует structured terminal outcome/reason/evidence;
  неизвестный или legacy prose-only blocker классифицируется как unsupported,
  а не как доказанная maintenance finding.
- External producer protocol принимает schema-bound findings через detector
  adapter boundary из `060-02`; consumer-specific retrospective остается у
  consumer.
- Feedback normalization использует те же identity/evidence fingerprint rules
  и board dedup contract, что deterministic scan.
- Quality rollup читает structured maintenance reports/state и показывает как
  минимум catalog coverage, open/resolved/accepted/waived findings, stale/generated
  findings, duplicate-card prevention, instruction bytes when available,
  time-to-triage и accepted/rejected fix proposals.
- Missing optional metrics выводятся как `unknown`, а не как zero.
- Rollup поддерживает human-readable, JSON и stable CSV output без изменения
  existing delivery metrics columns.
- ChangeRail dogfood catalog покрывает canonical docs и fixtures для broken
  link/anchor, stale generated index, optional schema-bound instruction producer
  import и canonical source contradiction annotation.
- Semantic contradiction остается agent annotation with retained evidence;
  один LLM verdict не превращается в deterministic gate.
- Никакой feedback adapter по умолчанию не создает card, commit, comment, PR или
  external mutation.
- Existing review, delivery, evidence and delivery-metrics schema ids/columns
  remain unchanged.

## Depends On
- `060-03-add-maintenance-findings-lifecycle`
- `060-04-add-maintain-skill-and-scheduler-adapters`
- Card `050` only for future instruction-budget values; its currently missing
  producer is optional and does not block delivery of this card.

## Change Set
- `connect-maintenance-feedback-adapters`
- `add-maintenance-quality-rollup`
- `complete-maintenance-dogfood`

## Verify
- Review history and blocked-run positive/negative fixtures.
- Legacy/malformed record fail-closed tests without prose parsing.
- External producer fingerprint/dedup integration smoke.
- Rollup text/JSON/CSV golden fixtures with unknown optional values.
- Complete/incomplete snapshot resolution and triage/proposal timing fixtures.
- ChangeRail dogfood scan and contradiction triage fixture.
- `python3 scripts/smoke-contract-schemas.py`
- `python3 scripts/smoke-repository-knowledge.py`
- Public-surface current/history scans and full release baseline.

## Related
- `openspec/board/1.backlog/060-00-repository-knowledge-maintenance-program-epic.md`
- `openspec/board/4.done/060-03-add-maintenance-findings-lifecycle.md`
- `openspec/board/4.done/060-04-add-maintain-skill-and-scheduler-adapters.md`
- `openspec/changes/archive/2026-08-09-connect-maintenance-feedback-adapters/`
- `openspec/changes/archive/2026-08-09-add-maintenance-quality-rollup/`
- `openspec/changes/archive/2026-08-09-complete-maintenance-dogfood/`
- `openspec/specs/changerail-delivery-observability/spec.md`
- `openspec/specs/changerail-repository-knowledge/spec.md`
- `bin/changerail-delivery-metrics`

## Change 1: `connect-maintenance-feedback-adapters`

### Why
Review and blocked-run evidence already identifies harness weaknesses, but it
cannot enter maintenance backlog reliably without structured normalization.

### Goal
Add schema-backed review, blocked-run and external producer adapters using the
common finding lifecycle.

### Scope
- Add `bin/changerail-maintenance feedback` and its schema validation,
  normalization and public documentation.
- Reuse the existing detector-result adapter boundary and lifecycle identity;
  do not change frozen review or delivery schemas.

### Acceptance
- Adapters satisfy the structured-input and compatibility rules above.
- Existing schema ids remain unchanged.
- Duplicate findings/cards are prevented by common identity fingerprints.

### Depends On
- `060-03-add-maintenance-findings-lifecycle`

### Related
- `openspec/changes/archive/2026-08-09-connect-maintenance-feedback-adapters/`

## Change 2: `add-maintenance-quality-rollup`

### Why
Maintainers need trend evidence before deciding whether broader automation or
fix mode is justified.

### Goal
Add schema-backed proposal evidence and stable maintenance quality text, JSON
and CSV outputs without altering delivery metrics.

### Scope
- Add `changerail.maintenance-quality-rollup.v1` and
  `changerail.maintenance-proposal-decision.v1` schemas.
- Add `bin/changerail-maintenance quality` with complete-snapshot,
  optional/unknown and board-marker semantics frozen above.

### Acceptance
- Rollup satisfies the metrics and snapshot semantics above.
- Optional data remains `unknown` when not observed.
- Existing delivery metrics output and columns remain unchanged.

### Depends On
- `connect-maintenance-feedback-adapters`
- `060-04-add-maintain-skill-and-scheduler-adapters`

### Related
- `openspec/changes/archive/2026-08-09-add-maintenance-quality-rollup/`

## Change 3: `complete-maintenance-dogfood`

### Why
The current tracked ChangeRail policy is a valid minimal skeleton with no
enabled detectors, so it proves wiring but not the full read-only harness.

### Goal
Enable applicable deterministic detectors for ChangeRail's canonical knowledge
scope and retain public-safe regression fixtures for deterministic and agent
annotation boundaries.

### Scope
- Extend `.changerail/knowledge.yaml`, `.changerail/maintenance.yaml` and the
  generated index for the accepted dogfood scope.
- Add or update regression fixtures without depending on ignored local history
  in default CI.

### Acceptance
- Root `scan`/`report` executes non-zero detector coverage and passes on the
  clean repository without tracked mutation.
- Broken deterministic fixtures fail with stable codes; contradiction remains
  annotation-only; instruction metrics remain `unknown` until `050` publishes a
  producer.
- Dogfood runtime output remains ignored and public-safe.

### Depends On
- `connect-maintenance-feedback-adapters`
- `add-maintenance-quality-rollup`
- `060-04-add-maintain-skill-and-scheduler-adapters`

### Related
- `openspec/changes/archive/2026-08-09-complete-maintenance-dogfood/`

## Result
Implemented feedback normalization, quality rollup contracts/CLI and root
repository-knowledge dogfood scanning. Synced main specs and archived all three
card-owned OpenSpec changes.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Verification
- passed: `./bin/openspec validate connect-maintenance-feedback-adapters --strict`
- passed: `./bin/openspec validate add-maintenance-quality-rollup --strict`
- passed: `./bin/openspec validate complete-maintenance-dogfood --strict`
- passed: `./bin/openspec validate --all --strict` after archive (23/23)
- passed: `python3 scripts/smoke-contract-schemas.py` (18 schemas)
- passed: `python3 scripts/smoke-repository-knowledge.py`
- passed: `bin/changerail-maintenance validate-catalog`
- passed: `bin/changerail-maintenance render-index --check`
- passed: `bin/changerail-maintenance scan --json` (5 detectors, 0 findings)
- passed: `python3 scripts/public-surface-scan.py` (869 files, 0 findings)
- passed: `python3 scripts/public-surface-scan.py --history` (869 files, 0 findings)
- passed: `python3 scripts/run-release-baseline.py` (31/31)
- passed: `git diff --check`
- passed: `bin/changerail-python scripts/changerail_delivery_manifest.py validate .runtime/changerail/delivery-manifests/060-05-connect-feedback-and-quality-rollup.json --json`
- passed: `bin/changerail-python scripts/changerail_delivery_manifest.py scope-check .runtime/changerail/delivery-manifests/060-05-connect-feedback-and-quality-rollup.json --target working-tree --json`

## Archive
- `openspec/changes/archive/2026-08-09-connect-maintenance-feedback-adapters/`
- `openspec/changes/archive/2026-08-09-add-maintenance-quality-rollup/`
- `openspec/changes/archive/2026-08-09-complete-maintenance-dogfood/`

## Next
- done

## Log
- `2026-08-09T12:35:25Z` — feedback/rollup story extracted from broad harness card.
- `2026-08-09T19:40:00Z` — refreshed after published `060-04`; feedback input,
  rollup snapshot/proposal semantics, full dogfood boundary and non-blocking
  `050` optional metric were frozen, and the story moved to `2.todo`.
- `2026-08-09T19:53:27Z` — fast-forward created apply-ready artifacts for
  `connect-maintenance-feedback-adapters`, `add-maintenance-quality-rollup` and
  `complete-maintenance-dogfood`; story moved to `3.inprogress`.
- `2026-08-09T20:17:15Z` — implementation finished, main spec synced, all three
  card-owned changes archived, and delivery-level verification passed.
- `2026-08-09T20:27:55Z` — fresh independent review cycle 1 returned `no-go`
  with blockers R1 for review-feedback lifecycle identity collapse and R2 for
  missing completed full release-baseline evidence.
- `2026-08-09T20:32:23Z` — same-card rescue attempt 1 fixed R1 by promoting
  review `original_finding_id` into lifecycle subject identity and added
  same-path feedback fingerprint smoke coverage; R2 was addressed by retaining
  full release-baseline evidence for the final payload.
- 2026-08-09T20:53:18Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
