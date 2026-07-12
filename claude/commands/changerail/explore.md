---
description: "ChangeRail explore: enter OpenSpec explore mode for an idea, problem, architecture question or active change"
argument-hint: <topic-or-change-name>
---

Run the **`changerail-explore`** skill.

Load and follow the `changerail-explore` skill by name through Claude skill
discovery, treating the arguments below as the skill's `$changerail-explore` input.
This `/changerail:explore` command is the Claude invocation surface for the same
generic ChangeRail explore flow.

Arguments: $ARGUMENTS

Reminders from the skill contract:

- Read project context from `openspec/config.yaml`, `AGENTS.md`,
  `AGENTS.shared.md`, relevant artifacts and code.
- Explore and reason only.
- Do not implement. Hand off to `/changerail:ff` or an implementation workflow when
  the work is ready.
