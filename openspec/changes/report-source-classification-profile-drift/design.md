## Context

After materialization, final classification may be manually edited, built-in
profile data may drift without version bump, or new likely sources may appear
outside effective rules. Existing preflight validates only final file and counts
classified paths; it cannot explain profile baseline, intentional overrides or
uncovered likely source. Detection remains advisory and must not mutate risk.

## Goals / Non-Goals

**Goals:**

- Add schema-backed `check` report for provenance, effective rules and drift.
- Distinguish declared project overrides from undeclared divergence.
- Report bounded uncovered-source signals with confidence/severity semantics.
- Integrate confirmed blocking drift into project verification/preflight.
- Document explicit detect/review/materialize/check lifecycle and migration.

**Non-Goals:**

- Не auto-update profile/classification or Git.
- Не block solely on an unaccepted low/high-confidence candidate.
- Не copy source contents, raw XML/BSL or machine paths into reports.
- Не reinterpret final rules during current risk calculation.

## Decisions

1. **`check` is read-only and source-explicit.** It validates final file,
   provenance and built-in profiles. Local integration profile may be supplied
   explicitly again; without it, checksum baseline is `unavailable`, not
   guessed from machine path. Report schema is
   `changerail.source-classification-check.v1`.

2. **Effective policy remains final project file.** Report first lists profile
   baseline, then applies only provenance-declared override paths to explain
   final effective rules. Undeclared difference is `confirmed_profile_drift`.
   Check never substitutes recomputed profile rules into review preflight.

3. **Severity depends on authority.** Invalid file/schema, changed built-in
   content at same id/version/checksum, incompatible supplied local profile,
   undeclared difference or measure conflict is blocking. Detection-only
   uncovered candidate is advisory (`low` or `high` confidence), because it was
   never accepted as policy. A confirmed selected profile whose expected rule
   no longer covers its matching source is blocking.

4. **Uncovered scan is bounded and value-free.** Reuse HEAD/snapshot path
   enumeration and profile signals. Report aggregates counts by suffix/root/
   source kind and caps normalized path examples. It excludes source bodies,
   file hashes tied to content, raw XML and output from external tools.

5. **Preflight separates diagnostic from calculation.** It calculates
   `added_production_loc` only from validated final classification as today.
   Then it consumes/checks report: blocking confirmed drift fails process gate;
   advisory candidate appears in diagnostics and cannot add LOC or change risk.

6. **Migration is an explicit future/operator action.** `check` produces
   semantic diff and recommended `detect -> review -> materialize/check` action,
   but materialize still refuses overwrite. A separate reviewed migration edit
   updates project file/provenance; no `--force` is introduced.

## Risks / Trade-offs

- [Local profile unavailable on another machine] -> provenance remains
  checkable by checksum, baseline comparison is unavailable/advisory unless
  project/integration supplies profile explicitly.
- [Uncovered path examples reveal names] -> only normalized repository paths,
  capped; no external/machine paths or content.
- [Manual override declared too broadly] -> override paths target exact fields,
  not wildcard sections.
- [Preflight cost grows] -> bounded HEAD path scan, no content parsing/network.

## Migration Plan

1. Add check-report schema and helper subcommand.
2. Implement baseline/override/drift and bounded uncovered diagnostics.
3. Integrate blocking/advisory results into project verification/preflight.
4. Update templates/docs and synthetic mixed/conflict fixtures.
5. Rollback removes diagnostics; final classification remains effective.

## Open Questions

- none
