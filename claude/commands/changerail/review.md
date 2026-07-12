---
description: "ChangeRail review: run the independent fresh-context go/no-go gate for a delivered board card"
argument-hint: <card-path> [--cycle N]
---

Run the **`changerail-review`** skill.

Load and follow the `changerail-review` skill by name through Claude skill discovery,
treating the arguments below as the skill's `$changerail-review` input. This
`/changerail:review` command is the Claude invocation surface for the same generic
ChangeRail review gate.

Arguments: $ARGUMENTS

Reminders from the skill contract:

- Run only from a fresh context that did not plan or implement the card.
- Write only `.runtime/changerail/reviews/<card-id>.json`.
- Do not fix reviewed files, commit or push.
