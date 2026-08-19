## Context

The current review fingerprint helper computes an exact reviewed tree by
creating a temporary index, reading HEAD into it and running `git add -A` for
the entire repository. On large generated-source repositories this can dominate
review preflight even when the actual payload touches only docs. Preflight also
runs OpenSpec validation, scoped whitespace checks and public-surface scans, so
operators need timing data that separates Git tree construction from the rest
of the gate.

## Goals / Non-Goals

Goals:
- Measure each deterministic preflight phase separately with stable labels.
- Add a synthetic large-repository benchmark for docs-only and source payloads.
- Make benchmark output public-safe and compact enough for retained evidence.
- Preserve all existing freshness semantics and validation outcomes.

Non-Goals:
- Replace the reviewed-tree construction algorithm.
- Add cache reuse.
- Store private consumer repository paths, logs or generated-source contents.

## Decisions

1. Add an internal timing collector that records monotonic durations for named
   phases and emits them only in benchmark/preflight diagnostic contexts. The
   existing `fingerprint` JSON output remains backward compatible unless an
   explicit diagnostics flag is supplied.
2. Use generic synthetic repositories under temporary directories. The fixture
   should parameterize tracked file count, generated-source file size and
   payload type, but default to a size small enough for CI and large enough to
   catch a full-index refresh regression.
3. Measure at least:
   - Git status and changed path discovery;
   - temporary index load and reviewed-tree write;
   - untracked non-ignored enumeration and content hashing;
   - OpenSpec strict validation;
   - scoped `git diff-tree --check`;
   - public-surface scan.
4. Report before/after-style data as JSON plus a concise human line so both
   agents and maintainers can use the same evidence.
5. Set thresholds from the measured baseline in the synthetic fixture, not from
   private field-validation timings.

## Verification

- Add smoke coverage that proves timing records include all expected phase
  labels for docs-only and source payloads.
- Add or extend a benchmark smoke that fails if the synthetic docs-only
  baseline cannot distinguish full-tree setup cost from changed-scope work.
- Run existing review fingerprint and review preflight smoke.
- Run strict OpenSpec validation and whitespace checks.
