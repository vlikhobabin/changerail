---
name: changerail-pub
description: "Run the final ChangeRail publish loop for a reviewed board card: validate its risk-appropriate gate, confirm reviewed docs, create a scoped commit and push unless disabled."
---

# ChangeRail Pub

## Purpose

Finalize a delivered and risk-appropriately reviewed ChangeRail board card:

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
rerun deterministic preflight without normalization:

```bash
bin/changerail-review-verdict preflight "<card-path>" --workspace . \
  --output ".runtime/changerail/review-preflights/<card-id>.json" --json
```

For an explicitly deterministic/process payload, fresh `machine-reviewed` is
the required payload gate and no LLM verdict exists. For ordinary or critical
risk, validate the verdict:

```bash
bin/changerail-review-verdict validate \
  ".runtime/changerail/reviews/<card-id>.json" --check-fresh --workspace . --json
```

For ordinary or critical risk, if the verdict is absent, stale, invalid or not `result: go`, stop before
staging. A verdict whose reviewed `workspace.tree_sha` is missing or differs
from the current publish tree is stale for review-gated publish and requires a
fresh review. Never stage the verdict file.

If the project declares `.changerail/execution-target.json`, deterministic
preflight must also prove current declaration, manifest and retained evidence
have one exact matching target identity. Missing, multiple or mismatched target
identity blocks publish; do not stage or propose provider substitution.

## Workflow

### 1. Read Final State

Run:

```bash
git status --short
git branch --show-current
git remote -v
bin/openspec list --json
```

Read the target card, delivery manifest when present, and archived change
artifacts. Verify card-owned changes are archived unless `--allow-unarchived`
is present.

Build a publish scope from manifest `committable_paths`, archive paths, synced
specs, card state, docs and changed files. Exclude runtime paths and unrelated
active OpenSpec changes.

When a delivery manifest exists and the helper supports `scope-check`, compare
the manifest with the working tree before staging:

```bash
bin/changerail-delivery-manifest scope-check \
  ".runtime/changerail/delivery-manifests/<card-id>.json" \
  --target working-tree --json
```

Stop before staging if the result reports missing, extra or mismatched
committable paths.

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
bin/openspec validate --all --strict
```

Also run focused checks required by tasks, project config or affected code.
Rerun the complete project-declared verification suite immediately before final
publish (and separately before live admission when applicable); focused
re-review may reuse prior suite evidence only while its payload hash is
unchanged. Do not add a clean-HEAD LLM audit here unless this is the single
milestone explicitly declared by the card.
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
bin/changerail-delivery-manifest scope-check \
  ".runtime/changerail/delivery-manifests/<card-id>.json" \
  --target staged --json
git commit -m "<message>"
```

If staged scope reconciliation reports any missing, extra or mismatched path,
unstage the incorrect explicit path set only after confirming it is safe, then
return to scope review. Never include unrelated staged paths in the commit.

Use `--message` when provided. Otherwise derive a concise message from the
card summary and local commit style.

### 5. Card Sync

After a successful payload commit, update the card with stable result, log
entry and the documented `4.done` board move when local board conventions
require it. Do not write the card's own exact final commit hash or mutable push
status into tracked card text; exact payload/published commit and push metadata
belongs in the ignored delivery manifest. This post-publish card metadata is
deterministic finalization, not a substantive change to the reviewed payload. If
this creates a new card-only diff before push, amend only the card with explicit
staging.

When the workspace provides `bin/changerail-delivery-manifest`, prefer
helper-assisted finalization through the shared Python runtime selector:

```bash
bin/changerail-delivery-manifest finalize-card "<card-path>" \
  --commit "<payload-commit>" --remote "<remote>" --branch "<branch>" \
  --push-status pending --timestamp "<utc>"
git add -- <old-card-path> <new-card-path>
git commit --amend --no-edit
```

This helper may only move/update board metadata: `Status`, `Owner`,
`OpenSpec Stage`, `Result`, `Next` and `Log`. If finalization would require
substantive code, docs, specs, schemas, scripts or tests changes, stop and send
the card back through delivery/review.

### 6. Push

Skip only with `--no-push`.

```bash
git branch --show-current
git rev-parse --abbrev-ref --symbolic-full-name @{u}
git push
```

If no upstream exists and project policy permits it, use `git push -u origin
HEAD`. Never force-push.

When `--no-push` is supplied, do not claim remote publication readiness. After
the card-only amend, update the ignored manifest with skipped local-only publish
evidence when the helper exists:

```bash
bin/changerail-delivery-manifest publish-update \
  ".runtime/changerail/delivery-manifests/<card-id>.json" \
  --status skipped --payload-commit "<payload-commit>" \
  --published-commit "<local-final-commit>" \
  --reason "push skipped by --no-push" --mode local-only
```

After push, update ignored manifest publish metadata when the helper exists:

```bash
bin/changerail-delivery-manifest publish-update \
  ".runtime/changerail/delivery-manifests/<card-id>.json" \
  --status pushed --payload-commit "<payload-commit>" \
  --published-commit "<published-commit>" --remote "<remote>" \
  --branch "<branch>" --pushed-at "<utc>" --mode review-gated
```

Never stage the ignored manifest.

## Safety Stops

Stop when:

- the risk-appropriate machine receipt or semantic review verdict is absent,
  stale, invalid or negative;
- declared execution target evidence is missing, mismatched or substituted;
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
