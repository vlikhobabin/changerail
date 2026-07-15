## Context

`bin/changerail-delivery-runner` currently owns one non-interactive card run and
publishes one `changerail.delivery-run.v1` status record. Multi-workspace queue
supervisors need a durable public contract that can be validated before a
future live queue run, while preserving the existing single-card record.

## Goals / Non-Goals

**Goals:**

- Define schema-backed queue plan and aggregate status contracts.
- Keep queue plans consumer-owned and public-safe.
- Make queue status reference per-card delivery run records instead of replacing
  them.
- Add schema smoke coverage for the new contracts.

**Non-Goals:**

- No YAML dependency is required for the initial contract.
- No change to the existing `changerail.delivery-run.v1` shape is required.
- No private workspace inventory or machine-local plan is committed.

## Decisions

- Use JSON as the required plan format. JSON is already supported by Python's
  standard library and avoids a mandatory runtime dependency; YAML can remain an
  optional future extension.
- Identify workspaces by alias and consumer-root-relative path. This keeps
  public examples generic and makes aggregate status readable without storing
  credentials or operator-specific absolute paths in tracked plans.
- Split plan and status schemas. The plan is a user-authored input contract;
  status is ignored runtime evidence that records fingerprint, state and child
  run references.
- Keep child run records authoritative for card-level execution details. Queue
  status stores references and aggregate outcomes, not a second incompatible
  delivery-run format.

## Risks / Trade-offs

- Schema validation cannot express every DAG invariant alone -> runner semantic
  validation must reject cycles, invalid wave ordering and duplicate references.
- Consumer-root-relative paths require an invocation root -> CLI commands must
  define how `--consumer-root` defaults and how resolved workspaces are reported.
- Public examples can accidentally normalize private paths -> docs and tests
  must use `/opt/example-*` only.

## Migration Plan

Existing single-card runner users continue using `run <card>` and existing
status records. Queue users add a JSON plan and invoke new plan-oriented
commands. No existing runtime record migration is needed.

## Open Questions

- Whether a future optional YAML reader should live in ChangeRail core or in a
  consumer extension remains deferred until JSON support is stable.
