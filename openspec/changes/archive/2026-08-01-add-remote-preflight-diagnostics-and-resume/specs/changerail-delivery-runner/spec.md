## ADDED Requirements

### Requirement: Remote publish-target preflight diagnostics
The delivery runner MUST classify remote-push publish-target preflight failures
and MUST retain sanitized structured evidence in `changerail.delivery-run.v1`
status without relying on raw child logs.

#### Scenario: SSH config failure is classified
- **WHEN** single-card preflight cannot prove the publish target because Git or
  SSH reports SSH configuration, identity, key setup or host key setup failure
- **THEN** the `publish target` preflight check fails with
  `failure_class: ssh_config`
- **AND** the status contains only sanitized remote name, branch, remote URL
  class, command summary and bounded detail

#### Scenario: DNS failure is classified
- **WHEN** single-card preflight cannot resolve the remote host while proving
  the publish target
- **THEN** the `publish target` preflight check fails with
  `failure_class: dns`
- **AND** the failure is marked retryable

#### Scenario: Auth failure is classified
- **WHEN** single-card preflight reaches the remote but authentication or
  authorization is denied
- **THEN** the `publish target` preflight check fails with
  `failure_class: auth`
- **AND** the failure is not marked retryable

#### Scenario: Missing branch is classified
- **WHEN** `git ls-remote --exit-code` proves the remote exists but the selected
  upstream branch ref is absent
- **THEN** the `publish target` preflight check fails with
  `failure_class: missing_branch`
- **AND** the failure is not marked retryable

#### Scenario: Timeout is classified
- **WHEN** publish-target proof times out before `git ls-remote` returns
- **THEN** the `publish target` preflight check fails with
  `failure_class: timeout`
- **AND** the failure is marked retryable

#### Scenario: Unknown remote failure is classified
- **WHEN** publish-target proof fails for a remote condition that does not
  match a more specific class
- **THEN** the `publish target` preflight check fails with
  `failure_class: unknown_remote_failure`
- **AND** the failure remains fail-closed

### Requirement: Bounded transient remote preflight retry
The delivery runner MUST apply bounded retry/backoff only to transient remote
preflight classes and MUST stop immediately on authority or branch uncertainty.

#### Scenario: Transient class is retried
- **WHEN** remote-push preflight fails with `failure_class: dns`, `timeout` or
  `unknown_remote_failure`
- **THEN** the runner may repeat the publish-target proof up to the configured
  bounded attempt count
- **AND** the final status records attempt count and final sanitized evidence

#### Scenario: Non-transient class is not retried
- **WHEN** remote-push preflight fails with `failure_class: ssh_config`,
  `auth` or `missing_branch`
- **THEN** the runner does not retry automatically
- **AND** the final status remains `BLOCKED`

### Requirement: Explicit single-card resume after remote preflight failure
The delivery runner MUST provide an explicit single-card resume path that
accepts prior status for context, repeats full fresh preflight, and launches
delivery only after the selected publish target is proven.

#### Scenario: Resume succeeds after later publish-target proof
- **WHEN** prior single-card status is `BLOCKED` by a remote-push preflight
  failure
- **AND** the operator invokes single-card `resume` with that status
- **AND** fresh preflight now proves the upstream branch through `git ls-remote`
- **THEN** the runner launches `$changerail-deliver` for the current card path
- **AND** the new status records fresh preflight evidence rather than trusting
  the prior failed status

#### Scenario: Resume fails closed on stale or unsafe prior status
- **WHEN** prior status is missing, invalid, belongs to another workspace/card,
  or did not stop at a recoverable remote preflight failure
- **THEN** single-card `resume` records `BLOCKED` and exits non-zero before
  launching delivery

#### Scenario: Resume repeats the full preflight
- **WHEN** single-card `resume` is invoked
- **THEN** the runner re-runs launcher, auth, config, symlink, permission and
  publish-target checks for the current workspace
- **AND** no prior preflight check is treated as a pass

### Requirement: Queue remote preflight diagnostics
The delivery runner MUST propagate child remote publish-target preflight
diagnostics through queue preflight and status records as compact structured
operator evidence.

#### Scenario: Queue preflight reports child remote class
- **WHEN** `preflight-plan` observes a child `publish target` preflight failure
  with a remote `failure_class`
- **THEN** aggregate card status includes a compact reason with that class and
  a `run_status_path` reference to the child `changerail.delivery-run.v1`
  status
- **AND** aggregate status does not inline raw child stdout or stderr

#### Scenario: Queue resume requires fresh child proof
- **WHEN** `resume-plan` continues after a prior child remote preflight stop
- **THEN** the queue runner launches a fresh child run or preflight for the
  unresolved card
- **AND** downstream cards remain blocked until that child satisfies normal
  push-enabled or explicit `--no-push` success criteria
