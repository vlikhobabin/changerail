## MODIFIED Requirements

### Requirement: Consumer wiring contract
OPSX MUST define how consumer projects expose OPSX skills, OpenSpec lifecycle
skills, command wrappers and helper wrappers without requiring undocumented
root paths.

#### Scenario: Consumer project wires Claude surface
- **WHEN** a consumer project follows OPSX wiring
- **THEN** Claude commands resolve from `.claude/commands/opsx` and skills
  resolve from `.claude/skills`

#### Scenario: Consumer project wires Codex surface
- **WHEN** a consumer project follows OPSX wiring
- **THEN** Codex skills resolve from `.codex/skills/opsx-*` and
  `.codex/skills/openspec-*` entries without committing Codex runtime state

#### Scenario: Consumer project wires OpenSpec wrapper
- **WHEN** a consumer project follows OPSX wiring
- **THEN** `bin/openspec` can resolve to the OPSX wrapper while project-local
  OpenSpec artifacts remain in the consumer repository
