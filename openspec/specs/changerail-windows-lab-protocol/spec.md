# changerail-windows-lab-protocol Specification

## Purpose
Зафиксировать public-safe protocol для native Windows research lab: generic host
ids, ignored inventory, disposable workspaces, least-privilege SSH execution,
cleanup and evidence retention.

## Requirements

### Requirement: Public-safe Windows lab inventory
ChangeRail MUST keep native Windows lab connection details outside tracked
files while exposing stable generic host ids for public evidence.

#### Scenario: Tracked report names generic hosts
- **WHEN** Windows lab protocol or report content is committed
- **THEN** it identifies hosts only as `windows-host-a` and `windows-host-b`
- **AND** it does not include raw hostname, username, credential, SSH target or
  private disposable root values

#### Scenario: Ignored inventory provides connection data
- **WHEN** the Windows lab harness reads an operator inventory
- **THEN** each host entry includes `id`, `ssh_command` and `disposable_root`
- **AND** the inventory path is ignored by Git

### Requirement: Disposable workspace isolation
Windows lab probes MUST operate only inside per-run disposable directories
derived from the ignored host inventory.

#### Scenario: Probe creates isolated workspace
- **WHEN** a live Windows lab probe starts for a host
- **THEN** it creates or reuses a per-run child directory below that host's
  disposable root
- **AND** it does not write into a real ChangeRail or consumer repository

#### Scenario: Probe cleanup is idempotent
- **WHEN** cleanup runs after a successful or failed probe
- **THEN** it removes only the per-run child directory and fixture files created
  by that probe
- **AND** repeated cleanup attempts do not require manual intervention

### Requirement: Least-privilege non-interactive execution
Windows lab probes MUST use bounded non-interactive SSH execution and MUST NOT
request elevation by default.

#### Scenario: Probe runs without elevation
- **WHEN** the harness executes a remote command
- **THEN** the command is bounded by a configured timeout
- **AND** the command does not invoke UAC, `runas`, administrator elevation or
  persistent machine configuration

#### Scenario: Elevation needs separate operator action
- **WHEN** a future probe requires elevated mode
- **THEN** the card records explicit operator action and separates elevated
  evidence from the default least-privilege result

### Requirement: Evidence retention boundary
Windows lab research MUST retain raw command output only in ignored runtime
evidence and publish only sanitized summaries.

#### Scenario: Raw evidence is retained
- **WHEN** a live Windows lab probe completes
- **THEN** raw command output is stored under ignored `.runtime/changerail/`
  evidence paths
- **AND** tracked cards or docs reference only command class, host id, outcome
  and sanitized capability values

#### Scenario: Local dry-run validates protocol shape
- **WHEN** a maintainer runs the Windows lab harness in dry-run sample mode
- **THEN** it validates the generic inventory/report shape without contacting
  real Windows hosts
