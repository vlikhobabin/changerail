## ADDED Requirements

### Requirement: Consumer instruction budget verification
`verify-project` MUST measure effective `AGENTS.md` as UTF-8 bytes against the
tracked `project_doc_max_bytes` value. It MUST pass below 85 percent, emit a
non-blocking warning from 85 percent through the configured limit, and fail
blocking above the limit.

#### Scenario: Instructions are below warning threshold
- **WHEN** effective instructions use less than 85 percent of the tracked budget
- **THEN** the instruction budget check passes with measured and allowed bytes

#### Scenario: Instructions approach the limit
- **WHEN** effective instructions use at least 85 percent but do not exceed the
  tracked budget
- **THEN** verification returns a non-blocking warning with remediation

#### Scenario: Instructions exceed the limit
- **WHEN** effective instructions exceed `project_doc_max_bytes`
- **THEN** verification reports a blocking failure
- **AND** it recommends reducing project/shared content or explicitly reviewing
  a tracked budget change

### Requirement: Static and runtime verification separation
Default `verify-project` MUST describe Codex TOML, trust, MCP and instruction
checks as static. Effective runtime diagnostics MUST run only after explicit
operator opt-in and MUST never convert unavailable or invalid probe output into
a successful runtime claim.

#### Scenario: Default verifier runs
- **WHEN** an operator invokes `verify-project` without runtime diagnostics
- **THEN** no Codex runtime or network probe is launched
- **AND** the result makes only static configuration claims

#### Scenario: Runtime diagnostics are requested
- **WHEN** an operator passes `--runtime-diagnostics` in a supported Codex
  environment
- **THEN** version-aware structured probes inspect loaded config/trust/MCP and
  discovered instructions from the consumer context
- **AND** runtime outcome is reported separately from static summary

#### Scenario: Runtime probe is unavailable
- **WHEN** the supported Codex command or expected structured output is absent
- **THEN** runtime diagnostics report unsupported or invalid evidence
- **AND** they do not report runtime readiness

### Requirement: Runtime diagnostic evidence safety
Raw runtime output MUST be stored only under ignored
`.runtime/changerail/diagnostics/`. Machine-readable summaries MUST use an
allowlist and redact absolute local paths, credential values and raw auth data.

#### Scenario: Runtime probe contains local state
- **WHEN** structured Codex output contains home paths, auth marker locations or
  endpoint details
- **THEN** raw data remains ignored
- **AND** public-safe summary reports only classified status and redacted path
  kinds

#### Scenario: Public scan inspects diagnostic fixtures
- **WHEN** current/history public-surface checks run
- **THEN** no raw runtime report, private path or credential-like value is
  tracked
