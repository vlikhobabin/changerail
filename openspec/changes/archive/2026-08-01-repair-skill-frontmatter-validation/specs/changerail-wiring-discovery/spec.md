## ADDED Requirements

### Requirement: Wiring smoke parses complete skill frontmatter
Wiring discovery smoke MUST parse the full YAML frontmatter for every bundled
skill it validates, rather than extracting only the `name` line with string
splitting.

#### Scenario: Codex skill contract is checked
- **WHEN** wiring smoke validates a `skills/*/SKILL.md` file through repo-local
  or consumer-example Codex wiring
- **THEN** it parses the complete frontmatter as YAML
- **AND** it fails if any frontmatter field makes the YAML document invalid

#### Scenario: Claude skill contract is checked
- **WHEN** wiring smoke validates a bundled skill through Claude skill wiring
- **THEN** it uses the same complete YAML frontmatter parser as Codex skill
  checks
- **AND** it still verifies that parsed `name` matches the expected skill name

### Requirement: Wiring smoke rejects colon scalar regression
Wiring discovery smoke MUST include a deterministic negative fixture proving
that an unquoted scalar containing `: ` is rejected.

#### Scenario: Negative skill metadata fixture is parsed
- **WHEN** wiring smoke runs its frontmatter parser regression check
- **THEN** a fixture with `description: invalid: scalar` fails parsing
- **AND** the smoke fails if that fixture is accepted
