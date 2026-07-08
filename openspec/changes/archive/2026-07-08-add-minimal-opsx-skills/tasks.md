## 1. OpenSpec Planning

- [x] 1.1 Add board card for minimal generic skill surface.
- [x] 1.2 Add `add-minimal-opsx-skills` change metadata, proposal and design.
- [x] 1.3 Add `opsx-skill-surface` spec delta.

## 2. Skill Surface

- [x] 2.1 Add `skills/opsx-explore/SKILL.md`.
- [x] 2.2 Add `skills/opsx-ff/SKILL.md`.
- [x] 2.3 Add Claude wrappers for `/opsx:explore` and `/opsx:ff`.
- [x] 2.4 Update README, AGENTS and CLAUDE notes for the current surface.

## 3. Verification

- [x] 3.1 Run `openspec validate --all --strict`.
- [x] 3.2 Run `.mcp.json` and `.codex/config.toml` parsing checks.
- [x] 3.3 Run whitespace checks covering tracked and untracked files.
- [x] 3.4 Run `git status --short --ignored`.
- [x] 3.5 Run public-surface scan for private names and machine-local paths.

## 4. Review Fixes

- [x] 4.1 Remove root `skills/` path assumptions from Claude wrappers.
- [x] 4.2 Make `opsx-ff` handoff conditional on installed delivery surface.
- [x] 4.3 Update stale board README language for the minimal skill surface.
