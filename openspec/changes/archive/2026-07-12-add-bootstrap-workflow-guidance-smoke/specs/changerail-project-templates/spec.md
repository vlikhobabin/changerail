## ADDED Requirements

### Requirement: Generated workflow guidance remains testable
Project templates MUST render workflow guidance in stable enough terms for
bootstrap smoke to detect lifecycle and review-gated board semantics.

#### Scenario: Consumer project is generated
- **WHEN** bootstrap renders `AGENTS.md` and `openspec/board/README.md`
- **THEN** generated text includes the ChangeRail lifecycle, role model,
  independent review gate and `3.inprogress -> 4.done` finalization boundary
