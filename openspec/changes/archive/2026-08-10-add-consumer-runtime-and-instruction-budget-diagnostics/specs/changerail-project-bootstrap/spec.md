## ADDED Requirements

### Requirement: Tracked consumer instruction budget
Bootstrap MUST render an explicit `project_doc_max_bytes` value in generated
Codex config and MUST keep generated `AGENTS.md` below the warning threshold at
creation time. The budget MUST be tracked project policy rather than an inferred
machine default.

#### Scenario: Consumer is generated
- **WHEN** bootstrap renders a default consumer
- **THEN** `.codex/config.toml` declares `project_doc_max_bytes = 32768`
- **AND** generated `AGENTS.md` remains below 85 percent of that value

#### Scenario: Generated instructions exceed warning threshold
- **WHEN** template and shared instructions would reach 85 percent before target
  creation completes
- **THEN** bootstrap reports the measured byte count and remediation
- **AND** it does not silently claim an unconstrained instruction surface

### Requirement: Runtime diagnostic handoff
Generated guidance MUST distinguish static verification from opt-in effective
Codex runtime diagnostics and MUST identify ignored evidence and credential
boundaries.

#### Scenario: Operator reads generated guidance
- **WHEN** a consumer inspects verification instructions
- **THEN** static config validation is not described as effective runtime proof
- **AND** the opt-in runtime command and ignored evidence location are stated
