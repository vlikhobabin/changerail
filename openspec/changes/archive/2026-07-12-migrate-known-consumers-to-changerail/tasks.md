## 1. Operator Inventory

- [x] 1.1 Confirm the ignored consumer inventory under `internal/` lists the selected projects and migration order.
- [x] 1.2 Confirm no real consumer names or paths are present in tracked ChangeRail files before public commit.

## 2. Repository Rename Gate

- [x] 2.1 Run `git remote -v` in the ChangeRail repository.
- [x] 2.2 If `origin` still points to the old `opsx` repository URL, stop before touching consumers and ask the operator to rename GitHub to `changerail` and update or confirm local `origin`.
- [x] 2.3 Continue only after `origin` points to the `changerail` repository URL.

## 3. Per-Consumer Migration

- [x] 3.1 For each selected consumer, stop or finish active Claude/Codex sessions before rewiring when possible; if an active session cannot be interrupted, record a follow-up card before publishing the main rename.
- [x] 3.2 For each selected consumer, check `git status` and pause on unrelated tracked WIP.
- [x] 3.3 Replace generic OPSX wiring with ChangeRail wiring in `.claude`, `.codex`, `bin`, `AGENTS.md`, `CLAUDE.md`, `.mcp.json`, `.codex/config.toml` and local runbooks as applicable.
- [x] 3.4 Preserve project-specific rules, domain overlays and verification floors.
- [x] 3.5 Remove stale generic OPSX wiring after ChangeRail verification is green.

## 4. Verification

- [x] 4.1 Run `/opt/changerail/bin/verify-project <project>` for each migrated consumer.
- [x] 4.2 Record each consumer verification result in that consumer repository or ignored operator notes.
- [x] 4.3 Create a follow-up card for restarting Claude/Codex sessions before using `/changerail:*` or `$changerail-*` where active sessions could not be interrupted.
- [x] 4.4 Run a final public-surface scan in the ChangeRail repository to confirm local consumer names and paths remain untracked.

## Notes

- 2026-07-12: Consumer wiring and verification passed for all selected
  consumers; results are recorded in ignored
  `internal/changerail-consumer-inventory.md`.
- 2026-07-12: An active `claude` session and provider proxy processes were
  detected in one migrated consumer after wiring. The implementation session
  did not terminate those processes. Remaining restart/fresh-context checks are
  tracked by
  `openspec/board/1.backlog/finalize-known-consumer-migration-after-restart.md`.
