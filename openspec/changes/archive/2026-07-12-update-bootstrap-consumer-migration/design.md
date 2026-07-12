## Context

Consumer projects discover the workflow through generated project files,
symlinks, helper wrappers and verification gates. After the product rename,
bootstrap and verify become the enforcement point that prevents new consumers
from inheriting stale OPSX wiring.

## Goals / Non-Goals

**Goals:**
- Generate new consumers with ChangeRail paths and command names.
- Verify ChangeRail wiring and reject stale OPSX defaults.
- Update release smoke and drift checks for generated ChangeRail fixtures.
- Document GitHub rename and consumer migration steps.

**Non-Goals:**
- Do not mutate non-empty existing consumer projects through bootstrap.
- Do not put real consumer project names into tracked docs.
- Do not preserve `/opt/opsx` as a normal supported source-of-truth path.

## Decisions

1. **Bootstrap stays for new/empty projects.**
   Existing project migration remains a runbook/adoption flow. This avoids
   overwriting project-local rules during the rename.

2. **Verify enforces canonical ChangeRail wiring.**
   `verify-project` should fail old `.claude/commands/opsx`,
   `.codex/skills/opsx-*` and `bin/opsx-*` defaults after the rename.

3. **Placeholders are renamed.**
   Templates should use `{{CHANGERAIL_ROOT}}` and
   `{{CHANGERAIL_SHARED_AGENTS}}` so future generated files do not carry stale
   OPSX terminology.

## Risks / Trade-offs

- **Risk:** Consumers update repo path but not command symlinks. ->
  **Mitigation:** verify-project checks every expected skill/helper symlink.
- **Risk:** CI misses stale generated text. -> **Mitigation:** release smoke
  creates a generated fixture and scans it for old defaults.

## Migration Plan

1. Update templates and bootstrap symlink plan.
2. Update verify checks and smoke fixtures.
3. Rename CI workflow references.
4. Update docs/runbooks for new and existing consumers.
5. Use the generated fixture as regression evidence before real consumer
   migration.
