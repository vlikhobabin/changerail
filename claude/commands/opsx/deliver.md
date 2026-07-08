---
description: "OPSX deliver: run ff, do, review and pub for one board card or a bounded card queue"
argument-hint: <card-or-column-path> [--max-cards N] [--no-push] [--max-review-cycles N]
---

Run the **`opsx-deliver`** skill.

Load and follow the `opsx-deliver` skill by name through Claude skill
discovery, treating the arguments below as the skill's `$opsx-deliver` input.
This `/opsx:deliver` command is the Claude invocation surface for the same
generic OPSX supervised card pipeline.

Arguments: $ARGUMENTS

Reminders from the skill contract:

- Process one card at a time through `ff -> do -> review -> pub`.
- Preserve phase safety stops and scoped publish behavior.
- Review must come from a fresh context; the implementing session must not
  write its own verdict.
