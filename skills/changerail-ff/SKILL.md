---
name: changerail-ff
description: Run the generic ChangeRail board/card fast-forward planning loop. Use when the user asks for `$changerail-ff`, `changerail:ff`, `/changerail:ff`, `changerail:fff`, or wants to take an unprocessed OpenSpec board card or story, decompose it into implementation-sized changes, update the card, and generate apply-ready OpenSpec artifacts without implementing code.
---

# ChangeRail FF

## Purpose

Turn a board card or backlog story into an apply-ready OpenSpec change set.

```text
$changerail-ff <card-path>
```

This is planning only. The skill may create or update board cards and
`openspec/changes/<change>/` artifacts, but it does not implement code,
archive changes or publish commits.

## Project Context

At the start, resolve the repository root from the current working directory or
`CODEX_WORKDIR`. Then read only relevant context:

1. `openspec/config.yaml` if it exists.
2. `openspec/project.md` only as legacy fallback.
3. `AGENTS.md`, `AGENTS.shared.md`, `openspec/board/README.md` and
   `openspec/board/card-template.md` when present.
4. The target board card or backlog file.
5. Existing active or archived OpenSpec changes that the card references or
   depends on.

Treat project ownership, non-goals, verification rules, board conventions and
cross-repo boundaries from those files as binding.

## Inputs

Expected form:

```text
$changerail-ff openspec/board/1.backlog/card.md
$changerail-ff openspec/board/2.todo/card.md
```

Useful flags when present:

```text
$changerail-ff <card> --max-changes 4
$changerail-ff <card> --from change-slug
$changerail-ff <card> --until change-slug
$changerail-ff <card> --no-move
```

Accept legacy spellings such as `/changerail:ff <card>`, `changerail:ff <card>` and
`changerail:fff <card>` as equivalent, but present Codex CLI instructions with
`$changerail-ff`.

If no card path is provided and it cannot be inferred, ask for it.

## Operating Mode

- Plan and create OpenSpec artifacts only.
- Work in the foreground and keep the user informed before major stages.
- Keep changes scoped to the board card and `openspec/changes/<change>/`
  artifacts.
- Prefer small implementation-sized changes with clear boundaries and
  dependencies. A typical card decomposes into about 2-5 such changes; if it
  needs many more, it is likely two cards.
- Stop if the story cannot be decomposed without product or architecture
  clarification.
- Do not launch nested agent CLIs or background batches unless the user
  explicitly asks for delegated work.

## Stage 1: Read And Assess The Card

1. Run:
   ```bash
   openspec list --json
   ```
2. Read the target card or backlog file.
3. Identify:
   - user story or operator problem;
   - observable acceptance criteria;
   - explicit constraints, non-goals and related links;
   - affected capabilities or specs;
   - cross-repo ownership boundaries;
   - existing `## Change N:` sections, if any.
4. Check for matching active or archived changes before proposing new slugs.

If the card is too vague, ask a concise clarification question instead of
inventing architecture.

## Stage 2: Decompose The Story

If the card has no ordered change sections, create them. If it already has
sections, refine only missing details and preserve existing slugs unless they
are clearly unsafe.

Good changes are:

- independently understandable;
- small enough to implement and verify;
- ordered by dependency;
- scoped to one owner or repository whenever possible;
- named with stable kebab-case slugs.

Avoid:

- one giant change for a broad story;
- artificial micro-changes that cannot be verified independently;
- changes that cross repository ownership without an explicit linked card;
- speculative implementation details not supported by project context.

Recommended card section shape:

```md
## Change 1: `change-slug`

### Why
...

### Goal
...

### Scope
- ...

### Acceptance
- ...

### Depends On
- none

### Related
- `openspec/changes/change-slug/`
```

Update common card fields when present:

- `Status`
- `OpenSpec Stage`
- `Change Set`
- `Verify`
- `Related`
- `Result`
- `Next`
- `Log`

If the card starts in `openspec/board/1.backlog/`, move it to
`openspec/board/2.todo/` after decomposition unless `--no-move` is present or
local board docs say otherwise.

## Stage 3: Create Or Complete Change Artifacts

For each selected planned change:

1. If archived, record it and skip.
2. If active, inspect current state:
   ```bash
   openspec status --change "<change>" --json
   ```
3. If pending, create it:
   ```bash
   openspec new change "<change>"
   ```
4. Create artifacts in dependency order until all apply-required artifacts are
   done:
   ```bash
   openspec status --change "<change>" --json
   openspec instructions <artifact-id> --change "<change>" --json
   ```
5. For each artifact:
   - read dependency artifacts first;
   - apply `context`, `rules`, `instruction` and `template` from the
     instructions output;
   - write the artifact to `outputPath`;
   - do not copy raw instruction blocks into artifact content;
   - keep the artifact aligned with the card and project context.
6. Re-run status after each artifact and stop when every required artifact is
   done.
7. Validate:
   ```bash
   openspec validate "<change>" --strict
   git diff --check
   ```

Do not overwrite completed artifacts casually. If an existing artifact
conflicts with the refined card plan, report the mismatch and ask whether to
update the artifact or preserve it.

## Stage 4: Final Card Sync

After all selected changes are apply-ready:

1. Ensure every card `Related` and `Change Set` entry points to the actual
   change directory.
2. Set `OpenSpec Stage` to `artifacts` or the local equivalent.
3. Set `Next` to the project's delivery workflow. If the `changerail-do` surface is
   installed, use:
   ```text
   $changerail-do <card-path>
   ```
   Otherwise state that the card is ready for the delivery workflow once that
   surface is installed.
4. Run:
   ```bash
   openspec validate --all --strict
   git diff --check
   ```

If new untracked files were created, make sure whitespace checks cover them
explicitly, either through staging/intent-to-add or a separate scan.

## Safety Stops

Stop and report clearly when:

- the card belongs to another repository;
- the story needs clarification before decomposition;
- a planned change slug conflicts with an unrelated active or archived change;
- generated artifacts would contradict existing artifacts;
- OpenSpec validation fails and the fix is not local to the card or change
  artifacts;
- the dirty tree contains unrelated edits in files this planning pass must
  modify;
- a destructive git operation would be needed;
- the user asks to pause, review or change direction.

## Output

When done, summarize:

- card path;
- generated or reused change slugs;
- artifacts created or completed for each change;
- validation commands and outcomes;
- remaining caveats;
- delivery handoff:
  ```text
  $changerail-do <card-path>  # when the changerail-do surface is installed
  ```
  or a clear note that delivery is deferred until that surface exists.
