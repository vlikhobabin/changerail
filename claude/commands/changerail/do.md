---
description: "ChangeRail do: implement, verify, sync specs and archive planned OpenSpec changes for a board card"
argument-hint: <card-path> [--from slug] [--until slug] [--max-fix-cycles N]
---

Run the **`changerail-do`** skill.

Load and follow the `changerail-do` skill by name through Claude skill discovery,
treating the arguments below as the skill's `$changerail-do` input. This `/changerail:do`
command is the Claude invocation surface for the same generic ChangeRail delivery
flow.

Arguments: $ARGUMENTS

Reminders from the skill contract:

- Implement one card-owned OpenSpec change at a time.
- Verify with project-required commands before sync/archive.
- Do not commit, push or self-review.
- Hand off to `/changerail:review <card-path>` when delivery is complete.
