---
name: opsx-review
description: Run the independent OPSX review gate for a delivered board card before publish, producing a machine-checkable go/no-go verdict in ignored runtime state.
---

# OPSX Review

## Purpose

Provide the independent quality gate between delivery and publish:

```text
$opsx-do <card-path>      # implementing session
$opsx-review <card-path>  # fresh-context review verdict
$opsx-pub <card-path>     # publish only after go
```

The reviewer produces evidence, not fixes. Its only write is the verdict file
under `.runtime/opsx/reviews/`.

## Independence Requirement

This skill must run in a context that did not plan or implement the card:

- a fresh non-interactive reviewer session;
- a fresh dedicated subagent;
- a separate interactive session driven by the operator.

If the current session produced any diff under review, stop immediately and
report a self-review violation instead of writing a verdict.

## Project Context

Resolve the repository root from the current working directory or
`CODEX_WORKDIR`. Read:

1. `openspec/config.yaml` if present.
2. `AGENTS.md`, `AGENTS.shared.md`, board docs and local workflow docs that
   define verification, repo boundaries and board conventions.
3. The target card and ordered `## Change N:` sections.
4. Archived OpenSpec changes referenced by the card.
5. `.runtime/opsx/delivery-manifests/<card-id>.json` when present.

## Shared Review Verdict

Read `references/opsx-review-verdict.md` before writing a verdict. The verdict
path is:

```text
.runtime/opsx/reviews/<card-id>.json
```

The canonical schema id is `opsx.review-verdict.v1`. Use
`scripts/opsx_review_verdict.py` when present, otherwise the linked
`bin/opsx-review-verdict` helper, to compute and validate verdicts.

## Inputs

Expected forms:

```text
$opsx-review <card-path>
$opsx-review <card-path> --cycle 2
```

Accept legacy prompt forms such as `/opsx:review <card>` and
`opsx:review <card>` as equivalent, but present Codex CLI instructions with
`$opsx-review`.

## Workflow

### 1. Resolve Scope And Fingerprint

Run:

```bash
git status --short
git diff HEAD --stat
openspec list --json
python3 scripts/opsx_review_verdict.py fingerprint --workspace .
```

Read the card and delivery manifest. Confirm card-owned changes are archived.
If a manifest exists, treat `committable_paths` as the claimed publish scope;
otherwise reconstruct scope from the card, archives and `git status`.

### 2. Evidence Audit

For every verification claim in the card, archived tasks and manifest:

- identify the command that allegedly ran;
- identify the retained output, evidence path or observed output summary;
- re-run cheap read-only checks when feasible;
- mark unbacked mandatory claims as findings.

Fill one `acceptance` entry per card acceptance criterion. Generic assurance is
not evidence.

### 3. Diff Review

Read the full working-tree diff for the claimed publish scope:

```bash
git diff HEAD -- <committable paths>
```

Also inspect untracked committable files listed by `git status --short`. Check
correctness against the card, scope boundaries, tests, docs, schemas, error
handling and public-safety risks.

### 4. Test Adequacy Critique

For added or changed tests, answer whether they would fail if the behavior were
broken. Flag missing coverage, tautological assertions, weakened tests and
missing RED evidence where the project required test-first work.

### 5. Write And Validate Verdict

Assign findings `R1..Rn`:

- `blocker`: publish would ship a defect, missing mandatory evidence, failed
  acceptance or out-of-scope change;
- `major`: important but non-blocking follow-up;
- `minor`: small cleanup.

Set `result` to `no-go` when any blocker exists or any acceptance criterion is
`fail`; otherwise set `go`. Validate:

```bash
python3 scripts/opsx_review_verdict.py validate \
  ".runtime/opsx/reviews/<card-id>.json" --json
```

## Safety Stops

Stop without writing a verdict when:

- this session implemented or planned the card;
- card-owned changes are not archived;
- neither a manifest nor a reconstructable publish scope exists;
- the workspace is not a git repository or the fingerprint cannot be computed;
- the verdict cannot be validated after writing;
- the user asks to pause, stop or change direction.

## Output

Summarize:

- card path and review cycle;
- result and findings by severity;
- per-acceptance verdicts with evidence;
- unbacked claims;
- verdict path;
- exact next command (`$opsx-pub <card-path>` on `go`, otherwise the fix list).
