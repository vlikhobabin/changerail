# {{PROJECT_NAME}}

Read `AGENTS.md` first. This project uses OPSX from `{{OPSX_ROOT}}`.

OPSX Claude commands are exposed through `.claude/commands/opsx`:

- `/opsx:explore`
- `/opsx:ff`
- `/opsx:do`
- `/opsx:review`
- `/opsx:pub`
- `/opsx:deliver`

Do not write runtime state, auth files, traces or local reports into tracked
files. Keep project-specific rules in `AGENTS.md`; reusable OPSX methodology is
generated there from `{{OPSX_ROOT}}/AGENTS.shared.md`.
