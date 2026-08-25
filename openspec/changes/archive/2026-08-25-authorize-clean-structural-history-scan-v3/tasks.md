## 1. Exact Authorization Source

- [x] 1.1 Keep exactly one six-field `Investigation authorization` object on
  the board source with the fixed decision/successor identities, ceiling `350`
  and protocol allowance `false`.
- [x] 1.2 Preserve reciprocal decision/authorization/future-successor lineage,
  the exact future two-field reference, `<=349` future-H budget and H-only
  ownership without creating successor card/code.

## 2. Release-CI Contract

- [x] 2.1 Add and synchronize the `changerail-release-ci` requirement for the
  clean v3 authorization source, its fail-closed mismatch behavior and
  docs-only scope.

## 3. Documentation Verification And Handoff

- [x] 3.1 Run strict target, `changerail-release-ci` and all OpenSpec
  validation, then JSON/TOML parsing and exact authorization/lineage/future
  reference assertions.
- [x] 3.2 Run current-only public-surface scan, source classification,
  whitespace and delivery-manifest scope checks; do not run reachable-history,
  full, live or successor work.
- [x] 3.3 Run normalized ordinary/high preflight, archive only after the
  docs-only checks pass, and leave the card in `3.inprogress` for independent
  review without running review, commit or push.
