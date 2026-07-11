# OPSX Review Verdict

For card-level OPSX runs, the independent review phase records its outcome in
ignored runtime state:

```text
.runtime/opsx/reviews/<card-id>.json
```

Use the board card filename without `.md` as `<card-id>`. The canonical verdict
schema id is:

```text
opsx.review-verdict.v1
```

The verdict is the machine gate between `$opsx-do` and `$opsx-pub`. A publish
that is part of the review-gated flow must not proceed without a verdict that
is valid, `result: go`, and fresh against the current working tree. Never
commit the verdict file; record the summary in the card `Log` instead.

Review-cycle history may be retained as separate ignored runtime evidence:

```text
.runtime/opsx/reviews/<card-id>.history.json
```

This history does not replace the canonical verdict. Publish validates only the
latest `.runtime/opsx/reviews/<card-id>.json` verdict.

## Producing And Validating

Only a fresh reviewer context may write a verdict. The implementing session
must never write its own verdict.

Validate a verdict with the local helper:

```bash
python3 scripts/opsx_review_verdict.py validate \
  ".runtime/opsx/reviews/<card-id>.json" --json
```

Consumer projects may invoke the same helper through a linked wrapper:

```bash
bin/opsx-review-verdict validate \
  ".runtime/opsx/reviews/<card-id>.json" --json
```

Exit codes: `0` valid, `1` validation failed, `2` input error. Consumers must
fail closed on any non-zero exit.

## Freshness Fingerprint

A verdict certifies one exact working-tree state. Compute the fingerprint with:

```bash
python3 scripts/opsx_review_verdict.py fingerprint --workspace <repo-root>
```

The helper hashes `git status --porcelain`, `git diff HEAD --no-color`, and the
deterministic list and contents of untracked non-ignored files from
`git ls-files --others --exclude-standard`. Ignored runtime state does not
affect the fingerprint, so writing the verdict file itself does not invalidate
it. Reviewers must still read newly added files as defense-in-depth; the
fingerprint only proves that the reviewed bytes have not changed since the
verdict was written.

## Semantics

- `result: go`: publish may proceed. No blocker findings and no failed
  acceptance criteria may be present.
- `result: no-go`: publish is blocked and must be justified by at least one
  blocker finding or failed acceptance criterion.
- `acceptance`: one entry per card acceptance criterion, each backed by a
  concrete command, retained evidence path or explicit unverifiable reason.
- `findings[].severity`: `blocker` blocks publish; `major` and `minor` require
  follow-up when not fixed.
- `review_cycle`: `1` for the first review, incremented after fix cycles.
- The helper accepts only `opsx.review-verdict.v1`.
- Review-cycle history retains prior cycle finding details or immutable verdict
  snapshot paths for metrics and audit after a later cycle writes the latest
  canonical `go` verdict.
