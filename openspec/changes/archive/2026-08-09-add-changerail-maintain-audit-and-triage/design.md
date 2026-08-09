## Context

`060-01` through `060-03` delivered deterministic repository knowledge
validation, scan, lifecycle report, triage annotation and board-card preview
contracts. Those helpers are intentionally non-LLM and low-level. This change
adds the agent-facing layer that tells Codex and Claude how to consume those
contracts without silently escalating from audit to repository mutation.

The new surface belongs beside existing lifecycle skills in `skills/`,
`.codex/skills/` and `claude/commands/changerail/`. It is not a replacement for
`bin/changerail-maintenance`; the CLI remains the deterministic producer and
validator of JSON contracts.

## Goals / Non-Goals

**Goals:**
- Add discoverable `changerail-maintain` and `chrl-maintain` Codex skills.
- Add `/changerail:maintain` and `/chrl:maintain` Claude wrappers.
- Define `audit` as read-only repository knowledge inspection with optional
  prose explanation.
- Define `triage` as schema-bound ignored-runtime annotation and preview work.
- Make tracked card writes require a separate explicit `--write-cards` operator
  intent.
- Keep delivery, publish and fix outside this skill.

**Non-Goals:**
- Do not implement `fix`; that is card `060-06`.
- Do not add scheduler execution; that is `add-scheduled-maintenance-runners`.
- Do not change maintenance schema semantics already delivered by `060-03`.
- Do not add provider-specific scheduler or issue tracker integrations.

## Decisions

1. Maintain is an agent workflow skill, not a new deterministic scan engine.
   The skill invokes or consumes `bin/changerail-maintenance scan/report` output
   and uses existing schemas for triage/card previews. Alternative: put prose
   guidance directly into the CLI. Rejected because the CLI must remain
   deterministic and usable without an LLM.
2. `audit` is strictly read-only. It may run scan/report commands and explain
   ambiguous findings, but it cannot write state, baseline, board cards or
   external systems. Alternative: allow audit to refresh lifecycle state.
   Rejected because scheduler and audit use cases need a safe default.
3. `triage` can write ignored annotations/previews under
   `.runtime/changerail/maintenance/`, but tracked board mutation requires an
   explicit `--write-cards` handoff to the existing card bridge. Alternative:
   make triage create cards by default. Rejected because the triage output must
   remain reviewable before tracked board changes.
4. `chrl-maintain` mirrors the existing short lifecycle alias pattern and
   delegates to the canonical `changerail-maintain` contract. Alternative:
   duplicate the full instructions. Rejected to keep one source of truth.
5. Claude wrappers are thin command surfaces that load the matching skill by
   discovery, matching current wrapper conventions.

## Risks / Trade-offs

- [Risk] Operators may expect `maintain triage` to fix issues. -> Mitigation:
  skill wording explicitly routes fix/mutation to normal ChangeRail card flow
  and names `060-06` as the future fix-mode owner.
- [Risk] Read-only audit might be too constrained for baselining. ->
  Mitigation: baseline acceptance already has explicit CLI `--write` semantics;
  maintain skill can point to that handoff without executing it by default.
- [Risk] Multiple wrappers can drift. -> Mitigation: alias skill and short
  wrapper delegate to canonical instructions; validation checks frontmatter and
  path-neutrality.

## Migration Plan

Add the new skill and wrapper files without changing existing lifecycle skill
behavior. Consumers that link all ChangeRail skills can discover maintain after
refresh; existing consumers remain unaffected until they opt into maintenance
workflows.

Rollback removes the new skill/wrapper surfaces while preserving the
deterministic maintenance CLI and schemas.

## Open Questions

- none
