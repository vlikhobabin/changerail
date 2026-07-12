## Context

Current CI uses a manually curated `py_compile` list and a string-based release
workflow smoke. Since the runner, metrics and fingerprint surfaces were added,
that list no longer represents the full tracked Python surface. The repository
also has schema-backed helper validation, but release CI does not yet exercise
every public schema file as a release contract.

## Goals / Non-Goals

**Goals:**
- Make CI discover tracked executable Python helpers and smoke scripts from git
  inventory instead of a stale list.
- Add a pinned lint gate for `bin` and `scripts`.
- Run all focused ChangeRail smoke scripts that protect release-facing helper,
  schema, runner, metrics, manifest, review and drift behavior.
- Validate every public contract schema with Draft 2020-12 meta-schema checks
  and fixture-backed positive/negative validation.

**Non-Goals:**
- Add a packaging/build system for ChangeRail.
- Replace existing smoke scripts with a test framework.
- Make `scripts/smoke-drift.py` no-argument self-contained; it remains
  inventory-driven and is invoked with a generated fixture by CI.

## Decisions

- Use a tracked discovery script for Python syntax coverage. It should collect
  executable helpers under `bin/` and Python scripts under `scripts/` from
  `git ls-files`, then call `py_compile` on those exact paths.
- Add `requirements-dev.txt` for release-gate tool pins. CI and local release
  baseline install from this file before running `ruff` and schema validation.
- Keep `ruff check bin scripts` as the lint command named in public docs and CI.
  Configuration stays minimal so the gate catches obvious import/dead-code
  drift without broad style churn.
- Add a schema smoke that imports the same helper validation modules used by
  runtime CLIs and validates positive/negative fixtures for all five public
  schemas.
- Convert `scripts/smoke-release-ci.py` from substring-only checks to an
  inventory check that asserts required commands and workflow structure.

## Risks / Trade-offs

- Pinned dev dependencies require network access in GitHub Actions. Mitigation:
  pin direct tool versions and keep the surface small (`jsonschema`, `ruff`).
- Auto-discovered syntax checks can include new scripts before they are ready.
  Mitigation: tracked executable Python files are public release surface, so CI
  should fail early when such files are incomplete.
