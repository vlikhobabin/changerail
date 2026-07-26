## Context

The current plan contract is intentionally explicit, but a small ordered queue
requires a lot of boilerplate: schema id, workspace array, card array, ids and
optional dependencies. A helper should reduce operator error without creating a
second contract.

## Decisions

- Add `generate-plan` as a non-live command in the existing runner.
- Use `--workspace alias=path` for one or more public-safe workspace aliases.
- Use repeatable `--card path` entries as the ordered list. Card ids derive from
  the file stem after slug sanitization.
- Use `--depends card-id=dep-id[,dep-id]` for optional dependency edges.
- Default all cards to the first workspace unless `--default-workspace` selects
  another declared alias.
- Write JSON to stdout by default, or atomically write to `--output`.
- Validate the generated payload with existing schema validation before
  returning success.

## Public Safety

The helper must reject absolute workspace/card paths and unsafe dependency or
identifier values through the existing schema validation path. It must not read
or write auth files, runtime logs or credentials.
