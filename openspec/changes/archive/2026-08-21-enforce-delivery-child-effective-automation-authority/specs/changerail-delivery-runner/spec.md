## ADDED Requirements

### Requirement: Explicit-home Codex child authority is effective
The delivery runner MUST propagate already-validated unattended automation
authority to the real tracked Codex launcher when the operator explicitly
selects an operator-owned `CODEX_HOME`.

The propagation MUST remain conditional on the existing exact
`approval_policy = "never"` and `sandbox_mode = "danger-full-access"` policy
gate and MUST NOT replace clean-tree, authentication, upstream or publish-target
preflight.

#### Scenario: Explicit trusted home receives invocation-level authority
- **WHEN** the operator explicitly sets `CODEX_HOME`
- **AND** its effective config passes the existing unattended automation
  authority gate
- **AND** the runner uses the tracked ChangeRail Codex launcher
- **THEN** the launched Codex command includes
  `--dangerously-bypass-approvals-and-sandbox` before `exec`
- **AND** existing status records the exact command in `command.argv`
- **AND** no new required status field is introduced

#### Scenario: Unsupported Codex CLI blocks before child launch
- **WHEN** the explicit-home tracked-launcher route requires invocation-level
  authority
- **AND** the installed Codex CLI does not advertise the required bypass mode
- **THEN** preflight records a failed `Codex effective automation authority`
  check
- **AND** no delivery child is launched

#### Scenario: Existing safety gates remain authoritative
- **WHEN** explicit `CODEX_HOME` policy, authentication, workspace cleanliness,
  upstream or publish-target verification fails
- **THEN** the runner remains blocked before child launch
- **AND** invocation-level authority does not convert that failure into a pass

#### Scenario: Non-opted-in launch paths remain unchanged
- **WHEN** the runner uses its generated default runtime home
- **OR** the operator supplies a supported custom launcher
- **THEN** the runner does not inject the Codex-specific bypass option
- **AND** existing launch behavior remains unchanged
