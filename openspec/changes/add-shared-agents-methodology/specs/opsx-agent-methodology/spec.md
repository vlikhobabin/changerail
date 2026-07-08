## ADDED Requirements

### Requirement: Shared Agent Methodology
OPSX MUST provide tracked file `AGENTS.shared.md`, задающий reusable agent
methodology для OPSX consumers.

#### Scenario: Consumer project needs OPSX methodology
- **WHEN** consumer project bootstrapped from OPSX templates
- **THEN** project can receive methodology content derived from
  `AGENTS.shared.md`

### Requirement: Generic Public-Safe Content
Shared methodology MUST avoid private workspace names, customer data, secrets,
local traces, credentials и machine-specific runtime state.

#### Scenario: Public repository review
- **WHEN** `AGENTS.shared.md` reviewed before commit
- **THEN** it contains only generic OPSX rules and documented example paths such
  as `/opt/opsx` and `/opt/example-project`

### Requirement: Workflow Coverage
Shared methodology MUST cover OPSX lifecycle from exploration through publish,
including board usage, OpenSpec artifacts, review gates, verification evidence и
scoped publishing.

#### Scenario: Agent reads shared methodology
- **WHEN** agent receives shared methodology in consumer project
- **THEN** it has enough workflow guidance to follow `explore -> ff -> do ->
  review -> pub` without relying on project-private OPSX notes

### Requirement: Drift-Aware Embedding
Shared methodology MUST state that generated consumer-project sections are
subject to future drift checks against OPSX source of truth.

#### Scenario: Future verify-project checks generated instructions
- **WHEN** consumer project has embedded OPSX methodology section
- **THEN** `verify-project` can treat that section as generated content that
  must match `AGENTS.shared.md`
