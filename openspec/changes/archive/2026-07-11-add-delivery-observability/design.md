## Context

The review verdict helper validates only the latest canonical verdict required
by publish. Operations need additional retained history so metrics can answer
whether a card passed first review, how many findings occurred and how long runs
took. That history must remain runtime state unless a project explicitly
commits curated evidence.

## Goals / Non-Goals

**Goals:**
- Preserve review-cycle history separately from the canonical latest verdict.
- Add a metrics helper that reads run records and review evidence.
- Support text and CSV output with explicit unknown values.
- Document the scoped rescue loop from over-claim through no-go to re-review.

**Non-Goals:**
- Do not make runtime logs part of publish scope.
- Do not change the canonical `opsx.review-verdict.v1` gate.
- Do not infer metrics from free-text logs.

## Decisions

- Keep canonical latest verdict at `.runtime/opsx/reviews/<card-id>.json`.
  - Rationale: publish freshness behavior remains unchanged.
  - Alternative considered: make publish read a history file. That would
    expand the critical path unnecessarily.
- Store review cycle history under ignored runtime state.
  - Rationale: it preserves no-go cycles for metrics without committing runtime
    payloads.
- Implement metrics as a dependency-free Python helper.
  - Rationale: it can read JSON records and emit CSV without external packages.

## Risks / Trade-offs

- Older runs may lack new fields -> metrics must print `unknown` instead of
  inventing values.
- Review history may be absent for externally managed reviews -> aggregate
  output should count the run and mark review data unavailable.
