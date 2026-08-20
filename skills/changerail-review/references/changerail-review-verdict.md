# ChangeRail Review Verdict

For card-level ChangeRail runs, the independent review phase records its outcome in
ignored runtime state:

```text
.runtime/changerail/reviews/<card-id>.json
```

Use the board card filename without `.md` as `<card-id>`. The canonical verdict
schema id is:

```text
changerail.review-verdict.v1
```

The verdict is the machine gate between `$changerail-do` and `$changerail-pub`. A publish
that is part of the review-gated flow must not proceed without a verdict that
is valid, `result: go`, and fresh against the current working tree. Never
commit the verdict file; record the summary in the card `Log` instead.

Review-cycle history may be retained as separate ignored runtime evidence:

```text
.runtime/changerail/reviews/<card-id>.history.json
```

This history does not replace the canonical verdict. Publish validates only the
latest `.runtime/changerail/reviews/<card-id>.json` verdict.

Before launching an ordinary or critical reviewer, the orchestrator runs
`bin/changerail-review-verdict preflight <card> --workspace . --normalize
--json`. A schema-valid `machine-reviewed` preflight result is the payload gate
for an explicitly deterministic/process card with no added production code.
Ordinary and critical cards still require this independent verdict; process
preflight failures never become verdict findings or review cycles.

During an active parent delivery run, `CHANGERAIL_ACTIVE_RUN_DIR` identifies
parent-owned runtime evidence that is write-only from the child review
perspective. A reviewer must not read, search, tail, cite or summarize files in
that directory, including raw runtime logs such as `stdout.jsonl` and
`stderr.log`. The review must use the card, manifest, preflight, reviewed tree
and retained card-owned evidence outside the active run directory. Evidence
available only in the protected directory remains unbacked until the parent run
terminates and exposes it through an allowed handoff.

## Producing And Validating

Only a fresh reviewer context may write a verdict. The implementing session
must never write its own verdict.

Each verdict MUST include an independence attestation:

```json
"reviewer": {
  "kind": "codex-exec",
  "session": "optional session id",
  "model": "optional model id",
  "independence": {
    "fresh_context": true,
    "did_not_plan_or_implement": true,
    "basis": "fresh reviewer session launched only for this review"
  }
}
```

The validator checks that `fresh_context` and `did_not_plan_or_implement` are
true and that `basis` is non-empty. This is a machine-checkable attestation and
freshness gate, not proof of real-world identity or full memory isolation.

Validate a verdict with the local helper:

```bash
bin/changerail-review-verdict validate \
  ".runtime/changerail/reviews/<card-id>.json" --json
```

Consumer projects may invoke the same helper through a linked wrapper:

```bash
bin/changerail-review-verdict validate \
  ".runtime/changerail/reviews/<card-id>.json" --json
```

Exit codes: `0` valid, `1` validation failed, `2` input error. Consumers must
fail closed on any non-zero exit.

Validation first enforces the tracked Draft 2020-12 schema
`schemas/changerail-review-verdict.schema.json`, including date-time formats,
unknown-field rejection and nested field types. After schema validation, the
helper applies ChangeRail semantic rules such as `go`/finding consistency and
freshness.

## Freshness Fingerprint

A verdict certifies one exact working-tree state. Compute the fingerprint with:

```bash
bin/changerail-review-verdict fingerprint --workspace <repo-root>
```

The helper hashes `git status --porcelain`, `git diff HEAD --no-color`, and the
deterministic list and contents of untracked non-ignored files from
`git ls-files --others --exclude-standard`. It also computes
`workspace.tree_sha`, the Git tree that would be committed for the reviewed
working tree, through a temporary Git index without touching the real staging
area. In an unborn repository, `workspace.head_commit` is `unborn` and
`workspace.tree_sha` still identifies the reviewed initial tree.

Current helpers derive changed paths from NUL-delimited Git status, build the
reviewed tree from `HEAD` plus the exact changed-path set on the safe happy
path, and retain a full-tree `git add -A` reference/fallback for unsafe states
and parity tests. `--diagnostics` reports public-safe timing, tree-builder mode
and cache hit/miss data. Preflight and verdict validation may reuse an ignored
`.runtime/changerail/review-fingerprint-cache/` entry only after current HEAD,
changed-path metadata, path content/mode metadata and Git exclude-visible state
match the cached payload.

Ignored runtime state does not affect the fingerprint or reviewed tree, so
writing the verdict file itself does not invalidate it. Reviewers must still
read newly added files as defense-in-depth; the fingerprint and tree only prove
that the reviewed bytes have not changed since the verdict was written. Publish
must fail closed if the current tree or fingerprint differs from the verdict.

## Semantics

- `result: go`: publish may proceed. No blocker findings and no failed
  acceptance criteria may be present.
- `result: no-go`: publish is blocked and must be justified by at least one
  blocker finding or failed acceptance criterion.
- `acceptance`: one entry per card acceptance criterion, each backed by a
  concrete command, retained evidence path/reference or explicit unverifiable
  reason.
- `evidence_refs`: optional structured references on acceptance entries or
  findings, using evidence id, index path and raw output path from retained
  ignored runtime evidence such as `bin/changerail-evidence` output.
- `findings[].severity`: `blocker` blocks publish; `major` and `minor` require
  follow-up when not fixed.
- `review_cycle`: `1` for the first review, incremented after fix cycles.
- The helper accepts only `changerail.review-verdict.v1`.
- Review-cycle history retains prior cycle finding details or immutable verdict
  snapshot paths for metrics and audit after a later cycle writes the latest
  canonical `go` verdict.

When available, review-cycle history also records same-card rescue budget state:

- `rescue_budget.limit`: configured same-card rescue attempt limit.
- `rescue_budget.used`: consumed post-review same-card rescue attempts.
- `rescue_budget.remaining`: attempts still available before linked rescue or
  investigation policy takes over.
- `rescue_budget.exhausted`: whether autonomous same-card rescue is exhausted.
- `cycles[].same_card_rescue_attempt`: consumed same-card rescue attempts before
  that review; the first independent review is `0`.

Legacy history without these optional fields remains readable as `unknown`.
