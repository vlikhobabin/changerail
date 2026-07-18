## ADDED Requirements

### Requirement: Delivery skills hand off fix-budget exhaustion structurally
`changerail-do` and `changerail-deliver` MUST use a shared structured handoff
when the pre-review fix budget is exhausted, while keeping the independent
review rescue budget separate.

#### Scenario: Do exhausts its fix budget
- **WHEN** `changerail-do` reaches `--max-fix-cycles` without completing
  verification
- **THEN** it MUST stop the phase with `terminal_outcome: BLOCKED` and
  `terminal_reason: fix_budget_exhausted`
- **AND** it MUST report remaining findings and evidence without requesting an
  exceptional manual budget as the default continuation

#### Scenario: Deliver receives fix-budget exhaustion
- **WHEN** supervising `changerail-deliver` receives the structured
  `fix_budget_exhausted` handoff
- **THEN** it MUST classify the remaining work as bounded same-card micro-fix,
  linked rescue/replacement work or external blocker
- **AND** it MUST NOT count that handoff as an independent-review `NO-GO`

#### Scenario: Bounded continuation still cannot verify
- **WHEN** a bounded same-card micro-fix does not reach its concrete
  verification target
- **THEN** the lifecycle MUST stop or create a linked recovery card according
  to scope instead of extending the local loop without a bound
