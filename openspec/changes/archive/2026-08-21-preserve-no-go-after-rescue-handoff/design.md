## Context

The fallback currently invokes verdict validation with `--check-fresh` before
examining `result`. This is correct for `go`, because publication must bind to
the exact reviewed tree, but wrong for a final `no-go`: creating the required
tracked rescue card changes the tree after review and turns a truthful negative
verdict into a generic invalid-verdict blocker.

## Decisions

- First validate schema and semantic consistency without freshness.
- Return terminal `NO-GO` immediately for a valid negative verdict. A stale
  negative remains conservative and cannot authorize publication.
- For `go`, run the existing exact workspace freshness validation and keep
  stale/invalid outcomes blocked as `review_verdict_invalid`.
- Extend the existing review-budget smoke so its fake child creates a tracked
  rescue card after writing the final negative verdict.

## Risks / Trade-offs

- [An old negative verdict can conservatively stop a changed payload] -> this
  fails safe and requires a fresh review to proceed; it never authorizes push.
- [Validation is invoked twice for `go`] -> the helper is local and bounded,
  and explicit phase separation is easier to audit than partial parsing.
