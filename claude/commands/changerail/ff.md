---
description: "ChangeRail board fast-forward: decompose a board card or story into apply-ready OpenSpec changes"
argument-hint: <card-path> [--max-changes N] [--from slug] [--until slug] [--no-move]
---

Run the **`changerail-ff`** skill.

Load and follow the `changerail-ff` skill by name through Claude skill discovery,
treating the arguments below as the skill's `$changerail-ff` input. This `/changerail:ff`
command is the Claude invocation surface for the same generic ChangeRail board
planning flow.

Arguments: $ARGUMENTS

If a runner provided `CHANGERAIL_PROGRESS_EVENT_PATH`, follow the canonical
skill's value-free `progress-event ff <stage>` transition contract.

Reminders from the skill contract:

- Plan and create OpenSpec artifacts only.
- Do not implement code in this step.
- If no card path is given and it cannot be inferred, ask for it before
  proceeding.
- When done, hand off to the project's delivery workflow. Use
  `/changerail:do <card-path>` only when that command surface is installed.
