---
name: changerail-do
description: Run a supervised ChangeRail delivery loop for a board card or backlog file: implement each planned OpenSpec change, verify it, sync specs and archive completed changes without publishing.
---

# ChangeRail Do

## Purpose

Deliver the implementation part of the ChangeRail lifecycle:

```text
$changerail-ff <card-path>      # plan/decompose and create apply-ready artifacts
$changerail-do <card-path>      # implement, verify, sync specs and archive
$changerail-review <card-path>  # independent go/no-go review
$changerail-pub <card-path>     # scoped commit and push
```

`changerail-do` works in the foreground as the implementing session. It does not
review itself, commit, push or publish.

In the supervised role model this skill is the delivery worker. The delivery
worker may be the same active session as the orchestrator for small or
single-card work, but it must never act as the independent reviewer for the
payload it planned or implemented.

## Project Context

Resolve the repository root from the current working directory or
`CODEX_WORKDIR`. Read only context relevant to the requested card or change:

1. `openspec/config.yaml` if present.
2. `AGENTS.md`, `AGENTS.shared.md`, board docs and local workflow docs that
   define verification, repo boundaries or safety policy.
3. The named board card or backlog section.
4. Active OpenSpec artifacts for the card-owned changes.

Treat project-specific verification commands and repository boundaries as
binding. If the requested work belongs to another repository, stop and report
that boundary.

## Shared Delivery Manifest

For card-level runs, maintain ignored runtime state at:

```text
.runtime/changerail/delivery-manifests/<card-id>.json
```

Use the card filename without `.md` as `<card-id>`. Record repository-relative
paths only:

- card metadata and ordered planned change slugs;
- `preexisting_dirty` from `git status --short` at delivery start;
- card-owned committable paths introduced by planning, implementation, synced
  specs, archives, docs, tests and board updates;
- excluded runtime paths such as manifests, review verdicts, raw command logs
  and local evidence files.

Validate or normalize the manifest with `scripts/changerail_delivery_manifest.py`
when a project provides that helper. If no helper exists, keep the manifest
small, structured and conservative; publish must still re-check scope before
staging.

## Inputs

Expected forms:

```text
$changerail-do <card-path>
$changerail-do <card-path> --from change-slug
$changerail-do <card-path> --until change-slug
$changerail-do <card-path> --max-fix-cycles 2
```

Accept legacy prompt forms such as `/changerail:do <card-path>` and
`changerail:do <card-path>` as equivalent, but present Codex CLI instructions with
`$changerail-do`.

If no card path is provided and it cannot be inferred, ask for it.

## Plan Discovery

1. Run:
   ```bash
   git status --short
   openspec list --json
   ```
2. Read the card and extract ordered change ids from `## Change N:` sections
   and `Change Set`.
3. Classify each card-owned change:
   - `archived`: exists under `openspec/changes/archive/YYYY-MM-DD-<change>/`;
   - `active`: exists under `openspec/changes/<change>/`;
   - `pending`: no active or archived directory exists;
   - `blocked`: dependency or required context is missing.
4. Treat unrelated active OpenSpec changes as workspace context, not a blocker,
   unless they overlap files this card must modify.
5. Report the planned change count, archived count, active count, next selected
   change and dirty-tree caveats.

## Per-Change Workflow

Process one card-owned pending or active change at a time.

### 1. Complete Artifacts

Use OpenSpec status as the source of truth:

```bash
openspec status --change "<change>" --json
```

If apply-required artifacts are missing, follow the `openspec-ff-change`
procedure: create artifacts in dependency order using
`openspec instructions <artifact-id> --change "<change>" --json`. Stop if an
artifact cannot be produced without clarification.

### 2. Apply Implementation

Use the `openspec-apply-change` procedure:

```bash
openspec instructions apply --change "<change>" --json
```

Read every context file returned by the CLI. Implement tasks in order and mark
each task complete only after the corresponding implementation and verification
are in place.

For testable code changes, prefer test-first discipline: add or extend the
focused test first, run it and record the failing RED result, then implement
until the same test passes. For docs-only, config-only or non-testable changes,
record why RED evidence is not applicable.

### 3. Verify

Minimum verification for every change:

```bash
openspec status --change "<change>" --json
openspec instructions apply --change "<change>" --json
openspec validate "<change>" --strict
git diff --check
```

Also run focused checks required by `tasks.md`, `design.md`,
`openspec/config.yaml`, `AGENTS.md` or affected code. Build the mandatory
verification floor from project-declared sources: `AGENTS.md`,
`openspec/config.yaml`, OpenSpec `tasks.md`/`design.md` and the affected
toolchain. Formatter, strict typing and clean/ambient environment matrices are
mandatory only when those sources declare them or the changed surface requires
them. For docs/config-only changes, `openspec validate` plus whitespace/config
parsing checks are normally sufficient.

Every verification claim recorded in the card, tasks or manifest must name the
executed command and observed outcome. Keep raw logs in ignored runtime state
when needed; do not commit local runtime evidence.

For added or changed tests, record why the test observes the intended behavior
source and would fail if the claimed regression were present. For docs-only,
config-only or otherwise non-test-firstable work, record why RED evidence is
not applicable instead of claiming a failure that was not run.

### 4. Fix And Reverify

Default `--max-fix-cycles` is `2`.

If verification finds actionable defects:

1. Fix issues in the current change scope.
2. Add or adjust tests when appropriate.
3. Re-run the same verification commands.
4. Stop if the same finding repeats, fixes require unrelated scope, or the
   command cannot be made green within the allowed cycles.

### 5. Sync Specs

Before archiving, sync delta specs into main specs using the
`openspec-sync-specs` procedure. Read each delta under
`openspec/changes/<change>/specs/*/spec.md` and update the corresponding main
spec under `openspec/specs/<capability>/spec.md` idempotently.

Run:

```bash
openspec validate "<capability>" --strict
openspec validate --all --strict
```

Do not archive a change whose delta specs have not been synced unless the user
explicitly requests that exception.

### 6. Archive

Use the `openspec-archive-change` procedure after successful verification and
spec sync:

```bash
openspec archive "<change>" --yes
openspec validate --all --strict
git diff --check
```

Record archive paths in the card and delivery manifest.

### 7. Board/Card Update

If the input is an ChangeRail board card, keep status fields, verification notes,
archive paths, result, next step and log consistent with local board
conventions. For review-gated cards, `changerail-do` MUST leave the story in
`3.inprogress` after implementation, verification, spec sync and archive. Do
not move the card to `4.done`; that is a deterministic post-publish
finalization responsibility of `changerail-pub`.

## Safety Stops

Stop and report clearly when:

- a dependency is missing or another active change owns the same files;
- artifacts or implementation need product clarification;
- verification cannot be made clean within the fix-cycle limit;
- `openspec validate --all` fails after sync or archive;
- the dirty tree contains unrelated edits in files the next change must touch;
- implementation would require another repository;
- a destructive git operation would be needed;
- the user asks to pause, review or change direction.

## Output

When complete, summarize:

- completed changes and archive paths;
- verification commands and outcomes;
- delivery manifest path and excluded runtime artifacts;
- remaining unrelated active changes or dirty files;
- board/card status updates;
- exact next command:
  ```text
  $changerail-review <card-path>
  ```
  followed by `$changerail-pub <card-path>` after a fresh `go` verdict.
