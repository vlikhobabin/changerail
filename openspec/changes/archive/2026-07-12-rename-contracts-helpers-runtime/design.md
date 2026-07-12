## Context

ChangeRail publishes machine-readable schemas, helper wrappers, delivery status
records and metrics inputs. These are currently named with the `opsx` namespace.
Contracts are stronger than prose docs: if they keep the old namespace, tooling
and evidence will continue to look like OPSX after the rename.

## Goals / Non-Goals

**Goals:**
- Rename schema ids and schema filenames to `changerail`.
- Rename helper wrappers and internal helper modules.
- Move default runtime paths to `.runtime/changerail`.
- Update validation and smoke tests for the new namespace.

**Non-Goals:**
- Do not support mixed `opsx.*` and `changerail.*` schema ids in the canonical
  validator after the breaking rename.
- Do not migrate old ignored runtime evidence.
- Do not rename OpenSpec CLI artifacts.

## Decisions

1. **Contract ids change at the same time as filenames.**
   A filename-only rename would leave machine-readable evidence semantically
   old. Validators must require `changerail.*`.

2. **Runtime evidence is not migrated.**
   `.runtime/` is ignored local state. Existing evidence can remain historical;
   new runs should write `.runtime/changerail`.

3. **Helper wrappers follow product namespace.**
   Public helper entrypoints become `bin/changerail-review-verdict`,
   `bin/changerail-delivery-runner` and `bin/changerail-delivery-metrics`.

## Risks / Trade-offs

- **Risk:** Old review verdicts fail new validators. -> **Mitigation:** Treat
  this as a breaking migration and require fresh verdicts for post-rename
  publish flows.
- **Risk:** Consumer scripts call old helper names. -> **Mitigation:** Consumer
  migration tasks must replace helper symlinks and run verification.

## Migration Plan

1. Rename schemas and update schema ids.
2. Rename helper scripts/wrappers and imports.
3. Update runtime default paths and env names.
4. Update docs and smoke tests.
5. Record breaking contract namespace migration in release notes.
