## 1. Role Contract

- [x] 1.1 Add orchestrator, delivery worker and reviewer responsibilities to
  `AGENTS.shared.md`.
- [x] 1.2 Update `changerail-deliver` with supervised orchestrator wording and
  fresh review safety stop.
- [x] 1.3 Update `changerail-do` handoff wording for the delivery worker role.
- [x] 1.4 Update `changerail-review` wording for reviewer role and self-review
  boundary.
- [x] 1.5 Update Claude command reminders where needed.

## 2. Verification

- [x] 2.1 Run `./bin/openspec validate "define-agent-role-contract" --strict`.
- [x] 2.2 Run `./bin/openspec validate --all --strict`.
- [x] 2.3 Run `git diff --check`.
- [x] 2.4 Run targeted public-surface scan for touched methodology/skill files.

## Verification Notes

- `./bin/openspec validate define-agent-role-contract --strict` passed.
- `./bin/openspec validate --all --strict` passed with 17 items.
- `git diff --check` passed.
- Targeted scan for private `/opt/*` paths returned no matches; reviewed
  pre-existing `opsx` hits are historical rename references.
