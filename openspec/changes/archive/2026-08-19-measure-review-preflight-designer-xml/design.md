## Context

Designer XML is not safe to classify by suffix alone. A repository can contain
XML schemas, templates, examples, fixtures and documents that are not
production source. At the same time, Designer XML exports can be verbose enough
that raw added line count overstates review complexity for a single structural
metadata change and can exceed the current bounded authorization maximum.

This change depends on `define-review-preflight-source-classification` for
production proof and can compose with `count-review-preflight-bsl-production-loc`
for mixed 1C payloads.

## Goals / Non-Goals

**Goals:**
- Count Designer XML only through declared production source classification.
- Use a structural XML measure for Designer XML rather than unconditional raw
  XML line count.
- Fall back fail-closed when XML cannot be measured safely.
- Report BSL, Designer XML and mixed payload source-kind detail.
- Preserve bounded investigation authorization and exact successor binding.

**Non-Goals:**
- Validate 1C metadata correctness or parse every Designer semantic object.
- Treat generic `.xml` as production source by suffix.
- Raise the global `production_loc_ceiling` above the existing bounded maximum.
- Store real Designer exports as fixtures.

## Decisions

1. Designer XML uses a dedicated `xml-structure` measure strategy.

   For newly added classified Designer XML files, the helper parses the XML and
   counts effective structural units from element nodes and non-empty scalar
   text values while ignoring comments and whitespace-only formatting. For
   modified files, implementation may use a conservative diff-aware structural
   count; if it cannot prove a lower structural count, it falls back to raw
   added lines and records that fallback in the breakdown.

2. Classification proof is mandatory.

   `.xml` files contribute only when a valid source-classification rule assigns
   them a production source kind with the Designer XML measure strategy. Generic
   XML under schemas, templates, fixtures, docs, examples or OpenSpec remains
   non-production.

3. The existing guard ceiling applies to effective complexity.

   `added_production_loc` remains the aggregate fail-closed guard value, but
   Designer XML contributes effective structural units rather than serializer
   line count when measurement succeeds. Payloads above the default or
   authorized ceiling still require investigation; invalid XML or unsafe
   measurement never produces a zero contribution silently.

4. Breakdown explains raw and effective values.

   Each Designer XML entry records raw added lines, effective complexity,
   measure strategy and whether fallback was used. The result remains bounded
   and public-safe by limiting per-path detail and never copying XML content.

## Risks / Trade-offs

- [Structural units understate semantic risk] -> The metric is only a
  deterministic complexity guard; ordinary or critical semantic review still
  applies, and fallback uses raw lines when proof is weak.
- [Malformed XML hides complexity] -> Classified Designer XML that cannot be
  parsed or conservatively measured blocks or falls back to raw lines rather
  than returning zero.
- [Result grows for large exports] -> Store aggregate and bounded per-kind
  detail with path counts and capped examples.
- [Consumers expect `.xml` suffix to count globally] -> Contract docs state
  classification proof is required.

## Migration Plan

1. Add Designer XML measure handling behind source-classification rules.
2. Extend preflight schema and smoke fixtures for raw/effective breakdown.
3. Add synthetic XML cases for production, generic schema/template/fixture
   exclusions, malformed fallback and mixed BSL/XML payload.
4. Update contract docs with the effective complexity semantics.

## Open Questions

- none
