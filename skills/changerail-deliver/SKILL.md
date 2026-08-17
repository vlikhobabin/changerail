---
name: changerail-deliver
description: "Run the complete ChangeRail card pipeline in one supervised foreground workflow: ff, do, independent review gate and publish."
---

# ChangeRail Deliver

## Purpose

Orchestrate the standard ChangeRail card pipeline:

```text
$changerail-ff <card-path>      # plan/decompose and create apply-ready artifacts
$changerail-do <card-path>      # implement, verify, sync specs and archive
$changerail-review <card-path>  # independent fresh-context verdict
$changerail-pub <card-path>     # scoped commit and push
```

This skill is an orchestration layer. Before executing each phase, read and
follow the effective `changerail-ff`, `changerail-do`, `changerail-review` or `changerail-pub`
contract from the active workspace.

For normal operator handoff, a deliver-ready card is an accepted board card
with scoped ownership, observable acceptance, ordered change sections and known
gates. It may still lack OpenSpec artifacts; `changerail-deliver` starts with
`ff` and creates or completes those artifacts before `do`.

## Project Context

Resolve the repository root from the current working directory or
`CODEX_WORKDIR`. Read:

1. `openspec/config.yaml` if present.
2. `AGENTS.md`, `AGENTS.shared.md`, board docs and local workflow docs that
   affect scope, verification, board moves, commits, pushes or repo boundaries.
3. The target card, board column or ordered card list.
4. Phase skill contracts from the current workspace.

## Inputs

Expected forms:

```text
$changerail-deliver <card-path>
$changerail-deliver <board-column>
$changerail-deliver <card-path> --no-push
```

Useful flags:

```text
$changerail-deliver <path> --from change-slug
$changerail-deliver <path> --until change-slug
$changerail-deliver <path> --max-cards 3
$changerail-deliver <path> --no-push
$changerail-deliver <path> --max-fix-cycles 5
$changerail-deliver <path> --no-review
$changerail-deliver <path> --max-review-cycles 2
```

Accept legacy prompt forms such as `/changerail:deliver`, `changerail:deliver`,
`$changerail-delivery`, `/changerail:delivery` and `$changerail-all` as equivalent, but present
Codex CLI instructions with `$changerail-deliver`.

If no path is provided and it cannot be inferred, ask for it.

## Operating Mode

- Work in the foreground as the supervised orchestrator for the requested card
  or bounded queue.
- For single-card work, the active session may also perform the delivery worker
  role unless the operator delegates implementation.
- Process one card at a time, completing `ff -> do -> review -> pub` before
  selecting the next card.
- Do not use subagents unless the user explicitly asks for delegated work. The
  review phase is the one exception: it must be a fresh context, never the
  implementing session.
- If a fresh reviewer cannot be launched, validated or truthfully attested, stop
  with safety stop `awaiting external review`.
- Preserve phase safety stops, manifest handling, evidence expectations and
  scoped publish rules.
- Never run `git add .`, `git commit -a`, force-push, reset or checkout
  commands that discard changes.
- Stop on the first safety stop.

## Card Discovery

For a single file path, queue exactly that card. For a directory path, queue
`*.md` files in lexical order and skip obvious non-card files such as
`README.md` and `card-template.md`.

Do not require `openspec/changes/<change>/` directories before accepting a
deliver-ready `2.todo` card. Missing artifacts are work for the fast-forward
phase. If the accepted-card criteria themselves are missing, report the missing
scope, owner, acceptance, ordered plan, dependency or handoff criteria instead
of returning only a boolean readiness failure.

Before starting, run:

```bash
git status --short
openspec list --json
```

Report card count/range, branch and push mode when publish is enabled,
unrelated active OpenSpec changes and dirty-tree caveats.

Before `ff` or `do`, also prove the selected publish target:

- default mode is `remote-push`; the current branch must have an upstream, the
  remote URL must be credential-free, and `git ls-remote --exit-code <remote>
  refs/heads/<branch>` must succeed with secret-free diagnostics;
- `--no-push` is the only local-only bypass, and the log/preflight evidence
  must record that explicit mode and must not claim remote publication
  readiness.

After each phase, re-resolve the current card by filename under:

```text
openspec/board/1.backlog
openspec/board/2.todo
openspec/board/3.inprogress
openspec/board/4.done
openspec/board/5.canceled
```

Stop if the card is duplicated, missing or moved to `5.canceled` without
explicit operator intent.

## Per-Card Pipeline

### 1. Fast-Forward

Run the `changerail-ff` workflow for the current card. This is the internal
artifact-readiness phase for deliver-ready cards whose OpenSpec artifacts do
not exist yet. Continue only when ordered card-owned changes are known,
apply-required artifacts are complete or already archived, and validation
required by `changerail-ff` has passed.

### 2. Deliver

Run the `changerail-do` workflow for the re-resolved card. Continue only when planned
card-owned changes are implemented, verified, synced and archived, and the
delivery manifest/card state is updated. For review-gated cards, the delivery
phase must leave the card in `3.inprogress`; moving to `4.done` belongs to the
post-publish finalization step.

If `changerail-do` stops with `terminal_reason: fix_budget_exhausted`, keep that
pre-review `--max-fix-cycles` budget separate from the post-review
`--max-review-cycles` budget and classify the remaining work before continuing:

- use a bounded same-card micro-fix only when the defect stays inside the
  declared capability, acceptance scope and existing authority, and has one
  concrete verification target;
- create a linked rescue/replacement card when the work adds a capability,
  deliverable, acceptance scope or independently reviewable risk; carry source
  lineage, attempted fixes, findings, retained evidence and verification floor,
  and put the card before blocked downstream work;
- retain `BLOCKED` or `NOT-VERIFIABLE` with evidence and a resume condition for
  unavailable infrastructure, credentials, external authority or another
  blocker that implementation cannot remove.

One bounded continuation does not authorize an unbounded local loop. If it
cannot reach its verification target, stop or materialize the separate scope as
a linked card. Do not request exceptional manual budget merely because the
internal fix counter was exhausted, and do not count this handoff as an
independent-review `NO-GO`.

### 3. Review

Skip only when `--no-review` is supplied and record the operator rationale in
the card `Log`.

Before launching a reviewer, run the deterministic gate from the orchestrator
context:

```bash
bin/changerail-review-verdict preflight "<card-path>" --workspace . \
  --normalize --output ".runtime/changerail/review-preflights/<card-id>.json" --json
```

Handle its outcome before any model launch:

- `blocked`: return the process findings to delivery; do not create a review
  cycle or consume implementation rescue budget;
- `investigation-required`: stop the patch staircase and create/continue an
  investigation or simplification card;
- `machine-reviewed`: the explicitly deterministic/process payload has its one
  required machine review; do not launch an LLM;
- `already-reviewed`: validate the existing exact-payload verdict;
- `ready-for-llm-review`: launch one semantic reviewer with `high` for ordinary
  risk or `xhigh` for critical risk.

For ordinary or critical risk, obtain a valid, fresh `result: go` verdict at:

```text
.runtime/changerail/reviews/<card-id>.json
```

Preferred order:

1. Validate an existing external verdict:
   ```bash
   bin/changerail-review-verdict validate \
     ".runtime/changerail/reviews/<card-id>.json" --check-fresh --workspace . --json
   ```
2. Run a fresh reviewer context when the operator permits this orchestration
   to launch one.
3. Otherwise stop with safety stop `awaiting external review` and report:
   ```text
   $changerail-review <card-path>       # in a fresh session
   $changerail-deliver <card-path>      # resume; completed phases no-op
   ```

On `no-go`, fix blocker findings in card scope using `changerail-do`, then
request a focused fresh re-review. Default `--max-review-cycles` is `2`, allowing
two bounded same-card rescue attempts after the first `no-go`. Reuse unchanged
full-suite evidence only when it is bound to the same payload hash; rerun the
full suite before live admission or final publish.

Treat review cycles and same-card rescue attempts as distinct counters. The
initial independent review is `review_cycle: 1` and does not consume a rescue
attempt (`same_card_rescue_attempt: 0` when recorded). A same-card rescue attempt
is consumed only after an independent `no-go` when the implementing session
fixes scoped blocker findings in the same card; the following fresh review is a
re-review cycle. When review history supports `rescue_budget`, record or
preserve `limit`, `used`, `remaining` and `exhausted`; legacy history without
those optional fields is `unknown`, not inferred from prose.

Keep optional `phase_counters.planning_cycles`, `delivery_fix_cycles`,
`implementation_review_cycles` and `live_admission_reviews` separate. Only an
actual semantic payload verdict increments implementation review or consumes a
same-card rescue; preflight, planning and manifest corrections never do.

Every publish gets one risk-appropriate payload review. A second broad
clean-HEAD LLM audit is allowed at most once when the card explicitly declares
that milestone; never launch it after each micro-rescue or manifest-only
correction. More than 300 added production LOC, a new authority/wire protocol
or a repeated defect class is a typed `investigation-required` stop.

When the default same-card rescue budget is exhausted and the latest review
still returns `no-go`, autonomous delivery MUST NOT ask for manual exceptional
authorization as its default path, self-authorize another same-card rescue, or
publish the dirty payload. Instead, create or request a linked
rescue/replacement card and put it next before blocked downstream work. The
card must carry:

- source card and card lineage;
- latest safe published reference;
- prior `no-go` blocker findings and rescue attempts;
- retained evidence paths or concise summaries;
- current hypothesis;
- required verification floor and fresh review requirement.

If two linked replacement/rescue cards in the same lineage return the same
blocker class or unresolved invariant, the next autonomous card MUST be an
investigation/design card before further implementation rescue. If the blocker
requires unavailable credentials, network, license, stand access, required
software or an unreproducible target condition, record `BLOCKED`, `SUPERSEDED`
or `NOT-VERIFIABLE` with concrete evidence instead of creating another
implementation rescue.

When the execution surface supports machine-readable JSONL events, every
review-gated safety stop that returns without publish must emit a documented
terminal event instead of relying only on assistant prose:

- repeated or final external review `no-go`: `external-review/no-go`
- awaiting external review: `awaiting-review` or `awaiting-external-review`
- pre-review fix budget exhausted: exact completed agent-message lines
  `terminal_outcome: BLOCKED` and
  `terminal_reason: fix_budget_exhausted`
- other blocked publish/review gate stop: `delivery/blocked` or explicit
  `terminal_outcome: BLOCKED`

The delivery runner still checks canonical review evidence as a fail-closed
fallback when this structured event is absent.

When launching a fresh reviewer context, use this review contract as the prompt
body and fill in the card path and id:

```text
You are an independent ChangeRail reviewer for <workspace>.
Run the fresh-context review gate for:
<card-path>

Boundaries:
- You did not plan or implement this payload.
- Do not stage, commit, push or modify tracked reviewed payload files.
- Read AGENTS.md, AGENTS.shared.md, skills/changerail-review/SKILL.md and
  skills/changerail-review/references/changerail-review-verdict.md before
  writing a verdict.
- Review the card, delivery manifest, archived OpenSpec changes, synced specs
  and full working-tree diff for the manifest scope.
- Audit acceptance criteria, evidence claims, mandatory verification, test
  adequacy, scope and public-safety risks.
- Use the preflight risk route: ordinary defaults to `high`; credential,
  mutation, live-admission or final-certification risk uses `xhigh`.
- Do one payload review. On a focused re-review, reuse only unchanged evidence
  bound to the same payload hash; do not invent another clean-HEAD milestone.
- Write only .runtime/changerail/reviews/<card-id>.json and optional ignored
  review history.
- Include reviewer.independence with fresh_context true,
  did_not_plan_or_implement true and a non-empty basis.
- Compute the workspace fingerprint and validate the verdict with:
  bin/changerail-review-verdict validate \
    .runtime/changerail/reviews/<card-id>.json --json
```

After the reviewer returns, the orchestrator MUST validate the canonical verdict
with `--check-fresh` before publish. This freshness check includes the reviewed
Git tree SHA when the verdict schema requires it:

```bash
bin/changerail-review-verdict validate \
  ".runtime/changerail/reviews/<card-id>.json" --check-fresh --workspace . --json
```

### 4. Publish

Run `changerail-pub` for the re-resolved card. Pass `--no-push` when supplied. Do not
publish without a fresh risk-appropriate `machine-reviewed` receipt or valid
`go` verdict unless the operator explicitly
invoked standalone publish and the publish skill permits that exception.

## Safety Stops

Stop and report clearly when:

- card discovery is empty or ambiguous;
- a phase skill stops;
- semantic review is required but no valid verdict is present;
- a verdict is stale, invalid or `no-go` beyond allowed same-card review cycles
  and autonomous linked-card escalation cannot be created safely;
- publish scope would include unrelated files;
- unresolved staged changes or uncommitted card-owned files remain from a
  previous card;
- push target is missing or rejected;
- a destructive git operation would be needed;
- the user asks to pause, stop, review or change direction.

## Completion

Summarize:

- cards completed, skipped or blocked;
- archive paths or commits;
- verification commands and outcomes;
- review verdicts or recorded skips;
- manifest paths and excluded runtime artifacts;
- remaining unrelated active changes or dirty files;
- exact next command for any stopped card.
