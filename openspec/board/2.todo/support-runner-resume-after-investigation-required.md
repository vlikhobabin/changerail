# Support runner resume after investigation-required

## Status
2.todo

## Owner
ChangeRail maintainer

## OpenSpec Stage
artifacts

## Series
- none

## Series Index
- none

## Source
- Field validation of a package-runner delivery stopped by deterministic review
  complexity preflight.
- `bin/changerail-delivery-runner`

## Summary
The delivery runner correctly returns `BLOCKED: investigation_required` after
an implementation child retains an unreviewed dirty payload. Current
single-card `resume` accepts only remote publish-target failures, while a fresh
`run` or `run-plan` requires a clean workspace. The operator therefore cannot
resume the retained exact payload through the package runner after publishing
the required investigation and bounded authorization.

Add a fail-closed recovery contract for an `investigation_required` child that
preserves exact payload identity, requires the published reciprocal
authorization chain, and resumes review/publish without treating an unreviewed
checkpoint commit as review evidence.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `yes`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Acceptance
- Runner records enough schema-backed retained-payload identity at the
  `investigation_required` stop to reject unrelated or mutated work on resume.
- An explicit resume path accepts only the prior matching card/workspace/status
  and re-runs deterministic preflight after the investigation and authorization
  sources are clean tracked `HEAD` artifacts.
- Resume preserves the unreviewed payload as a working-tree review target; it
  does not accept a WIP commit, stash name, branch name or prose assertion as a
  substitute for exact fingerprint proof.
- Queue resume can represent the authorized recovery and keeps downstream cards
  blocked until the original or replacement payload is independently reviewed
  and published.
- Stale, missing, over-ceiling, relation-mismatched or payload-drifted recovery
  remains `BLOCKED` with a stable machine reason.
- Focused synthetic smokes cover successful recovery and adversarial dirty,
  stale authorization, wrong card, wrong workspace and fingerprint drift cases.

## Non-Goals
- Automatically authorizing a large payload.
- Relaxing clean-tree requirements for ordinary initial runner launches.
- Reading or publishing raw child logs as recovery proof.

## Change Set
- `record-investigation-required-payload-identity`
- `resume-investigation-required-single-card`
- `support-investigation-required-queue-recovery`

## Verify
- GREEN: `./bin/openspec validate record-investigation-required-payload-identity --strict`
- GREEN: `./bin/openspec validate resume-investigation-required-single-card --strict`
- GREEN: `./bin/openspec validate support-investigation-required-queue-recovery --strict`
- GREEN: `./bin/openspec validate --all --strict` -> 26/26 passed.
- GREEN: `git diff --check`
- GREEN: untracked-file trailing-whitespace scan over `git ls-files --others
  --exclude-standard`
- GREEN: `python3 scripts/public-surface-scan.py` -> 1069 files scanned, 0
  findings.

## Archive
- not started

## Related
- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-contracts/spec.md`
- `openspec/changes/record-investigation-required-payload-identity/`
- `openspec/changes/resume-investigation-required-single-card/`
- `openspec/changes/support-investigation-required-queue-recovery/`

## Result
not started

## Next
- After retrospective lifecycle closure for
  `openspec/board/3.inprogress/fix-npm-integrity-stderr-isolation.md`, run
  `$changerail-do openspec/board/2.todo/support-runner-resume-after-investigation-required.md`.
- Preserve the critical/new-wire review route. If deterministic review preflight
  requires a published investigation authorization for this implementation,
  stop there instead of treating the direct runner resume as a waiver.

## Change 1: `record-investigation-required-payload-identity`

### Why
`investigation_required` currently preserves a dirty working-tree payload for
operator investigation but does not expose enough schema-backed identity for a
later runner resume to prove that the same payload is still present.

### Goal
Extend the delivery-run status contract so the stop records bounded,
machine-verifiable retained-payload identity for the exact card, workspace,
HEAD, tree, diff fingerprint and review target.

### Scope
- Add status/schema fields for an `investigation_required` retained payload.
- Define how identity is captured without embedding raw source, logs or runtime
  evidence in tracked files.
- Keep WIP commits, stash names, branch names and prose assertions outside the
  trusted identity contract.

### Acceptance
- A runner stop caused by deterministic review preflight
  `investigation-required` records schema-valid retained-payload identity.
- Identity includes enough card/workspace/status and fingerprint context to
  reject unrelated, missing or mutated payloads on resume.
- Raw child logs, raw source payload and ignored runtime evidence are not copied
  into tracked card or schema fields.

### Depends On
- none

### Related
- `openspec/changes/record-investigation-required-payload-identity/`

## Change 2: `resume-investigation-required-single-card`

### Why
The existing single-card `resume` path is scoped to remote publish-target
preflight failures and cannot resume an exact retained dirty payload after the
operator publishes the required investigation and authorization sources.

### Goal
Add an explicit fail-closed single-card resume path for prior
`investigation_required` status records that re-runs deterministic preflight
against the retained working-tree payload after the authorization chain is
clean and tracked at `HEAD`.

### Scope
- Accept only the prior matching card, workspace and status path.
- Verify retained-payload fingerprints before launching review/publish resume.
- Require clean tracked investigation and authorization sources at `HEAD`.
- Preserve the dirty working tree as the review target; do not convert an
  unreviewed checkpoint commit into evidence.

### Acceptance
- Matching authorized resume continues to review/publish using the retained
  working-tree payload.
- Wrong card, wrong workspace, stale status, missing authorization, relation
  mismatch, over-ceiling authorization and fingerprint drift fail closed with
  stable machine reasons.
- Fresh deterministic preflight evidence is recorded for the resumed run.

### Depends On
- `record-investigation-required-payload-identity`

### Related
- `openspec/changes/resume-investigation-required-single-card/`

## Change 3: `support-investigation-required-queue-recovery`

### Why
Queue `resume-plan` can represent linked recovery for `NO-GO` and
`fix_budget_exhausted`, but not the authorized continuation of a retained
`investigation_required` child payload.

### Goal
Teach queue status and `resume-plan` to represent authorized
`investigation_required` recovery while keeping downstream cards blocked until
the original retained payload or its explicit replacement is independently
reviewed and published.

### Scope
- Extend aggregate queue status/recovery metadata for retained-payload
  investigation recovery.
- Constrain plan augmentation and source matching for this recovery class.
- Add focused synthetic smokes for successful recovery and adversarial dirty,
  stale authorization, wrong card, wrong workspace and fingerprint drift cases.

### Acceptance
- `resume-plan` accepts only valid same-workspace retained-payload recovery or
  explicit replacement recovery for a prior `investigation_required` child.
- Downstream cards remain blocked until the recovered source is independently
  reviewed and published.
- Synthetic smoke coverage exercises successful and fail-closed recovery paths.

### Depends On
- `record-investigation-required-payload-identity`
- `resume-investigation-required-single-card`

### Related
- `openspec/changes/support-investigation-required-queue-recovery/`

## Triage Decision
- Move to `2.todo`: bounded replacement already delivered, but the original
  inability to continue the exact retained payload through the package runner
  is still unresolved and now has apply-ready OpenSpec artifacts.
- Priority: high. Это единственная открытая карточка, которая уже блокировала
  реальный delivery flow и потребовала ручную recovery-ветку.

## Log
- 2026-08-19T07:17:52Z created after package-runner delivery could not resume a
  retained `investigation_required` payload through either `resume` or a fresh
  clean-tree launch.
- 2026-08-19T14:05:00Z post-delivery triage confirmed the bounded replacement
  succeeded but did not add runner resume support; card remains the first
  implementation candidate after current in-progress closure.
- 2026-08-19T15:17:24Z `$chrl-ff` decomposed the story into retained-payload
  identity, single-card resume and queue recovery changes.
- 2026-08-19T15:24:37Z OpenSpec artifacts completed and per-change strict
  validation passed.
- 2026-08-19T15:25:29Z final all-change validation and whitespace checks
  passed.
- 2026-08-19T15:26:01Z current-tree public-surface scan passed.
