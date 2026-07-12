## Context

Several local projects already consume the current OPSX workflow. Their real
names and paths are operator-local and must remain in ignored inventory. The
public repository can define the migration protocol without exposing that list.

## Goals / Non-Goals

**Goals:**
- Migrate known local consumers one at a time after ChangeRail tooling is ready.
- Require session restart and project-local verification for each consumer.
- Keep real consumer identifiers out of tracked ChangeRail files.
- Allow the main ChangeRail rename to publish when consumer rewiring and
  verification are complete but session restart must wait for active work in a
  consumer repository.

**Non-Goals:**
- Do not perform consumer repository edits in the ChangeRail repo change.
- Do not commit local operator inventory.
- Do not migrate projects that are not explicitly selected by the operator.

## Decisions

1. **Consumer list stays in ignored `internal/`.**
   This satisfies public safety while allowing the operator to retain concrete
   migration order and notes.

2. **Consumer migration depends on tooling rename.**
   Real consumers should not be rewired until `/opt/changerail/bin/verify-project`
   can validate the new surface.

3. **GitHub rename is an explicit operator gate.**
   The implementing session cannot rename the GitHub repository by editing this
   local working tree. Before touching known consumers it must check `origin`
   and stop if the repository still points at the old `opsx` URL, asking the
   operator to rename GitHub and update/confirm the remote.

4. **One project at a time.**
   Each project has its own git status, agent sessions and verification floor.
   Mixing them would make rollback and review harder.

5. **Session restart may be deferred as an operator card.**
   When an active consumer session cannot be stopped safely, the rename delivery
   records verified rewiring and creates a separate board card for restart,
   fresh-context verification and consumer repository publication. The migrated
   consumer is not considered ready for `/changerail:*` or `$changerail-*` use
   until that follow-up is done.

## Risks / Trade-offs

- **Risk:** Active sessions keep old discovery state. -> **Mitigation:** Stop or
  finish Claude/Codex sessions before rewiring, then restart after verification.
- **Risk:** Private project names leak into ChangeRail docs. -> **Mitigation:**
  scan tracked files for operator-local project paths before public commit.
- **Risk:** A consumer has domain-specific overlays. -> **Mitigation:** preserve
  project-local rules and migrate only the generic ChangeRail-owned wiring.

## Migration Plan

1. Read ignored operator inventory.
2. Check `git remote -v` for the ChangeRail repository.
3. If the remote still points to the old `opsx` repository, stop and ask the
   operator to rename GitHub to `changerail` and update local `origin`.
4. For each selected consumer, check `git status` and pause on unrelated WIP.
5. Replace old OPSX symlinks/helpers/docs with ChangeRail equivalents.
6. Run `/opt/changerail/bin/verify-project <project>`.
7. Record result in the consumer repository or ignored operator notes.
8. Restart agent sessions for that project before using ChangeRail commands, or
   create a separate follow-up card if active sessions cannot be interrupted.
