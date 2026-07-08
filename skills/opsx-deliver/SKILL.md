---
name: opsx-deliver
description: Run the complete OPSX card pipeline in one supervised foreground workflow: ff, do, independent review gate and publish.
---

# OPSX Deliver

## Purpose

Orchestrate the standard OPSX card pipeline:

```text
$opsx-ff <card-path>      # plan/decompose and create apply-ready artifacts
$opsx-do <card-path>      # implement, verify, sync specs and archive
$opsx-review <card-path>  # independent fresh-context verdict
$opsx-pub <card-path>     # scoped commit and push
```

This skill is an orchestration layer. Before executing each phase, read and
follow the effective `opsx-ff`, `opsx-do`, `opsx-review` or `opsx-pub`
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
$opsx-deliver <card-path>
$opsx-deliver <board-column>
$opsx-deliver <card-path> --no-push
```

Useful flags:

```text
$opsx-deliver <path> --from change-slug
$opsx-deliver <path> --until change-slug
$opsx-deliver <path> --max-cards 3
$opsx-deliver <path> --no-push
$opsx-deliver <path> --max-fix-cycles 2
$opsx-deliver <path> --no-review
$opsx-deliver <path> --max-review-cycles 1
```

Accept legacy prompt forms such as `/opsx:deliver`, `opsx:deliver`,
`$opsx-delivery`, `/opsx:delivery` and `$opsx-all` as equivalent, but present
Codex CLI instructions with `$opsx-deliver`.

If no path is provided and it cannot be inferred, ask for it.

## Operating Mode

- Work in the foreground as the active agent.
- Process one card at a time, completing `ff -> do -> review -> pub` before
  selecting the next card.
- Do not use subagents unless the user explicitly asks for delegated work. The
  review phase is the one exception: it must be a fresh context, never the
  implementing session.
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

Run the `opsx-ff` workflow for the current card. Continue only when ordered
card-owned changes are known, apply-required artifacts are complete or already
archived, and validation required by `opsx-ff` has passed.

### 2. Deliver

Run the `opsx-do` workflow for the re-resolved card. Continue only when planned
card-owned changes are implemented, verified, synced and archived, and the
delivery manifest/card state is updated.

### 3. Review

Skip only when `--no-review` is supplied and record the operator rationale in
the card `Log`.

Otherwise obtain a valid, fresh `result: go` verdict at:

```text
.runtime/opsx/reviews/<card-id>.json
```

Preferred order:

1. Validate an existing external verdict:
   ```bash
   python3 scripts/opsx_review_verdict.py validate \
     ".runtime/opsx/reviews/<card-id>.json" --check-fresh --workspace . --json
   ```
2. Run a fresh reviewer context when the operator permits this orchestration
   to launch one.
3. Otherwise stop with safety stop `awaiting external review` and report:
   ```text
   $opsx-review <card-path>       # in a fresh session
   $opsx-deliver <card-path>      # resume; completed phases no-op
   ```

On `no-go`, fix blocker findings in card scope using `opsx-do`, then request
one re-review. Default `--max-review-cycles` is `1`; a second consecutive
`no-go` is a safety stop.

### 4. Publish

Run `opsx-pub` for the re-resolved card. Pass `--no-push` when supplied. Do not
publish without a fresh valid `go` verdict unless the operator explicitly
invoked standalone publish and the publish skill permits that exception.

## Safety Stops

Stop and report clearly when:

- card discovery is empty or ambiguous;
- a phase skill stops;
- external review is required but no valid verdict is present;
- a verdict is stale, invalid or `no-go` beyond allowed review cycles;
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
