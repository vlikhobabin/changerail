# {{PROJECT_NAME}}

Read `AGENTS.md` first. This project uses ChangeRail from {{CHANGERAIL_ROOT_LABEL}}.

ChangeRail Claude commands are exposed through `.claude/commands/chrl` for
daily use and `.claude/commands/changerail` as the canonical reference surface:

- `/chrl:explore`
- `/chrl:ff`
- `/chrl:do`
- `/chrl:review`
- `/chrl:pub`
- `/chrl:deliver`
- `/changerail:explore`
- `/changerail:ff`
- `/changerail:do`
- `/changerail:review`
- `/changerail:pub`
- `/changerail:deliver`

Do not write runtime state, auth files, traces or local reports into tracked
files. Keep project-specific rules in `AGENTS.md`; reusable ChangeRail methodology is
generated there from the linked ChangeRail `AGENTS.shared.md`.
