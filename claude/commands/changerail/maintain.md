---
description: "ChangeRail maintain: audit or triage repository maintenance findings without delivery, publish or fix mutation"
argument-hint: "[audit|triage] [--report <path>] [--annotations <path>] [--write-cards]"
---

Run the **`changerail-maintain`** skill.

Load and follow the `changerail-maintain` skill by name through Claude skill
discovery, treating the arguments below as the skill's `$changerail-maintain`
input. This `/changerail:maintain` command is the Claude invocation surface for
the same generic ChangeRail maintenance audit and triage workflow.

Arguments: $ARGUMENTS

Reminders from the skill contract:

- Default to read-only `audit` when no mode is supplied.
- `audit` runs or consumes deterministic maintenance scan/report output and
  must not mutate tracked files, baseline, board, runtime state or external
  systems.
- `triage` is preview-first and writes only ignored annotations/previews unless
  the operator explicitly supplies `--write-cards`.
- Maintain does not implement delivery, publish or fix.
