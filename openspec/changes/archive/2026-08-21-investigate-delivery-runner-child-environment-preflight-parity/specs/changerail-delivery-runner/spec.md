## ADDED Requirements

### Requirement: Child-environment publish-target preflight investigation decision
ChangeRail MUST publish a tracked investigation decision before implementing
delivery-runner queue admission changes for child-equivalent publish-target
preflight. The decision MUST reproduce the supervisor/child parity gap with
public-safe deterministic evidence, map execution boundaries, select one
canonical preflight design, define structured terminal behavior and bind one
exact implementation successor with its verification floor.

#### Scenario: Investigation records deterministic parity reproducer
- **WHEN** the child-environment publish-target preflight investigation is
  completed
- **THEN** it records a public-safe deterministic reproducer in which a
  supervisor publish-target proof passes for a temporary repository and local
  upstream
- **AND** the same workspace, branch and configured remote are checked through
  a child-equivalent Git/SSH resolution profile that fails with a sanitized
  `ssh_config` class
- **AND** the reproducer does not require real credentials, private remotes,
  live provider access or machine-local runtime logs

#### Scenario: Decision maps child execution boundaries
- **WHEN** the investigation records the selected design
- **THEN** it identifies runner process, launcher environment, Codex
  configuration, permission profile, sandboxed command execution, Git
  configuration and SSH configuration resolution as boundaries that can affect
  publish-target proof
- **AND** it states why supervisor-only `git ls-remote` proof is insufficient
  for queue admission

#### Scenario: Decision selects child-equivalent preflight receipt
- **WHEN** the investigation binds the canonical design
- **THEN** it requires the future implementation to produce a pre-delivery
  child-equivalent receipt before aggregate queue admission, before workspace
  lock creation and before delivery child launch
- **AND** the receipt is bound to workspace, card, `HEAD`, branch, remote,
  remote URL class, launcher, `CODEX_WORKDIR`, effective `CODEX_HOME` policy,
  permission profile and sanitized Git/SSH profile
- **AND** the decision sets a bounded freshness interval and requires
  dispatch-time revalidation before each later child starts

#### Scenario: Decision preserves structured failure and retry taxonomy
- **WHEN** the future child-equivalent proof fails
- **THEN** the selected contract records aggregate `BLOCKED` with
  `terminal_reason: publish_target_preflight_failed`
- **AND** the affected card status preserves sanitized `failure_class`,
  retryability, attempt count and child status reference instead of falling
  back to `unpublished_card`
- **AND** retry is bounded to DNS, timeout and transient transport classes while
  authentication, SSH policy/configuration and missing branch remain
  non-retryable

#### Scenario: Decision constrains SSH override support
- **WHEN** the investigation evaluates SSH override support
- **THEN** it allows only explicit consumer-scoped overrides that do not become
  a generic default, bypass host policy or modify package-managed system SSH
  files
- **AND** diagnostics must remain sanitized and must not expose credentials,
  identity paths, URL userinfo or raw SSH configuration contents

#### Scenario: Decision binds exact implementation successor
- **WHEN** the investigation names the implementation successor
- **THEN** it binds successor id
  `add-delivery-runner-child-equivalent-preflight`
- **AND** it records the current successor path
  `openspec/board/1.backlog/add-delivery-runner-child-equivalent-preflight.md`
- **AND** it records a production LOC ceiling of 300 added production-counted
  lines and a `no` runner/status protocol-boundary declaration
- **AND** it states that exceeding this boundary requires a separate published
  authorization bound to this investigation and the exact successor
