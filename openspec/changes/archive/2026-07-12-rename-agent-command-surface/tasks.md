## 1. Skill And Command Rename

- [x] 1.1 Rename `skills/opsx-*` directories to `skills/changerail-*` and update `SKILL.md` frontmatter, descriptions and handoff text.
- [x] 1.2 Rename `claude/commands/opsx/` to `claude/commands/changerail/` and update wrappers from `/opsx:*` to `/changerail:*`.
- [x] 1.3 Update repo-local `.codex/skills/changerail-*` and `.claude/commands/changerail` symlinks.
- [x] 1.4 Update docs, runbooks and templates that list lifecycle commands or skill names.
- [x] 1.5 Confirm `openspec-*` skills and `bin/openspec` remain unchanged.

## 2. Discovery Verification

- [x] 2.1 Run `python3 scripts/smoke-wiring-discovery.py`.
- [x] 2.2 Run `./bin/openspec validate rename-agent-command-surface --strict`.
- [x] 2.3 Run `git diff --check`.
- [x] 2.4 Scan generated and tracked surfaces for stale `/opsx:*`, `$opsx-*`, `.claude/commands/opsx` and `.codex/skills/opsx-*` defaults.
