---
description: "OPSX review: run the independent fresh-context go/no-go gate for a delivered board card"
argument-hint: <card-path> [--cycle N]
---

Run the **`opsx-review`** skill.

Load and follow the `opsx-review` skill by name through Claude skill discovery,
treating the arguments below as the skill's `$opsx-review` input. This
`/opsx:review` command is the Claude invocation surface for the same generic
OPSX review gate.

Arguments: $ARGUMENTS

Reminders from the skill contract:

- Run only from a fresh context that did not plan or implement the card.
- Write only `.runtime/opsx/reviews/<card-id>.json`.
- Do not fix reviewed files, commit or push.
