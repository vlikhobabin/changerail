## ADDED Requirements

### Requirement: Board docs align with lifecycle surface
ChangeRail board documentation MUST describe the currently available lifecycle
surface and MUST NOT retain obsolete statements that delivery, review or
publish skills are unavailable when those skills are part of the public surface.

#### Scenario: Agent reads the root board README
- **WHEN** an agent reads `openspec/board/README.md`
- **THEN** the README describes `changerail-ff`, `changerail-do`,
  `changerail-review`, `changerail-pub` and `changerail-deliver` as available
  lifecycle surfaces
- **AND** it keeps the review-gated `3.inprogress -> 4.done` boundary aligned
  with shared methodology
