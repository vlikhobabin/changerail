---
description: "OPSX pub: validate review verdict, update final docs, create a scoped commit and push"
argument-hint: <card-path> [--no-push] [--message text] [--docs-only]
---

Run the **`opsx-pub`** skill.

Load and follow the `opsx-pub` skill by name through Claude skill discovery,
treating the arguments below as the skill's `$opsx-pub` input. This
`/opsx:pub` command is the Claude invocation surface for the same generic OPSX
publish flow.

Arguments: $ARGUMENTS

Reminders from the skill contract:

- Fail closed unless a fresh valid `go` review verdict is present.
- Stage explicit card-owned paths only.
- Never use broad staging, force-push or destructive git commands.
