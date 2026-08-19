## ADDED Requirements

### Requirement: Delivery discovery output remains bounded
ChangeRail delivery skills MUST instruct delivery agents to start repository
discovery with scoped, low-output commands before reading broad command output.

#### Scenario: Delivery child searches implementation evidence
- **WHEN** a delivery child needs to inspect implementation state
- **THEN** the delivery skill directs it to prefer scoped paths, file-name
  discovery, counts or bounded excerpts before broad content searches
- **AND** the skill directs the child to narrow follow-up reads to files or
  ranges needed for the current card-owned change

#### Scenario: Search scope is not yet known
- **WHEN** a delivery child cannot identify the relevant paths from the card,
  OpenSpec artifacts or project context
- **THEN** the delivery skill directs it to perform bounded discovery such as
  top-level file lists, targeted spec references or `rg -l` before requesting
  full matching-line output

### Requirement: Truncated discovery output is inconclusive evidence
ChangeRail delivery skills MUST forbid using truncated command output as proof
that implementation is present or absent.

#### Scenario: Search output is truncated
- **WHEN** a command exits because output was truncated or produces an
  incomplete excerpt
- **THEN** the delivery skill directs the agent to treat the result as
  inconclusive
- **AND** the agent must collect narrower structured evidence before recording
  an acceptance, verification or absence claim

#### Scenario: Truncated output includes apparent matches
- **WHEN** truncated output contains some matching lines
- **THEN** the delivery skill directs the agent to verify the relevant files
  directly instead of inferring full implementation coverage from the truncated
  stream
