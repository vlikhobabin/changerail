---
description: "OPSX board fast-forward: decompose a board card or story into apply-ready OpenSpec changes"
argument-hint: <card-path> [--max-changes N] [--from slug] [--until slug] [--no-move]
---

Run the **`opsx-ff`** skill.

Load and follow the `opsx-ff` skill by name through Claude skill discovery,
treating the arguments below as the skill's `$opsx-ff` input. This `/opsx:ff`
command is the Claude invocation surface for the same generic OPSX board
planning flow.

Arguments: $ARGUMENTS

Reminders from the skill contract:

- Plan and create OpenSpec artifacts only.
- Do not implement code in this step.
- If no card path is given and it cannot be inferred, ask for it before
  proceeding.
- When done, hand off to the project's delivery workflow. Use
  `/opsx:do <card-path>` only when that command surface is installed.
