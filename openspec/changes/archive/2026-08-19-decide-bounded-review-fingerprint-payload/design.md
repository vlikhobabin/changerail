## Context

The canceled review-fingerprint delivery produced useful implementation
evidence but was stopped correctly before independent review. The retained
local checkpoint is not a review artifact; its public-safe diff summary is
read-only input for deciding a smaller replacement boundary. The public card sequence now separates the work
into investigation, authorization publication and bounded delivery so the
successor can pass deterministic preflight without raising the global
production-LOC limit.

The retained diff shows the production-counted overrun in three files:

- `scripts/changerail_review_verdict.py`: 489 added lines.
- `scripts/changerail_review_preflight.py`: 36 added lines.
- `scripts/run-release-baseline.py`: 2 added lines.

The same diff also added focused smoke coverage outside the production LOC
count: `scripts/smoke-review-fingerprint-benchmark.py`,
`scripts/smoke-review-fingerprint-cache.py`,
`scripts/smoke-review-fingerprint.py` and `scripts/smoke-review-preflight.py`.

## Goals / Non-Goals

**Goals:**

- Publish a public-safe investigation decision that explains why the first
  payload measured 527 production LOC.
- Identify a concrete simplification boundary that keeps the exact same
  review-fingerprint correctness expectations.
- Authorize only the exact successor
  `deliver-bounded-review-fingerprint-optimization` at a ceiling of 500 added
  production LOC.
- Preserve focused verification for edge-path parity, untracked content
  hashing, cache invalidation and synthetic benchmark behavior.

**Non-Goals:**

- Implement the optimized fingerprint helper in this investigation change.
- Raise the global 300 production-LOC ordinary limit.
- Authorize more than 500 added production LOC.
- Treat the retained local checkpoint as reviewed or publishable.
- Remove edge-path parity or cache invalidation tests to satisfy the ceiling.

## Decisions

1. The investigation decision is a tracked board/OpenSpec artifact, not a code
   change. This keeps the review surface limited to public-safe reasoning and
   enables the later authorization card to publish the machine-readable
   allowance.

2. The bounded successor keeps the three existing implementation changes instead
   of splitting into a new broad series. The retained overrun is not caused by
   story scope drift; it is caused by over-expanded helper implementation and
   duplicated smoke scaffolding within the same accepted scope.

3. The replacement implementation should reduce production LOC by consolidating
   helper abstractions:
   - reuse a single small timing collector or plain timing helper across
     fingerprint and preflight instead of two local classes;
   - avoid extra dataclass layers unless they remove more code than they add;
   - keep cache metadata minimal and validate it through the existing
     fingerprint fields plus changed-state metadata;
   - keep diagnostics opt-in and avoid expanding the default public JSON
     contract beyond required fields.

4. Focused smoke coverage should be compacted, not weakened:
   - combine benchmark and cache fixtures where practical so repository setup
     helpers are shared;
   - keep parity cases for add, modify, delete, rename, symlink, Unicode,
     spaces, literal arrow and valid non-UTF-8 Linux paths;
   - keep invalidation cases for tracked modification, deletion, rename,
     untracked content and exclude-state changes.

5. The replacement ceiling remains 500 added production LOC. The target is not
   to fit under the ordinary 300 limit by deleting meaningful behavior; it is to
   demonstrate that the accepted review-fingerprint scope can be delivered below
   the existing bounded investigation maximum.

## Risks / Trade-offs

- Bounded LOC pressure could encourage under-tested helper shortcuts.
  Mitigation: the successor keeps exact parity, untracked hashing, cache
  invalidation and benchmark smoke acceptance as mandatory verification.
- Consolidating helper code could obscure failure diagnostics. Mitigation:
  require fail-closed cache/recompute behavior and public-safe diagnostics for
  tree builder, cache event and timing phases.
- Using the retained checkpoint as evidence could accidentally legitimize
  unreviewed code. Mitigation: card text and tasks state that only its
  public-safe diff summary informs the investigation; the code is not published
  or counted as review evidence.
