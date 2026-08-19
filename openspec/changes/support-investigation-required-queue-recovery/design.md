## Context

Queue `resume-plan` currently preserves fail-fast behavior and supports a
constrained `recovery_for` augmentation after child `NO-GO` or
`fix_budget_exhausted`. A child that stops at `investigation_required` is
different: the unsafe payload may still exist as an exact retained working tree
and can become reviewable only after a published investigation/authorization
chain exists.

This change depends on the retained identity and single-card resume changes.
The queue must consume their status fields instead of reconstructing payload
identity from logs or prose.

## Goals / Non-Goals

**Goals:**

- Let `resume-plan` recognize prior child `investigation_required` as a
  recoverable but fail-closed queue state.
- Preserve downstream dependency blocking until original retained-payload resume
  or an explicit replacement recovery publishes successfully.
- Record enough aggregate status metadata for operators to see which prior
  status and retained identity are being recovered.
- Cover successful and adversarial recovery paths with focused smokes.

**Non-Goals:**

- No automatic investigation or authorization authoring.
- No downstream launch before a recovered source satisfies normal queue success
  criteria.
- No raw child log parsing as recovery proof.

## Decisions

1. Treat `investigation_required` as a recoverable source only when the prior
   child status is schema-valid and contains retained-payload identity. This
   mirrors single-card resume and prevents queue resume from trusting a process
   exit code or free-text log.

2. Support two explicit recovery forms. The preferred form resumes the original
   card by launching single-card `resume --status-path <prior-child-status>`
   when the plan fingerprint is otherwise unchanged. The replacement form uses
   an added same-workspace, same-wave `recovery_for` card when the original
   retained payload cannot be safely continued.

3. Extend aggregate status with bounded recovery metadata such as
   `recovery_kind`, `source_run_status_path` and retained-payload fingerprint
   summary. The aggregate status references child status paths instead of
   inlining raw child logs.

4. Keep dependency semantics unchanged. A source in recovery does not satisfy
   downstream dependencies until it is `DELIVERED` or marked `recovered` by a
   successfully published recovery child.

## Risks / Trade-offs

- [Risk] Queue augmentation logic can become permissive. Mitigation: require
  same workspace, same wave, inherited dependencies and exact source status
  matching for any added recovery card.
- [Risk] Original retained-payload resume and replacement recovery could both
  be attempted. Mitigation: allow one active recovery path per source and fail
  closed on duplicates.
- [Risk] Aggregate status may expose too much runtime detail. Mitigation:
  include only bounded metadata and child status references.

## Migration Plan

- Update `resume-plan` recoverable-source classification for
  `investigation_required`.
- Extend `schemas/changerail-delivery-plan-status.schema.json` for bounded
  retained recovery metadata.
- Add focused queue smokes for successful retained recovery and fail-closed
  adversarial cases.

## Open Questions

- none
