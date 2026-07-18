## Context

The single-card runner currently derives `DELIVERED` from child exit code `0`
when stdout has no authoritative terminal event. That fallback can misclassify
a successful agent process which deliberately stopped before publish after
exhausting `changerail-do` fix cycles. Queue status then sees a successful child
and may rely on repository checks that do not preserve the original reason.

Queue plans are fingerprinted and `resume-plan` currently rejects every plan
change. This protects against silent mutation but leaves no safe mechanism to
add the linked recovery card already required by the public queue spec.

## Goals / Non-Goals

**Goals:**

- Preserve a machine-readable terminal reason from agent handoff through the
  single-card and aggregate status records.
- Fail closed for unstructured exit `0` when the requested card is not
  published.
- Allow only a constrained recovery augmentation of a failed aggregate plan.
- Run recovery before dependants and satisfy the failed source dependency only
  after recovery publishes through the normal reviewed delivery pipeline.

**Non-Goals:**

- No parsing of arbitrary prose or recursive JSON values.
- No automatic invention of recovery scope by the runner.
- No bypass of `changerail-deliver`, independent review or publish gates.
- No general mutable-plan resume; unrelated fingerprint drift still blocks.

## Decisions

1. **Terminal signal is outcome plus optional reason.**
   `changerail.delivery-run.v1` gains backward-compatible optional
   `terminal_reason` matching a stable identifier pattern. The runner reads
   authoritative top-level JSONL outcome fields as before and additionally
   accepts exact `terminal_outcome:` / `terminal_reason:` lines only from a
   completed Codex `agent_message` event. Last authoritative signal wins.

2. **Unpublished unstructured success fails closed.**
   Without an authoritative signal or canonical review fallback, exit `0`
   yields `DELIVERED` only when the card resolves uniquely under
   `openspec/board/4.done/`. Otherwise status is `BLOCKED` with
   `terminal_reason: unpublished_card`. Non-terminal tool error strings remain
   irrelevant; a real success fixture emits an authoritative delivered signal
   or has a published card.

3. **Queue trusts child status, not child exit code.**
   Missing or invalid child status becomes `BLOCKED` with
   `missing_or_invalid_child_status`. A valid child's `terminal_reason` is
   copied into aggregate card status and human-readable reason text.

4. **Recovery plan augmentation is explicit and narrow.**
   A plan card may declare optional `recovery_for: <source-card-id>`. It must be
   in the same workspace and wave as its source, inherit the source's declared
   dependencies, and be unique for that source. On resume, fingerprint drift is
   accepted only when all previously known cards keep identity, workspace,
   card reference, wave and dependencies, while every added card is a valid
   recovery for a prior `NO-GO` source or a `BLOCKED` source whose
   `terminal_reason` is `fix_budget_exhausted`.

5. **Recovery satisfies source dependencies only after reviewed delivery.**
   On resume the failed source is not re-run. Its recovery card becomes ready;
   dependants remain blocked because the source id is absent from the completed
   set. When recovery child returns `DELIVERED` and normal queue success checks
   prove its reviewed publish result, aggregate status marks the source
   `recovered`, records `recovered_by`, adds the source id to completed, and
   only then schedules downstream cards. A failed recovery remains fail-fast.

6. **Published recovery is evidence of the review gate.**
   The queue continues to invoke the existing single-card `changerail-deliver`
   path. In push mode, unique done-card location, clean repository and upstream
   equality prove that publish completed; in no-push mode the existing committed
   ahead-state check applies. The runner does not try to revalidate a verdict
   fingerprint after publish, because the publish commit necessarily changes
   HEAD after the fresh pre-publish verdict was checked.

## Risks / Trade-offs

- [Риск] Controlled fingerprint exception could admit unrelated plan drift. →
  Compare every previous card's stable identity, workspace, card reference,
  wave and dependencies; require every new card to be a valid recovery link.
- [Риск] A recovery card could run beside unrelated work in the same wave. →
  Workspace serialization and dependencies remain enforced; only downstream
  cards depending on the failed source are strictly held behind recovery.
- [Риск] Marking source `recovered` hides its original failure. → Preserve its
  original result/reason and add `recovered_by`; history remains in prior
  aggregate and child status records.
- [Риск] Existing records lack new optional fields. → Keep schema ids at v1 and
  make all recovery/reason fields optional.

## Migration Plan

Add optional schema fields, update parser/queue behavior and focused smoke
fixtures. Existing plans without `recovery_for` and existing statuses without
`terminal_reason` remain valid. Unrelated plan fingerprint changes continue to
fail closed. Rollback consists of removing the optional behavior; no tracked
runtime migration is required.

## Open Questions

Нет. General plan editing and multi-hop recovery graphs remain future work; one
recovery per failed source is the bounded v1 behavior.
