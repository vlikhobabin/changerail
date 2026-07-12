# {{PROJECT_NAME}}

Read `AGENTS.md` first. This project uses ChangeRail from `{{CHANGERAIL_ROOT}}`.

ChangeRail Claude commands are exposed through `.claude/commands/changerail`:

- `/changerail:explore`
- `/changerail:ff`
- `/changerail:do`
- `/changerail:review`
- `/changerail:pub`
- `/changerail:deliver`

Do not write runtime state, auth files, traces or local reports into tracked
files. Keep project-specific rules in `AGENTS.md`; reusable ChangeRail methodology is
generated there from `{{CHANGERAIL_ROOT}}/AGENTS.shared.md`.
