## Context

The OPSX source model treats `openspec-*` action skills as reusable lifecycle
building blocks. The skills originate from the OpenSpec CLI skill set generated
for OpenSpec CLI `1.3.0` and are licensed MIT. OPSX needs to preserve that
provenance and define how future updates are synced.

## Goals / Non-Goals

**Goals:**
- Ship public source files for the OpenSpec action skills used by OPSX.
- Provide a wrapper that pins the CLI version and runs from the invoking
  project root.
- Document source, license, compatibility and sync policy.

**Non-Goals:**
- Fork the OpenSpec CLI implementation.
- Add bootstrap or consumer verification checks.
- Guarantee compatibility with future OpenSpec versions without an explicit
  update and smoke pass.

## Decisions

1. The initial skill set is copied from the OpenSpec generated skill source and
   kept under `skills/openspec-*` with its existing MIT/provenance metadata.
2. `bin/openspec` uses `npx -y @fission-ai/openspec@1.3.0` by default,
   disables telemetry unless the operator overrides it and allows
   `OPENSPEC_VERSION` for controlled local testing.
3. Compatibility notes live in `docs/openspec-lifecycle.md`; future changes to
   generated OpenSpec skills require updating that document and re-running the
   repository verification baseline.

## Risks / Trade-offs

- A pinned wrapper can lag upstream. Mitigation: record the pin and require a
  deliberate update with compatibility notes.
- Generated skill text can drift from CLI behavior. Mitigation: preserve
  provenance metadata and document that generated skills are synced from the
  OpenSpec CLI release they name.
