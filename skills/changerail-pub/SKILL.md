---
name: changerail-pub
description: Run the final ChangeRail publish loop for a reviewed board card: validate review verdict, confirm reviewed docs, create a scoped commit and push unless disabled.
---

# ChangeRail Pub

## Purpose

Finalize a delivered and independently reviewed ChangeRail board card:

```text
$changerail-review <card-path>  # fresh-context go/no-go verdict
$changerail-pub <card-path>     # scoped commit and push
```

Invoking `$changerail-pub` is explicit permission to create a scoped commit and push
unless `--no-push` is supplied or project policy forbids pushing.

## Project Context

Resolve the repository root from the current working directory or
`CODEX_WORKDIR`. Read:

1. `openspec/config.yaml` if present.
2. `AGENTS.md`, `AGENTS.shared.md`, board docs and local workflow docs that
   affect docs, checks, commit style, branch policy or repo boundaries.
3. The target card and archived card-owned changes.
4. Existing docs likely affected by the implemented behavior.

## Inputs

Expected form:

```text
$changerail-pub <card-path>
```

Useful flags:

```text
$changerail-pub <card-path> --no-push
$changerail-pub <card-path> --message "type(scope): summary"
$changerail-pub <card-path> --docs-only
$changerail-pub <card-path> --allow-unarchived
```

Accept legacy prompt forms such as `/changerail:pub <card>`, `changerail:pub <card>` and
`changerail:ship <card>` as equivalent, but present Codex CLI instructions with
`$changerail-pub`.

## Operating Mode

- Work in the foreground.
- Never run `git add .`, `git commit -a`, force-push, reset or checkout
  commands that discard changes.
- Commit only files tied to the named card, archived changes, synced specs,
  docs, tests and board state.
- Stop if unrelated dirty files cannot be separated confidently.

## Review Gate

Read `../changerail-review/references/changerail-review-verdict.md` before publishing.

At the start of publish, before documentation edits change the working tree,
validate the verdict:

```bash
python3 scripts/changerail_review_verdict.py validate \
  ".runtime/changerail/reviews/<card-id>.json" --check-fresh --workspace . --json
```

If the verdict is absent, stale, invalid or not `result: go`, stop before
staging. Never stage the verdict file.

## Workflow

### 1. Read Final State

Run:

```bash
git status --short
git branch --show-current
git remote -v
openspec list --json
```

Read the target card, delivery manifest when present, and archived change
artifacts. Verify card-owned changes are archived unless `--allow-unarchived`
is present.

Build a publish scope from manifest `committable_paths`, archive paths, synced
specs, card state, docs and changed files. Exclude runtime paths and unrelated
active OpenSpec changes.

### 2. Documentation Check

Confirm durable docs that changed user-facing commands, workflow, contracts or
setup are already part of the reviewed payload. Prefer existing docs. For
review-gated cards, do not make substantive code, docs, specs, schema, script
or test edits after a fresh `go` verdict; stop and send the card back through
delivery/review if such edits are required. If no docs need updates, record
that reason in the card or final summary.

### 3. Final Verification

Run:

```bash
git diff --check
openspec validate --all --strict
```

Also run focused checks required by tasks, project config or affected code.
Do not commit while final verification is failing unless the operator
explicitly requests publishing a known failing state and the card records the
residual risk.

### 4. Commit

Review:

```bash
git status --short
git diff --stat
git diff --cached --stat
```

Stage explicit paths only:

```bash
git add -- <path> ...
git diff --cached --stat
git diff --cached --check
git commit -m "<message>"
```

Use `--message` when provided. Otherwise derive a concise message from the
card summary and local commit style.

### 5. Card Sync

After a successful commit, update the card with result, commit hash, push
status, log entry and the documented `4.done` board move when local board
conventions require it. This post-publish card metadata is deterministic
finalization, not a substantive change to the reviewed payload. If this creates
a new card-only diff before push, amend only the card with explicit staging.

### 6. Push

Skip only with `--no-push`.

```bash
git branch --show-current
git rev-parse --abbrev-ref --symbolic-full-name @{u}
git push
```

If no upstream exists and project policy permits it, use `git push -u origin
HEAD`. Never force-push.

## Safety Stops

Stop when:

- the review verdict is absent, stale, invalid or `no-go`;
- planned card-owned changes are not archived and `--allow-unarchived` is not
  present;
- final verification fails;
- staged files include unrelated work;
- commit identity is not configured;
- branch is detached, no allowed push target exists, or push is rejected;
- a destructive git operation would be needed;
- the user asks to pause, review or change direction.

## Output

Summarize:

- card path;
- review gate result;
- docs updated or skipped;
- checks run and outcomes;
- commit hash and message;
- push target/result or `--no-push`;
- excluded runtime artifacts;
- unrelated dirty files left untouched.
