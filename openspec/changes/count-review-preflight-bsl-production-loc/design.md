## Context

The existing preflight production classifier counts common source suffixes and
executable helpers, then subtracts generic non-production paths. `.bsl` is not
in the built-in set, so a synthetic consumer can add more than 300 BSL lines
under a production source tree and still get `added_production_loc = 0`.

This change depends on `define-review-preflight-source-classification` so BSL is
declared by a consumer-owned root rather than globally counted in every
repository.

## Goals / Non-Goals

**Goals:**
- Count `.bsl` added lines for paths classified as production BSL source.
- Preserve non-production exclusions for tests, fixtures and examples.
- Add a focused smoke that first demonstrates the current false-negative, then
  proves the fixed behavior with synthetic temporary files.
- Preserve existing behavior for Python, Go, JavaScript and executable helpers.

**Non-Goals:**
- Parse BSL syntax or validate 1C modules.
- Add global `.bsl` production behavior without a declared production root.
- Store real 1C modules or client data in tracked fixtures.

## Decisions

1. BSL uses the `lines` measure strategy.

   For `.bsl`, effective complexity equals added text lines in the same way
   common source suffixes are counted today. That makes the guard comparable to
   existing `production_loc_ceiling` semantics.

2. Declared production classification is required.

   `.bsl` outside declared production roots remains non-production unless a
   future contract changes the default. Existing path parts such as `test`,
   `tests`, `fixtures` and `examples` remain exclusions even when a broad root
   is declared.

3. Smoke coverage uses temporary synthetic repositories.

   The smoke should create a temporary consumer, commit baseline files, add
   synthetic `.bsl` files under production and non-production paths, derive a
   manifest and run preflight. No tracked BSL fixture content is needed.

## Risks / Trade-offs

- [Projects forget to declare BSL roots] -> Preflight will keep legacy behavior;
  docs and template guidance make the opt-in explicit.
- [A broad production root captures examples] -> Non-production exclusions win
  and focused smoke proves that behavior.
- [False RED setup becomes brittle] -> The smoke should isolate the current
  false-negative assertion in a small helper path or test mode rather than
  relying on real consumer state.

## Migration Plan

1. Implement BSL suffix handling through the source-classification loader.
2. Add RED/GREEN synthetic smoke cases for production and non-production BSL.
3. Update contract docs and validation fixtures as needed.

## Open Questions

- none
