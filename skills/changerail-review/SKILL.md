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

When `CHANGERAIL_PROGRESS_EVENT_PATH` is set, emit value-free review progress
with `bin/changerail-delivery-runner progress-event review waiting` before
payload audit and `review complete` after verdict validation. Progress events
must use only the helper's bounded phase/stage contract and must not include
prose, commands, paths, environment values or output excerpts.

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

## Parent-Owned Active Runner Evidence

When `CHANGERAIL_ACTIVE_RUN_DIR` is set, that directory belongs to the parent
delivery runner until the child exits. Do not read, search, tail, cite or
summarize files under `CHANGERAIL_ACTIVE_RUN_DIR` while the parent run is
active. This includes `status.json`, `stdout.jsonl`, `stderr.log` and any other
file created inside that directory. Exclude the directory from broad workspace
discovery commands.

Review the card, manifest, preflight, tracked payload and retained card-owned
evidence outside the protected active-run directory. If a mandatory claim is
backed only by protected active-run output, record it as unbacked instead of
reading the raw log. The parent orchestrator may inspect the structured run
status and may expose retained evidence after the child terminates.

## Shared Review Verdict

Read `references/changerail-review-verdict.md` before writing a verdict. The verdict
path is:

```text
.runtime/changerail/reviews/<card-id>.json
```

The canonical schema id is `changerail.review-verdict.v1`. Use the linked
`bin/changerail-review-verdict` helper when present; otherwise use
`bin/changerail-python scripts/changerail_review_verdict.py` to compute and
validate verdicts through the shared Python runtime selector.

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
When the history contract supports rescue budget fields, retain
`rescue_budget.limit`, `rescue_budget.used`, `rescue_budget.remaining` and
`rescue_budget.exhausted`. The first independent review is `review_cycle: 1` and
`same_card_rescue_attempt: 0` when known; re-reviews after scoped same-card fixes
increment `review_cycle` and record the consumed same-card rescue attempt.

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

### 1. Require Deterministic Preflight

The orchestrator must run this before launching the reviewer context:

```bash
bin/changerail-review-verdict preflight "<card-path>" --workspace . \
  --normalize --output ".runtime/changerail/review-preflights/<card-id>.json" --json
```

The fresh reviewer reads that ignored result and may rerun preflight without
`--normalize`. Stop before payload analysis when it returns `blocked` or
`investigation-required`; those are process/complexity outcomes, not review
findings and do not increment `review_cycle`. Return immediately without an LLM
verdict on `machine-reviewed`. For `ready-for-llm-review`, use `high` for
ordinary risk and `xhigh` only for critical credential, mutation-authority,
live-admission or final-certification scope. Risk understatement is a blocker.

### 2. Resolve Scope And Fingerprint

Run:

```bash
git status --short
git diff HEAD --stat
openspec list --json
bin/changerail-review-verdict fingerprint --workspace .
```

Read the card and delivery manifest. Confirm card-owned changes are archived.
If a manifest exists, treat `committable_paths` as the claimed publish scope;
otherwise reconstruct scope from the card, archives and `git status`.
When the manifest helper supports `scope-check`, run the working-tree check and
treat missing, extra or mismatched committable paths as scope findings:

```bash
bin/changerail-delivery-manifest scope-check \
  ".runtime/changerail/delivery-manifests/<card-id>.json" \
  --target working-tree --json
```

Do not update the manifest from the reviewer context. Review writes only the
canonical verdict and optional ignored review-cycle history; orchestrator or
publish handoff may copy concise review summary data into the manifest after
the verdict is validated.

### 3. Evidence Audit

For every verification claim in the card, archived tasks and manifest:

- identify the command that allegedly ran;
- identify the retained output, evidence path or observed output summary;
- when the project declares `.changerail/execution-target.json`, confirm the
  current declaration, manifest and retained evidence have one exact matching
  target identity;
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

### 4. Diff Review

Read the full working-tree diff for the claimed publish scope:

```bash
git diff HEAD -- <committable paths>
```

Also inspect untracked committable files listed by `git status --short`. Check
correctness against the card, scope boundaries, tests, docs, schemas, error
handling and public-safety risks.

### 5. Test Adequacy Critique

For added or changed tests, answer whether they would fail if the behavior were
broken. Flag missing coverage, tautological assertions, weakened tests and
missing RED evidence where the project required test-first work. Treat an
explicit docs-only/config-only RED-not-applicable note as evidence to audit,
not as an automatic failure.

### 6. Write And Validate Verdict

Assign findings `R1..Rn`:

- `blocker`: publish would ship a defect, missing mandatory evidence, failed
  acceptance or out-of-scope change;
- `major`: important but non-blocking follow-up;
- `minor`: small cleanup.

Set `result` to `no-go` when any blocker exists or any acceptance criterion is
`fail`; otherwise set `go`. Validate:

```bash
bin/changerail-review-verdict validate \
  ".runtime/changerail/reviews/<card-id>.json" --json
```

When the workspace provides a review-cycle history contract, append or update a
runtime history summary for the cycle without editing the reviewed payload. Keep
previous `no-go` cycles available for metrics even after a later `go`.
Keep planning, delivery-fix, implementation-review and live-admission counters
separate when `phase_counters` is supported. A focused re-review may reuse
unchanged full-suite evidence only when it is bound to the same payload hash;
the full suite is rerun before live admission or final publish. Perform at most
one extra clean-HEAD LLM audit, and only at a card-declared milestone.

## Safety Stops

Stop without writing a verdict when:

- this session implemented or planned the card;
- deterministic preflight is absent, blocked or requires investigation;
- declared execution target identity is missing, mismatched, substituted or
  backed by multiple retained evidence targets;
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
