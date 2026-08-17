## Context

Preflight already parses review declarations and emits a schema-backed result,
but its fixed 300-line/protocol guard cannot consume a prior investigation
decision. The successor card is the only unambiguous place to declare which
published investigation authorizes it.

## Goals / Non-Goals

**Goals:**
- Parse a single inline JSON object from `## Review`.
- Require a successor reference to a clean, `HEAD`-tracked `4.done`
  authorization source. That source owns exact paths and ids for both cards,
  a `4.done` investigation card, `investigation Blocks successor` and
  `successor Depends On investigation` references, a ceiling from 301 through
  500 and an explicit boolean protocol allowance.
- Preserve the default 300-line/protocol investigation stop in every other
  case and retain the validated authorization state in the machine result.

**Non-Goals:**
- Add a CLI waiver, infer authority from prose, launch an LLM or relax the
  independent ordinary/critical review gate.
- Generalize this small exception beyond the explicitly bounded successor.

## Decisions

1. The successor declaration is an inline JSON source reference, not a waiver.

   It contains only the published authorization card path/id. The clean,
   tracked source owns the all-or-nothing decision object, preventing a
   successor from self-authorizing a higher ceiling or protocol.

2. Validation follows both links before altering complexity behavior.

   The source and investigation must be unchanged, tracked `HEAD` artifacts.
   The current card must have `## Depends On` with the investigation id; the
   investigation must have `## Blocks` with the current card id; and the source
   must depend on that investigation. A valid object may raise the production
   ceiling only up to 500 and permit protocol only when its boolean allowance
   is true.

3. Go test classification is path-specific.

   `*_test.go` is excluded while other `.go` files retain normal production
   accounting. Existing generic test directory/name exclusions remain intact.

## Risks / Trade-offs

- An investigation card might contain a superficial reference -> exact
  backticked ids in the required headings and unchanged `HEAD` artifacts are
  required.
- A card may declare a large ceiling -> schema and semantic validation cap it
  at 500.
- The one-line JSON is less friendly than prose -> templates and contract docs
  publish its exact fields, while machine validation remains deterministic.

## Migration Plan

1. Extend parser, schema and smoke fixtures.
2. Update the targeted public contract, methodology and templates.
3. Run focused smoke, schema smoke, strict OpenSpec, lint/compile and release
   baseline before the independent ordinary `high` review.

## Open Questions

- none
