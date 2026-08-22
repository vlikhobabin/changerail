## Context

Investigation ограничила resume existing fingerprints, closed blocker enum и
scoped evidence; authorization не может стать generic dirty bypass.

## Goals / Non-Goals

**Goals:** publish exact source with ceiling 500 and protocol allowance.

**Non-Goals:** handle credentials, rebind targets or implement resume.

## Decisions

- Source applies only to exact `3.inprogress` successor.
- Critical semantic review remains mandatory for implementation.
- Over-ceiling/broader authority requires split/new investigation.

## Risks / Trade-offs

- **Authorization is mistaken for credential authority.** Exact card scope and
  non-goals keep credential/mutation review boundary unchanged.
