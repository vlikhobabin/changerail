---
name: changerail-deliver
description: Run the complete ChangeRail card pipeline in one supervised foreground workflow: ff, do, independent review gate and publish.
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
$changerail-deliver <path> --max-review-cycles 5
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

Before starting, run:

```bash
git status --short
openspec list --json
```

Report card count/range, branch and push mode when publish is enabled,
unrelated active OpenSpec changes and dirty-tree caveats.

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

Run the `changerail-ff` workflow for the current card. Continue only when ordered
card-owned changes are known, apply-required artifacts are complete or already
archived, and validation required by `changerail-ff` has passed.

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

Otherwise obtain a valid, fresh `result: go` verdict at:

```text
.runtime/changerail/reviews/<card-id>.json
```

Preferred order:

1. Validate an existing external verdict:
   ```bash
   python3 scripts/changerail_review_verdict.py validate \
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
request a fresh re-review. Default `--max-review-cycles` is `5`, allowing five
bounded same-card rescue attempts after the first `no-go`; each rescue attempt
still requires a fresh independent re-review before publish.

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
- Write only .runtime/changerail/reviews/<card-id>.json and optional ignored
  review history.
- Include reviewer.independence with fresh_context true,
  did_not_plan_or_implement true and a non-empty basis.
- Compute the workspace fingerprint and validate the verdict with:
  python3 scripts/changerail_review_verdict.py validate \
    .runtime/changerail/reviews/<card-id>.json --json
```

After the reviewer returns, the orchestrator MUST validate the canonical verdict
with `--check-fresh` before publish:

```bash
python3 scripts/changerail_review_verdict.py validate \
  ".runtime/changerail/reviews/<card-id>.json" --check-fresh --workspace . --json
```

### 4. Publish

Run `changerail-pub` for the re-resolved card. Pass `--no-push` when supplied. Do not
publish without a fresh valid `go` verdict unless the operator explicitly
invoked standalone publish and the publish skill permits that exception.

## Safety Stops

Stop and report clearly when:

- card discovery is empty or ambiguous;
- a phase skill stops;
- external review is required but no valid verdict is present;
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
