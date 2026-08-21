## Context

Текущий `resume` валидирует либо recoverable remote preflight failure, либо
специальный retained-payload path `investigation_required`. Только второй путь
разрешает exact dirty working tree и только после published investigation
authorization. Queue recovery mirror ту же special reason. Child, корректно
остановившийся из-за недоступной required external platform, license,
credential или service, может оставить такой же полезный unreviewed payload,
но free-text reason не имеет authority ослабить clean-tree preflight.

Новый путь должен переиспользовать canonical review fingerprinting и ignored
evidence. Он не должен превращать каждый result `BLOCKED` в retryable dirty
resume.

## Goals / Non-Goals

**Goals:**

- Model a small generic taxonomy of temporary external blockers.
- Bind blocker, retained payload and required recovery evidence to one prior
  run/card/workspace.
- Preserve the exact declared execution target when the project has one.
- Resume only the exact payload after fresh schema-valid evidence.
- Give `resume-plan` parity with single-card resume and preserve queue order.
- Preserve the existing investigation authorization branch unchanged.

**Non-Goals:**

- Не принимать project-specific reason strings или boolean bypass.
- Не хранить credentials, entered values, screenshots или response bodies.
- Не считать восстановленную внешнюю доступность proof of business acceptance.
- Не возобновлять permanent policy, scope, review or implementation defects.
- Не считать blocker/recovery authority разрешением создать, клонировать,
  восстановить, переподключить или подменить execution target.

## Decisions

1. **External blocker is a separate bounded object.** Optional
   `external_blocker` uses `schema: changerail.external-blocker.v1`, run-local
   `blocker_id`, enum class (`credential`, `network`, `license`,
   `external_service`, `platform_access`, `required_software`), `observed_at`,
   `retryable: true` and a resume-evidence policy. The existing
   `terminal_reason` stays a stable machine value such as
   `recoverable_external_blocker`; class-specific prose is not authoritative.

2. **Only an authoritative structured terminal event can declare the object.**
   Runner validates the event and captures canonical retained identity at the
   stop. Agent prose and stderr cannot authorize dirty resume. Identity capture
   failure keeps `BLOCKED` but makes the status non-resumable.

3. **Evidence is an ignored index reference, not embedded output.** Resume
   accepts an explicit `changerail.evidence-index.v1` path. The blocker policy
   declares required evidence ids and bounded maximum age. Runner verifies
   schema, card/source-run scope, required entries, `status: passed`, timestamps
   newer than the blocker and redaction/runtime-storage policy. It does not
   reinterpret command output. Alternative of rerunning arbitrary stored argv
   was rejected because it would expand mutation/credential authority.

4. **Dirty authorization remains exact and narrow.** Current workspace root,
   card id/path, source status path, `HEAD`, tree SHA and diff fingerprint must
   equal retained identity. Ignored evidence files do not change the
   fingerprint. Any tracked/untracked payload drift fails before Codex launch.
   `investigation_required` continues through its published authorization
   branch and cannot satisfy this path with external evidence.

5. **Resume starts the existing lifecycle with explicit context.** Child gets
   value-free resume metadata (source run, blocker id/class and evidence-index
   reference) through the runner-owned prompt/environment contract. Lifecycle
   still performs its project-declared verification and review/publish gates;
   resume evidence proves only that the external condition may be retried.

6. **Queue resumes original card in place.** Aggregate card status retains a
   bounded recovery object referring to source run/status/fingerprint/blocker.
   `resume-plan` validates the same evidence, launches that card first, skips
   already delivered cards and releases dependencies only after normal
   successful publish. Duplicate or cross-workspace recovery fails closed.

7. **Declared target identity is immutable across retained resume.** If the
   source project declares an execution target, retained identity also freezes
   its logical id and sanitized fingerprint. Resume requires the current
   declaration and every target-bearing recovery evidence entry to match.
   Missing/mismatched/multiple targets fail before child launch. An explicit
   operator rebind starts a new clean attempt and invalidates prior runtime
   evidence; it cannot reuse this dirty-resume branch.

## Risks / Trade-offs

- [Passed evidence does not guarantee service stays available] -> child reruns
  the mandatory gate; repeat blocker remains a new `BLOCKED` attempt.
- [Taxonomy misses a real blocker] -> unknown classes remain nonrecoverable
  until contract review adds a generic class.
- [Evidence index is edited] -> schema, scope, ids, timestamps and current file
  state are revalidated at resume.
- [Dirty resume expands attack surface] -> exact fingerprint and explicit prior
  status are mandatory before child launch.
- [Recovered service points to another target] -> compare declared and observed
  target identities and reject drift before child launch.

## Migration Plan

1. Extend schemas with optional external blocker/evidence/recovery metadata.
2. Add authoritative stop capture and single-card validation.
3. Add queue retained recovery parity and stable failure reasons.
4. Add adversarial fixtures and operator docs.
5. Rollback removes the new optional branch; old remote and investigation
   resume paths remain valid.

## Open Questions

- none
