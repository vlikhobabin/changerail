---
description: "OPSX do: implement, verify, sync specs and archive planned OpenSpec changes for a board card"
argument-hint: <card-path> [--from slug] [--until slug] [--max-fix-cycles N]
---

Run the **`opsx-do`** skill.

Load and follow the `opsx-do` skill by name through Claude skill discovery,
treating the arguments below as the skill's `$opsx-do` input. This `/opsx:do`
command is the Claude invocation surface for the same generic OPSX delivery
flow.

Arguments: $ARGUMENTS

Reminders from the skill contract:

- Implement one card-owned OpenSpec change at a time.
- Verify with project-required commands before sync/archive.
- Do not commit, push or self-review.
- Hand off to `/opsx:review <card-path>` when delivery is complete.
