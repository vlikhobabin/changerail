---
description: "OPSX explore: enter OpenSpec explore mode for an idea, problem, architecture question or active change"
argument-hint: <topic-or-change-name>
---

Run the **`opsx-explore`** skill.

Load and follow the `opsx-explore` skill by name through Claude skill
discovery, treating the arguments below as the skill's `$opsx-explore` input.
This `/opsx:explore` command is the Claude invocation surface for the same
generic OPSX explore flow.

Arguments: $ARGUMENTS

Reminders from the skill contract:

- Read project context from `openspec/config.yaml`, `AGENTS.md`,
  `AGENTS.shared.md`, relevant artifacts and code.
- Explore and reason only.
- Do not implement. Hand off to `/opsx:ff` or an implementation workflow when
  the work is ready.
