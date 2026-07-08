---
name: opsx-explore
description: Short OPSX alias for OpenSpec explore mode. Use when the user asks for `$opsx-explore`, `opsx:explore`, `/opsx:explore`, or wants to explore an idea, problem, architecture, requirement, or active OpenSpec change before implementation.
---

# OPSX Explore

## Purpose

Enter OPSX/OpenSpec explore mode with a short command:

```text
$opsx-explore
```

Explore mode is for thinking, investigation and shaping the work before
implementation. It can read repository context and OpenSpec artifacts, but it
does not apply product/runtime changes.

## Stance

- Explore; do not implement.
- Stay grounded in the actual repository.
- Ask concise questions when they materially unblock better planning.
- Surface options, risks, hidden complexity and trade-offs.
- Use compact tables or ASCII diagrams when they clarify architecture, state,
  data flow or decision space.
- Do not force OpenSpec artifacts, but offer to capture decisions when the
  discussion becomes concrete.

## Project Context

At the start, check current OpenSpec state when the project has OpenSpec:

```bash
openspec list --json
```

Then load only relevant context:

1. `openspec/config.yaml` if it exists.
2. `openspec/project.md` only as legacy fallback.
3. `AGENTS.md`, `AGENTS.shared.md`, board docs and local workflow docs when
   they affect ownership, scope, verification or constraints.
4. Active change artifacts when the user mentions a change or the change is
   clearly relevant:
   - `openspec/changes/<name>/proposal.md`
   - `openspec/changes/<name>/design.md`
   - `openspec/changes/<name>/tasks.md`
   - `openspec/changes/<name>/specs/**/spec.md`

Treat project boundaries, non-goals and safety policy from those files as
binding. If the issue belongs in another repository, say so and suggest a card
there instead of drifting across repo boundaries.

## What To Do

Depending on the request:

- investigate the codebase and map the relevant architecture;
- compare implementation options;
- reframe a vague idea into clearer goals and non-goals;
- identify missing requirements or design decisions;
- trace how an active OpenSpec change is affected by new information;
- suggest next steps such as continuing exploration, creating a card, creating
  a proposal or switching to implementation.

Creating or updating OpenSpec artifacts is allowed only when the user asks to
capture the exploration. Writing application code is not part of explore mode.

## Guardrails

- Do not implement code or make product/runtime changes.
- Do not mark tasks complete.
- Do not archive, sync specs or run delivery loops from explore mode.
- Do not auto-capture decisions into artifacts without user consent.
- Do not fake certainty; inspect files or state uncertainty.
- If the user asks to implement, explain that explore mode is for thinking and
  point to the appropriate implementation workflow.

## Completion

If useful, end with a compact summary:

- what is now understood;
- viable options;
- risks or unknowns;
- recommended next command or artifact update.
