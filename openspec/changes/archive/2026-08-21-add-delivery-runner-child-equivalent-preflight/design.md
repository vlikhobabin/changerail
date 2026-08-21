## Context

Existing remote publish-target preflight classifies sanitized Git/SSH failures
in `changerail.delivery-run.v1` status. Delivery-plan `preflight-plan` and
initial `run-plan` already launch each single-card runner in `preflight` mode
and preserve `run_status_path` plus `failure_class` in
`changerail.delivery-plan-status.v1`.

The published investigation narrowed the remaining product gap:

- aggregate admission must treat the single-card preflight receipt as the
  child-equivalent publish-target proof and expose a specific terminal reason;
- serial `run-plan` / `resume-plan` dispatch must revalidate the later card
  immediately before the workspace lock and delivery child launch;
- single-card fallback must preserve a real child publish-target blocker
  instead of collapsing it to `unpublished_card`.

The implementation must stay inside the no-new-protocol boundary by reusing
existing status fields.

## Goals / Non-Goals

**Goals:**

- Reuse the single-card runner `preflight --write-status` command as the
  child-equivalent receipt.
- Stop aggregate admission before workspace locks or delivery children when
  that receipt fails.
- Re-run the same receipt check at dispatch time for unresolved non-skipped
  cards.
- Preserve `failure_class`, retryability and attempt count in the child status
  and the aggregate `run_status_path` reference.
- Map child publish-target preflight failure to
  `terminal_reason: publish_target_preflight_failed`.
- Preserve explicit `--no-push` behavior.

**Non-Goals:**

- No required schema fields or new status schema version.
- No SSH config override feature in this change.
- No generic SSH bypass such as `ssh -F /dev/null`.
- No resumption of the current external consumer batch queue.

## Decisions

1. **Use the existing single-card `preflight` command as the receipt.**
   The plan runner already invokes the configured launcher with the target
   workspace, runtime root, run id and `--deliver-arg=--no-push` when selected.
   Extending that path keeps the receipt child-equivalent without adding a
   second runner protocol. The child status remains the source of detailed
   publish-target evidence.

2. **Return a typed plan terminal reason from child preflight failure.**
   When `first_failed_child_check` sees a failed `publish target` check, the
   aggregate card status records `terminal_reason:
   publish_target_preflight_failed`. The aggregate run remains `BLOCKED`, and
   the card keeps `run_status_path` plus sanitized `failure_class`.

3. **Revalidate at dispatch time before lock creation.**
   `run_queue` performs admission preflight once before entering the queue
   loop. The dispatch loop must call the same child preflight helper for the
   selected candidate immediately before `create_workspace_lock`. If it fails,
   the candidate is blocked, the plan terminal result is `BLOCKED`, and no
   workspace lock or delivery child is created.

4. **Keep pass receipts bounded by behavior instead of new schema state.**
   This change does not store a new receipt timestamp/freshness field. It
   obtains fresh evidence at admission and again at every dispatch point. That
   satisfies the investigation's bounded-freshness intent while staying inside
   existing status fields.

5. **Do not change retry taxonomy.**
   Retryability and attempts remain owned by single-card publish-target
   preflight. Aggregate status references the child status and copies only the
   already-supported failure class.

## Risks / Trade-offs

- [Risk] Dispatch-time preflight adds another child process per delivered card.
  Mitigation: the command is mutation-free and bounded, and the card explicitly
  prioritizes early fail-closed behavior over launch latency.
- [Risk] The aggregate status does not inline retryability and attempts.
  Mitigation: `run_status_path` points to the child `changerail.delivery-run.v1`
  status where those existing fields already live.
- [Risk] A custom launcher may not support `preflight --write-status`.
  Mitigation: the existing admission preflight already depends on that contract;
  failures remain fail-closed and produce a blocked aggregate status.

## Migration Plan

1. Add focused smoke fixtures for admission failure before lock/launch,
   dispatch-time drift failure and no-push pass behavior.
2. Implement the shared helper changes in `bin/changerail-delivery-runner`.
3. Update durable runner docs/specs and run the focused smoke plus release
   baseline.

Rollback is a normal scoped revert of the runner/docs/spec/test payload before
consumer lock updates.

## Open Questions

- none
