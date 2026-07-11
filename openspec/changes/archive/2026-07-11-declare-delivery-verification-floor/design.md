## Context

The generic delivery workflow needs a mandatory verification baseline, but OPSX
is installed into projects with different languages, tools and infrastructure.
The durable contract should define how to discover required checks and evidence
without silently imposing one global formatter/type/test matrix.

## Goals / Non-Goals

**Goals:**
- Define the sources of mandatory verification for delivery.
- Require explicit evidence/outcomes for every mandatory check.
- Clarify when RED evidence is applicable and when a reason is sufficient.
- Make review audit unbacked verification claims.

**Non-Goals:**
- Do not require every consumer project to use the same formatter, type checker
  or clean-room matrix.
- Do not require test-first evidence for docs-only or config-only changes where
  no behavioral test can be meaningful.

## Decisions

- The verification floor is project-declared.
  - Rationale: `AGENTS.md`, `openspec/config.yaml`, OpenSpec tasks/design and
    touched toolchain are the reliable sources for a project's required checks.
  - Alternative considered: hard-code a global tool matrix. That would fail on
    many valid consumer projects.
- Verification claims must include command and observed outcome.
  - Rationale: the independent reviewer can audit evidence without relying on
    generic assurance text.
- Changed tests need adequacy critique.
  - Rationale: passing tests are weak evidence if they cannot fail for the
    claimed regression or observe the relevant behavior source.

## Risks / Trade-offs

- Some projects may under-declare their floor -> review should flag missing
  project policy only when the local artifacts make the requirement mandatory.
- Evidence can become verbose -> runtime evidence may hold raw logs while cards
  and manifests record concise command/outcome summaries.
