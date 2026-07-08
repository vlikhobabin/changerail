## Context

The current public source surface has only `opsx-explore` and `opsx-ff`. Source
material for the remaining OPSX phases exists in a suite workspace, but those
instructions include domain-specific trace/provider policy and absolute
fallback paths that are not acceptable in the generic OPSX core.

## Goals / Non-Goals

**Goals:**
- Provide the four remaining OPSX lifecycle skills under `skills/`.
- Provide matching Claude command wrappers under `claude/commands/opsx/`.
- Keep instructions path-neutral and generic enough for future consumer
  symlinks.
- Preserve the independent review-gate contract.

**Non-Goals:**
- Implement bootstrap, verify-project or drift-gate behavior.
- Add domain-specific provider readiness, verification matrices or trace
  capture policy.
- Commit or publish any card result from this change.

## Decisions

1. The generic lifecycle skills will describe the workflow contracts directly
   instead of referencing private suite fallback paths. When helper scripts are
   needed, instructions resolve them from the current OPSX source tree or the
   consumer project wiring.
2. Claude wrappers stay thin: they load the matching skill by name through
   Claude skill discovery and forward the user's arguments.
3. Review remains independent. `opsx-deliver` may stop at an external review
   gate when an operator or supervisor supplies that mode, but the generic
   default remains `ff -> do -> review -> pub`.

## Risks / Trade-offs

- Porting long skill contracts can accidentally retain suite-specific
  language. Mitigation: run a public-surface scan over `skills/` and
  `claude/commands/opsx/`.
- Removing trace/provider policy makes the core less prescriptive for
  domain-heavy consumers. Mitigation: document that domain extensions layer
  their own policy on top of the generic core.
