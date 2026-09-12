---
name: chrl-native-deliver
description: Implement or repair one accepted openspec-v1 card from its pinned stock OpenSpec apply context.
---

# Native OpenSpec delivery

Read the named card, `openspec/config.yaml` and `$CHRL_NATIVE_CONTEXT`, including
its unchanged stock `workflows.apply` instructions. The card
owns high-level acceptance, budget and evidence policy. The linked OpenSpec
change owns proposal, delta specs, design and tasks. Do not duplicate or rewrite
the accepted plan; only task checkbox progress is allowed during implementation.
On the card, only Result/Log may be updated at the stages described below;
Status and board moves belong to the outer runner. Next is frozen, even when
its wording looks like a completed next step. Never edit Next, Scope, Acceptance
or any other accepted section. A rejected plan requires the operator-owned
plan restoration workflow; do not rewrite manifests or accepted receipts.

When `CHRL_RECOVERY_CONTEXT` is set, read that file and its concrete objective
before choosing work, including during `finalize`. Read `CHRL_REPAIR_CONTEXT`
when supplied. Complete the remaining evidence work named there; repeating sync
alone does not repair an observed-proof handoff failure.

For `CHRL_DELIVERY_STAGE=change`, implement only `CHRL_CHANGE_NUMBER`. Honor
`CHRL_CHANGE_NEXT_EVENT`; do not repeat an already started checkpoint. Emit
`change-<N> starting`, complete the group's product work, mark its actual tasks,
record current focused evidence with `chrl evidence`, then emit
`change-<N> complete` and stop. Do not hand off the aggregate card or start the
next group. The runner starts each unfinished group in a fresh CLI session.

For `CHRL_DELIVERY_STAGE=finalize`, every group is complete. Follow the context's
stock `workflows.sync` instructions to semantically merge the delta specs into
canonical specs, preserving unrelated requirements. Write the delta-to-canonical
mapping and any deliberate no-op to a report under this run, then call
`./bin/chrl native-sync <card> --report <current-run>/sync-report.md`.
Do not implement another task group. A sync receipt binds bytes, not semantic
correctness: the independent reviewer assesses that separately.

For `CHRL_DELIVERY_STAGE=repair`, read the supplied repair context and fix only
its findings. Do not replay completed group events; refresh sync while the
change is active if canonical specs or its report changed.

If `CHRL_DELIVERY_STAGE=archive-refresh`, the runner has already received a
provisional GO and executed stock archive after semantic sync. Do not edit product code,
canonical specs, archived artifacts or replay checkpoint events. Read the
archive-finalization repair context, refresh only card Result/Log and evidence
whose payload fingerprint changed because of the archive, then hand off for the
mandatory continuation of the independent review. Re-execute invalidated checks
by default. Only checks explicitly admitted for dependency-based reuse may use
a new reuse receipt after the runner revalidates every declared input, command,
environment and original log. A reuse receipt records no new execution.
Runtime/external mutable state cannot use local-dependency reuse.

For a later `repair` session with archived context, fix the named product or
evidence findings and refresh affected proofs. Do not edit canonical specs or
archived artifacts, rerun sync, or replay group events; those changes need
explicit lifecycle reconciliation. The runner starts a fresh independent
review for a substantive repair within the remaining shared review allowance.

Preserve the `changerail.card-evidence.v1` contract. Record meaningful before/action/
after observations for the assigned implementation-stage conditions and retain
the project's runtime authorization, target binding, preflight and recovery rules. Do not invent
review/final evidence.

After implementation, finish Result/Log edits before running the checks that
will support handoff. `chrl evidence` records a check receipt, not an observed
proof. For each assigned implementation condition, record current
`changerail.card-proof.v1` artifacts with `./bin/chrl proof record <input.json>`
using `tools/changerail/schemas/card-proof.schema.json`. Each test proof keeps
a singleton `method: {kind, target}`; valid records must cover the primary target
and all declared `additional_targets` in the accepted Verify plan. Use relevant
independent tests, including existing common-boundary tests, without a monolithic
wrapper. One genuine receipt may support several conditions through distinct
condition-bound records; do not repeat dispatch merely for a condition number.
Retain current receipts/logs, selected PASSED nodes from `pytest -v`, and meaningful
before/action/after assertions. For assertions in an external helper, anchor the
entry test file in `assertion_support.source`, its hash-bound invocation fragment
in `invocation`, and the authenticated external assertion fragments. The reviewer
checks the actual call path and relevance; the validator does not prove callgraph.
Negative tests must assert the specific rejection and absence of unauthorized
writes. Add missing coverage within the accepted scope; do not relabel a test
proof as inspection to bypass validation. Payload edits after proof recording
require refreshing affected evidence.

Plan/proof extensions require a supporting engine before accepting a new plan.
Do not rewrite accepted Verify or mix new fields with an old frozen engine.
Existing singleton proofs remain compatible with the new reader.

Confirm all assigned conditions have current proof coverage, then call
`./bin/chrl handoff <card>` and stop only when it exits zero. Report a failed
handoff accurately, but fix routine missing-proof, formatting or staleness errors
within the authorized scope and retry. Stop for an actual unresolved scope,
authority, safety or infrastructure blocker; do not claim successful handoff or
overall delivery completion after a rejection. Never invoke review,
final verification, publication, commit or push: the outer runner owns them.

Timing targets are advisory. Continue accepted in-scope work past a target
without weakening tests or skipping stages. Stop only for a concrete scope,
authority, evidence, safety or infrastructure blocker.

At most two independent review cycles cover the whole run and its ordinary
continuations. Repair after NO-GO or a failed final floor consumes the same
remaining allowance. No terminal or post-floor exception grants another cycle.
