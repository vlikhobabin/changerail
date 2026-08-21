## ADDED Requirements

### Requirement: Child-equivalent delivery-plan publish-target preflight
The delivery runner MUST use a single-card child-equivalent preflight receipt
for delivery-plan admission before aggregate queue launch, workspace lock
creation or delivery child launch.

#### Scenario: Child publish-target failure blocks admission before locks
- **WHEN** `preflight-plan` or initial `run-plan` validates a delivery plan in
  remote-push mode
- **AND** the supervisor checks pass
- **AND** the child-equivalent single-card preflight fails its `publish target`
  check
- **THEN** aggregate status records `BLOCKED`
- **AND** no workspace lock is created
- **AND** no delivery child is launched
- **AND** the affected card status contains `terminal_reason:
  publish_target_preflight_failed`
- **AND** the affected card status contains `run_status_path` pointing at the
  child `changerail.delivery-run.v1` status
- **AND** the affected card status preserves the sanitized remote
  `failure_class` when the child status provides one

#### Scenario: Child publish-target pass admits the queue
- **WHEN** delivery-plan admission runs in remote-push mode
- **AND** supervisor checks and child-equivalent single-card preflight pass
- **THEN** the aggregate run is admitted without weakening clean-tree,
  authority, auth, upstream or remote reachability checks
- **AND** later delivery launch still uses the normal single-card runner command

#### Scenario: Explicit no-push remains local-only
- **WHEN** delivery-plan admission runs with explicit `--no-push`
- **THEN** child-equivalent single-card preflight receives the explicit no-push
  argument
- **AND** remote publish-target failure is not silently converted into no-push
- **AND** the aggregate status mode remains `no-push`

### Requirement: Delivery-plan dispatch revalidates child publish target
The delivery runner MUST re-run child-equivalent publish-target preflight for
each unresolved card immediately before dispatching that card from `run-plan`
or `resume-plan`.

#### Scenario: Dispatch revalidation catches later environment drift
- **WHEN** an aggregate run has already delivered or skipped earlier cards
- **AND** a later ready card's child-equivalent publish-target preflight fails
  immediately before dispatch
- **THEN** the aggregate run records `BLOCKED`
- **AND** no workspace lock is created for that card
- **AND** no delivery child is launched for that card
- **AND** the affected card status contains `terminal_reason:
  publish_target_preflight_failed`
- **AND** the affected card status references the fresh child preflight status
  with `run_status_path`

#### Scenario: Resume keeps delivered cards skipped and revalidates pending cards
- **WHEN** `resume-plan` continues a prior aggregate run
- **AND** previous cards are already delivered and still satisfy queue success
  checks
- **THEN** those cards remain skipped
- **AND** pending cards remain dependency-ordered
- **AND** each pending card receives fresh child-equivalent preflight before
  dispatch

### Requirement: Single-card publish-target preflight terminal status
Single-card preflight status MUST expose a specific terminal reason when the
publish-target check fails so aggregate consumers do not collapse the blocker
to `unpublished_card`.

#### Scenario: Single-card preflight records publish-target terminal reason
- **WHEN** `bin/changerail-delivery-runner preflight --write-status` cannot
  prove the remote-push publish target
- **THEN** the written `changerail.delivery-run.v1` status records `BLOCKED`
- **AND** `terminal_reason` is `publish_target_preflight_failed`
- **AND** the failed `publish target` check retains sanitized `failure_class`,
  retryability, attempt count and evidence fields when available

#### Scenario: Non-publish-target preflight failures remain generic blockers
- **WHEN** single-card preflight fails for a check other than `publish target`
- **THEN** the runner records `BLOCKED`
- **AND** it does not misclassify that failure as
  `publish_target_preflight_failed`
