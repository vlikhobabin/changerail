## ADDED Requirements

### Requirement: Risk-tiered payload review
ChangeRail MUST route payload review through explicit deterministic, ordinary or
critical risk without launching a model for machine-only process review.

#### Scenario: Deterministic process payload passes
- **WHEN** a card explicitly declares deterministic risk, adds no production
  code and deterministic preflight passes
- **THEN** the preflight receipt is the required payload review
- **AND** no LLM review is launched

#### Scenario: Ordinary payload is reviewed
- **WHEN** an ordinary payload needs semantic review
- **THEN** the default reviewer reasoning effort is `high`

#### Scenario: Critical boundary is reviewed
- **WHEN** a payload changes credentials, mutation authority, live admission or
  final certification
- **THEN** it is classified critical
- **AND** the reviewer reasoning effort is `xhigh`

### Requirement: Bounded review repetition
ChangeRail MUST require one risk-appropriate payload review before publish and
MUST NOT repeat broad LLM audits for process-only corrections.

#### Scenario: Focused re-review follows a scoped fix
- **WHEN** a semantic review finding is corrected without changing previously
  verified full-suite inputs
- **THEN** focused re-review may reuse full-suite evidence bound to the unchanged
  tree hash
- **AND** the full suite is rerun before live admission or final publish

#### Scenario: Clean-head milestone audit is requested
- **WHEN** a card declares a clean-HEAD milestone audit
- **THEN** at most one extra LLM audit is launched at that milestone
- **AND** no micro-rescue or manifest-only correction creates another milestone
  audit

### Requirement: Rescue complexity guard
ChangeRail MUST stop patch-staircase rescue for investigation and simplification
when bounded complexity signals are crossed.

#### Scenario: Rescue crosses a complexity signal
- **WHEN** a rescue adds more than 300 production LOC, introduces a new authority
  or wire protocol, or repeats the same defect class
- **THEN** preflight returns `investigation-required`
- **AND** implementation rescue does not continue on the same patch staircase
