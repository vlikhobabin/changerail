## Context

The public docs were written across several bootstrap changes. Some documents
still describe templates, bootstrap, verify and scripts as planned work, while
newer runner, metrics, review-history and manifest/finalization surfaces are
already tracked. Docs must be synchronized after the CI/baseline hardening
changes so the public surface described to consumers matches what exists.

## Goals / Non-Goals

**Goals:**
- Update public docs and notes to describe the current tracked ChangeRail
  surface.
- Keep examples generic and public-safe.
- Include user-facing Unreleased changes after `0.1.0`.
- Clarify drift command usage and generated fixture behavior.

**Non-Goals:**
- Add English docs beyond the existing Russian-first public surface.
- Change runtime contracts or helper behavior except as needed by the CI and
  baseline changes.
- Document private workspace migration notes.

## Decisions

- Treat README, AGENTS, changelog, compatibility notes, migration guide and
  release discipline as the durable public docs for this card.
- Add changelog bullets by capability area rather than every touched file.
- Keep compatibility notes focused on operators and consumer projects, including
  exact commands they can run.
- Keep migration notes generic and preserve `/opt/changerail` and
  `/opt/example-project` examples.

## Risks / Trade-offs

- Docs can overstate newly added release checks before implementation is green.
  Mitigation: update docs after the CI/baseline changes are implemented and
  verified.
