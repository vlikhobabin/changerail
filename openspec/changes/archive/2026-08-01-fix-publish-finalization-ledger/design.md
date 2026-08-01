## Context

Publish finalization currently has two conflicting responsibilities:

- the reviewed payload commit is the content that passed review and is ready to
  publish;
- the final amended commit includes deterministic board-card metadata produced
  after that first commit.

The current helper records the exact commit and `push status` in the tracked
done-card. If the card is amended, that exact commit can become stale. If push is
enabled, the tracked card can also retain `pending` even after the remote push
succeeds. The ignored delivery manifest is the right place for exact ledger
metadata because it can be updated after commit and push without invalidating
reviewed payload.

## Goals / Non-Goals

**Goals:**
- Keep tracked final cards stable: final state, completion outcome, and review
  evidence summary, but no self-referential final commit hash and no mutable
  push status.
- Record exact `payload_commit`, `published_commit`, remote, branch, status and
  timestamps in the ignored delivery manifest.
- Ensure `finalize-card` updates manifest `card.path` and `card.status` after a
  board move.
- Prove the sequence with a local bare remote regression smoke.

**Non-Goals:**
- Full publish scope reconciliation; that remains in card `010-04`.
- Remote retry/resume behavior; that remains in card `020-03`.
- Rewriting historical done cards outside the current card-owned payload.

## Decisions

1. Add explicit manifest publish fields instead of overloading `commit`.
   - Rationale: `payload_commit` and `published_commit` represent different git
     points when card finalization amends the payload commit. A legacy `commit`
     alias is ambiguous and encourages stale evidence.
   - Alternative considered: keep `commit` and infer which commit it represents
     from status. This is weaker because consumers would need hidden lifecycle
     knowledge to interpret the same field.

2. Keep exact publication details out of tracked card text.
   - Rationale: tracked cards cannot reliably contain the hash of the commit
     that contains their own finalization edits. They can state the stable
     result and point to ignored manifest evidence.
   - Alternative considered: perform a second amend after push. This still
     changes the final commit after the push and reintroduces stale remote
     metadata unless another push follows.

3. Let `finalize-card` update the ignored manifest card location when available.
   - Rationale: the helper already owns deterministic post-publish card
     metadata, so it is the smallest source of truth for the board path/status
     transition. The manifest update remains ignored runtime state and does not
     affect review freshness.
   - Alternative considered: require every publish orchestrator to call a
     separate derive/update command after board moves. That spreads a mandatory
     invariant across manual steps.

4. Use a local bare remote smoke rather than a live network integration test.
   - Rationale: it proves commit/finalize/amend/push/publish-update semantics
     deterministically without credentials or external service state.
   - Alternative considered: test only helper output strings. That would miss
     the self-invalidating commit sequence and real `git diff --check` defects.

## Risks / Trade-offs

- Existing consumers may still read `publish.commit`.
  -> Keep helper validation tolerant of legacy manifests if needed, but update
  docs and smokes to require `payload_commit` and `published_commit` for new
  publish evidence.

- Card text loses exact commit details.
  -> The exact values remain available from Git history and ignored manifest
  ledger; tracked cards keep stable outcome and verification summaries.

- Finalization helper now mutates ignored manifest state.
  -> The runtime manifest is already excluded from commit scope and review
  freshness fingerprints, and helper validation protects shape.

## Migration Plan

1. Update schema/helper/docs/tests in one reviewed payload.
2. Run focused manifest and publish-finalization smokes, then release baseline.
3. Archive the OpenSpec change and sync requirements.
4. Publish with the new helper behavior so this card itself is finalized without
   stale tracked commit or push status text.

Rollback is a normal git revert of the published payload. Ignored runtime
manifests can remain local evidence and do not require repository migration.

## Open Questions

- none
