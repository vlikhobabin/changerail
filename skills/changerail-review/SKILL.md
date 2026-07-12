---
name: changerail-review
description: Run the independent ChangeRail review gate for a delivered board card before publish, producing a machine-checkable go/no-go verdict in ignored runtime state.
---

# ChangeRail Review

## Purpose

Provide the independent quality gate between delivery and publish:

```text
$changerail-do <card-path>      # implementing session
$changerail-review <card-path>  # fresh-context review verdict
$changerail-pub <card-path>     # publish only after go
```

The reviewer produces evidence, not fixes. Its writes are ignored runtime
review evidence under `.runtime/changerail/reviews/`: the latest canonical verdict and
optional review-cycle history. It must not modify reviewed payload files.

## Independence Requirement

This skill must run in a context that did not plan or implement the card:

- a fresh non-interactive reviewer session;
- a fresh dedicated subagent;
- a separate interactive session driven by the operator.

If the current session produced any diff under review, stop immediately and
report a self-review violation instead of writing a verdict.

Every verdict must include `reviewer.independence` attestation:

- `fresh_context: true`
- `did_not_plan_or_implement: true`
- non-empty `basis` describing why the reviewer can truthfully make that claim

The helper validates this attestation as a publish-gate contract. It is not a
cryptographic proof of identity; if the reviewer cannot truthfully attest
independence, stop instead of writing a verdict.

## Project Context

Resolve the repository root from the current working directory or
`CODEX_WORKDIR`. Read:

1. `openspec/config.yaml` if present.
2. `AGENTS.md`, `AGENTS.shared.md`, board docs and local workflow docs that
   define verification, repo boundaries and board conventions.
3. The target card and ordered `## Change N:` sections.
4. Archived OpenSpec changes referenced by the card.
5. `.runtime/changerail/delivery-manifests/<card-id>.json` when present.

## Shared Review Verdict

Read `references/changerail-review-verdict.md` before writing a verdict. The verdict
path is:

```text
.runtime/changerail/reviews/<card-id>.json
```

The canonical schema id is `changerail.review-verdict.v1`. Use
`scripts/changerail_review_verdict.py` when present, otherwise the linked
`bin/changerail-review-verdict` helper, to compute and validate verdicts.

When retaining review-cycle evidence, keep the latest canonical verdict at:

```text
.runtime/changerail/reviews/<card-id>.json
```

Store cycle history separately, for example:

```text
.runtime/changerail/reviews/<card-id>.history.json
```

History must not replace the canonical verdict used by publish freshness
validation.

## Inputs

Expected forms:

```text
$changerail-review <card-path>
$changerail-review <card-path> --cycle 2
```

Accept legacy prompt forms such as `/changerail:review <card>` and
`changerail:review <card>` as equivalent, but present Codex CLI instructions with
`$changerail-review`.

## Workflow

### 1. Resolve Scope And Fingerprint

Run:

```bash
git status --short
git diff HEAD --stat
openspec list --json
python3 scripts/changerail_review_verdict.py fingerprint --workspace .
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

Audit the mandatory verification floor declared by `AGENTS.md`,
`openspec/config.yaml`, archived `tasks.md`/`design.md` and the affected
toolchain. Missing command/outcome evidence for a mandatory check is an
evidence finding. Formatter, strict typing and environment-matrix checks are
mandatory only when those sources declare them or the changed surface makes
them necessary.

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
missing RED evidence where the project required test-first work. Treat an
explicit docs-only/config-only RED-not-applicable note as evidence to audit,
not as an automatic failure.

### 5. Write And Validate Verdict

Assign findings `R1..Rn`:

- `blocker`: publish would ship a defect, missing mandatory evidence, failed
  acceptance or out-of-scope change;
- `major`: important but non-blocking follow-up;
- `minor`: small cleanup.

Set `result` to `no-go` when any blocker exists or any acceptance criterion is
`fail`; otherwise set `go`. Validate:

```bash
python3 scripts/changerail_review_verdict.py validate \
  ".runtime/changerail/reviews/<card-id>.json" --json
```

When the workspace provides a review-cycle history contract, append or update a
runtime history summary for the cycle without editing the reviewed payload. Keep
previous `no-go` cycles available for metrics even after a later `go`.

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
- exact next command (`$changerail-pub <card-path>` on `go`, otherwise the fix list).
