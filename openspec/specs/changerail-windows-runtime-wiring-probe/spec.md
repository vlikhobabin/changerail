# changerail-windows-runtime-wiring-probe Specification

## Purpose
Зафиксировать public-safe harness contract для native Windows runtime, wiring
и Git behavior probes внутри ignored disposable lab roots.

## Requirements

### Requirement: Disposable runtime wiring probe
ChangeRail MUST provide a public-safe native Windows runtime/wiring probe that
executes only inside ignored disposable lab roots and reports generic host ids.

#### Scenario: Live probe uses ignored inventory
- **WHEN** the live runtime/wiring probe is executed
- **THEN** it reads `id`, `ssh_command` and `disposable_root` from an ignored
  Windows lab inventory
- **AND** tracked or printed sanitized summaries identify only
  `windows-host-a` and `windows-host-b`

#### Scenario: Probe isolates fixture writes
- **WHEN** a host probe starts
- **THEN** it creates a per-run fixture directory below the configured
  disposable root
- **AND** it cleans up only that per-run fixture directory after the checks

### Requirement: Wiring strategy observations
The runtime/wiring probe MUST observe directory links, file links, generated
copies, wrapper invocation variants and Git traversal behavior as separate
strategy checks.

#### Scenario: Filesystem wiring checks are separated
- **WHEN** the probe evaluates filesystem wiring strategies
- **THEN** direct directory symlink, direct file symlink, junction and generated
  copy outcomes are reported as separate checks
- **AND** each check records `passed`, `failed`, `not-applicable` or
  `unsupported` with a concise sanitized reason when needed

#### Scenario: Runtime wrapper launch checks are separated
- **WHEN** the probe evaluates wrapper invocation strategies
- **THEN** extensionless direct launch, `.cmd`, PowerShell, Python and explicit
  Bash invocation are reported as separate checks
- **AND** unavailable runtime prerequisites are recorded without failing the
  entire host probe

#### Scenario: Git traversal uses machine-readable checks
- **WHEN** the probe evaluates Git behavior for linked or generated wiring
- **THEN** it records `git status --porcelain`, `git add --dry-run` and index
  inspection outcomes
- **AND** it does not rely only on console display text

### Requirement: Sanitized probe evidence
The runtime/wiring probe MUST retain raw host output only in ignored runtime
evidence and emit a sanitized structured report.

#### Scenario: Runtime report is retained outside tracked files
- **WHEN** a live probe completes
- **THEN** raw stdout and stderr are retained under ignored
  `.runtime/changerail/` paths
- **AND** tracked files reference only the sanitized report path, command class,
  generic host id and observed outcome summary

#### Scenario: Dry-run validates report shape
- **WHEN** a maintainer runs the probe dry-run with the sample inventory
- **THEN** it validates the public report shape without contacting real Windows
  hosts
- **AND** it reports both expected generic host ids
