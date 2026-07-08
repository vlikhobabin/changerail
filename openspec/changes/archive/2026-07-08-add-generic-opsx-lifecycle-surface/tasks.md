## 1. Lifecycle Skill Surface

- [x] 1.1 Add path-neutral `skills/opsx-do/SKILL.md`.
- [x] 1.2 Add path-neutral `skills/opsx-review/SKILL.md` and verdict reference.
- [x] 1.3 Add path-neutral `skills/opsx-pub/SKILL.md`.
- [x] 1.4 Add path-neutral `skills/opsx-deliver/SKILL.md`.
- [x] 1.5 Add Claude wrappers for `/opsx:do`, `/opsx:review`, `/opsx:pub` and `/opsx:deliver`.

## 2. Documentation

- [x] 2.1 Update README and Claude notes to describe the full lifecycle surface.
- [x] 2.2 Update architecture roadmap status for lifecycle skills.

## 3. Verification

- [x] 3.1 Run `openspec validate "add-generic-opsx-lifecycle-surface" --strict`.
- [x] 3.2 Run public-surface scan for path-specific or private source terms in lifecycle skills and wrappers.
- [x] 3.3 Run `git diff --check`.

## Verification Notes

- `openspec validate add-generic-opsx-lifecycle-surface --strict` passed.
- `python3 scripts/smoke-wiring-discovery.py` passed with 118/118 checks.
- Targeted public-path scan over docs, skills, commands, scripts, schemas and
  card artifacts returned no private path matches after cleanup.
- `git diff --check` passed.
