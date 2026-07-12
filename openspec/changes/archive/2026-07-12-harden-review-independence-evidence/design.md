## Context

The current helper validates schema consistency and working-tree freshness.
That proves the reviewed bytes did not change, but not that the reviewer was a
different memory/context from the implementer.

## Decisions

- Add a required `reviewer.independence` object to
  `changerail.review-verdict.v1`.
- Require:
  - `fresh_context: true`
  - `did_not_plan_or_implement: true`
  - non-empty `basis`
- Keep `reviewer.session` optional because not every tool exposes a stable
  public-safe session id.
- Document the limit: this is a machine-checkable attestation, not a proof of
  identity.

## Verification

- Update schema and validator together.
- Add smoke coverage for valid attestation and missing/false attestation.
- Run existing review fingerprint smoke.
- Validate OpenSpec and JSON schemas.
