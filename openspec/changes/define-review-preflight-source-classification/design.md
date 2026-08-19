## Context

`scripts/changerail_review_preflight.py` currently decides production source
from a hard-coded suffix set plus generic non-production path exclusions. That
works for common code files but leaves domain-specific source formats out of the
complexity guard unless ChangeRail core hard-codes each domain. The 1C case
needs `.bsl` modules and Designer XML metadata to be counted only when a
consumer explicitly classifies them as production source.

## Goals / Non-Goals

**Goals:**
- Add one deterministic, tracked, consumer-owned source-classification input
  for review preflight.
- Validate repository-relative roots and source-kind rules fail-closed.
- Preserve the existing default classifier when no source-classification file is
  present.
- Expose a source-kind breakdown in `changerail.review-preflight-result.v1`.

**Non-Goals:**
- Parse or validate language semantics for BSL or Designer XML.
- Add real 1C exports, configuration names or customer data to ChangeRail core.
- Let projects use prose in `AGENTS.md` or card text as a machine override.
- Relax published-investigation authorization or review independence gates.

## Decisions

1. Use `.changerail/source-classification.yaml` as the default tracked
   consumer-owned source of truth.

   The file uses schema id `changerail.source-classification.v1`. It contains
   repository-relative production root rules and optional additional
   non-production roots. Root paths are literal path prefixes, not arbitrary
   shell globs, so matching is deterministic and safe to validate. Missing file
   means legacy behavior; malformed file blocks preflight with a structured
   check failure.

2. Model classification as source kinds, not domain names.

   A rule declares an id such as `bsl` or `designer-xml`, suffixes, production
   roots and a measure strategy. ChangeRail core owns generic validation and
   measurement behavior; consumers own which repository paths are production.
   Generic non-production parts such as `test`, `tests`, `fixtures`,
   `examples`, `schemas`, `templates`, `docs` and `openspec` continue to win
   unless a future explicit contract changes that rule.

3. Keep the aggregate guard field and add breakdown detail.

   `added_production_loc` remains the aggregate guard value for compatibility
   with existing investigation authorization. New `source_breakdown` entries
   explain each counted kind with paths, raw added lines, effective complexity
   units and measure strategy. Existing code kinds can report `builtin` source
   kind until specialized rules are declared.

4. Bootstrap templates document the optional file without generating
   domain-specific defaults.

   `bootstrap-project` may render a commented or empty public-safe placeholder,
   but it must not guess production roots for a consumer. Projects opt in by
   committing their own classification.

## Risks / Trade-offs

- [Consumer misclassifies production as non-production] -> Missing or narrow
  config cannot be solved generically; docs require conservative declarations,
  and investigation remains available for suspicious payloads.
- [Malformed config creates false green] -> Schema and semantic validation
  block preflight rather than ignoring invalid rules.
- [Path matching becomes too broad] -> Rules use normalized repository-relative
  prefixes and reject absolute paths, traversal and root escape.
- [Result schema churn] -> Keep existing aggregate fields and add bounded
  structured detail rather than replacing the public result shape wholesale.

## Migration Plan

1. Add schema-backed loader and semantic path validation.
2. Add `source_breakdown` to preflight results and schema smoke fixtures.
3. Document the optional file in contract docs and generated consumer guidance.
4. Add focused temporary-repository smoke coverage for missing, valid and
   invalid classification.

## Open Questions

- none
