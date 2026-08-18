# changerail-windows-runtime-entrypoints Specification

## Purpose
Зафиксировать concrete native Windows helper entrypoint contract: tracked
`.cmd` wrappers, process invocation semantics, Python runtime selector usage and
pinned OpenSpec launch behavior.
## Requirements
### Requirement: Supported native Windows helper wrappers
ChangeRail MUST provide tracked `.cmd` wrappers for supported native Windows
helper command entrypoints.

#### Scenario: Maintainer inspects supported helper wrappers
- **WHEN** a maintainer inspects the tracked `bin/` helper surface
- **THEN** `.cmd` wrappers exist for `openspec`, `changerail-python`,
  `verify-project`, `changerail-review-verdict`, `changerail-evidence`,
  `changerail-delivery-runner` and `changerail-delivery-metrics`
- **AND** the existing POSIX entrypoints remain available

#### Scenario: Native Windows operator launches a helper
- **WHEN** an operator launches a supported helper through its `.cmd` wrapper
  from a native Windows command processor
- **THEN** the wrapper invokes the supported helper behavior without requiring
  implicit Bash or direct execution of the extensionless POSIX wrapper

### Requirement: Wrapper process semantics
Native Windows `.cmd` wrappers MUST preserve command invocation semantics
required by ChangeRail helper callers.

#### Scenario: Wrapper forwards process context
- **WHEN** a supported `.cmd` wrapper invokes its helper implementation
- **THEN** the helper receives the caller's argv without shell splitting
- **AND** the caller's current working directory and environment remain
  available to the helper
- **AND** the `.cmd` process exits with the helper's exit code

#### Scenario: Paths need safe forwarding
- **WHEN** helper arguments or repository paths contain spaces or non-ASCII
  characters
- **THEN** the `.cmd` wrapper forwards those values without lossy encoding or
  unquoted path splitting

### Requirement: Windows Python helper runtime selection
Python-backed native Windows helper wrappers MUST use the shared ChangeRail
Python runtime selector.

#### Scenario: Python-backed helper starts on Windows
- **WHEN** a native Windows operator launches a Python-backed helper through its
  `.cmd` wrapper
- **THEN** the wrapper routes execution through `changerail-python.cmd`
- **AND** the same supported Python version and runtime dependency contract used
  by POSIX helper launches applies

#### Scenario: Python runtime is unavailable or unsupported
- **WHEN** the shared selector cannot find a supported Python interpreter or a
  required runtime dependency
- **THEN** the Python-backed `.cmd` helper exits non-zero
- **AND** the diagnostic names the missing or unsupported runtime condition and
  the remediation path before helper-specific imports run

### Requirement: Native OpenSpec launch contract
The native Windows OpenSpec wrapper MUST use the same pinned OpenSpec version
contract as the existing ChangeRail OpenSpec entrypoint.

#### Scenario: OpenSpec wrapper runs on Windows
- **WHEN** an operator launches `openspec.cmd`
- **THEN** the wrapper invokes the pinned OpenSpec CLI contract used by
  ChangeRail
- **AND** npm prefers cached metadata and package content by default
- **AND** it does not require direct extensionless POSIX launch or implicit Bash

#### Scenario: Pinned OpenSpec launch fails
- **WHEN** the pinned OpenSpec invocation cannot start
- **THEN** `openspec.cmd` exits non-zero
- **AND** the failure is attributable to the pinned OpenSpec launch path rather
  than an implicit fallback to another shell or unpinned binary

### Requirement: Deterministic Windows entrypoint fixtures
ChangeRail MUST provide deterministic local verification for native Windows
entrypoint wrapper semantics before other Windows support layers depend on the
wrappers.

#### Scenario: Focused entrypoint smoke runs
- **WHEN** maintainers run the focused Windows entrypoint smoke
- **THEN** it verifies the supported `.cmd` wrapper surface for OpenSpec,
  `changerail-python`, `verify-project`, `changerail-review-verdict`,
  `changerail-evidence`, delivery runner and delivery metrics
- **AND** it verifies argv forwarding, cwd preservation, environment
  preservation and exit-code propagation

#### Scenario: Paths contain spaces or non-ASCII characters
- **WHEN** the deterministic entrypoint fixture uses repository or argument
  paths containing spaces or non-ASCII characters
- **THEN** the smoke verifies those values are represented without lossy
  encoding or unquoted splitting in the wrapper invocation contract

### Requirement: Unsupported native launch assumptions are tested
ChangeRail MUST keep unsupported native Windows launch assumptions visible in
its deterministic entrypoint coverage.

#### Scenario: Extensionless POSIX launch is considered
- **WHEN** the focused entrypoint smoke evaluates native Windows helper launch
  assumptions
- **THEN** it records direct extensionless POSIX helper launch as unsupported
  for native Windows defaults
- **AND** it does not treat implicit Bash availability as required for native
  Windows support

### Requirement: Entrypoint verification evidence
ChangeRail MUST record concrete command/outcome evidence for native Windows
entrypoint verification.

#### Scenario: Delivery records verification
- **WHEN** the native Windows entrypoint card is delivered
- **THEN** card, task or manifest evidence names the focused entrypoint smoke
  command and observed outcome
- **AND** the primary Linux release baseline outcome is recorded
- **AND** live Windows host smoke is recorded as passed evidence or as an
  explicit blocker/caveat without claiming unsupported proof

### Requirement: Native Windows bootstrap entrypoint
ChangeRail MUST provide a tracked native Windows `.cmd` wrapper for the
bootstrap helper used to create generated-copy consumer projects.

#### Scenario: Maintainer inspects bootstrap wrapper
- **WHEN** a maintainer inspects the tracked `bin/` helper surface
- **THEN** `bin/bootstrap-project.cmd` exists
- **AND** it routes execution through `changerail-python.cmd`
- **AND** it propagates the helper exit code

#### Scenario: Clean-clone lifecycle invokes bootstrap natively
- **WHEN** the Windows clean-clone lifecycle proof bootstraps a disposable
  consumer project
- **THEN** it uses the cloned `bootstrap-project.cmd` native entrypoint
- **AND** it does not require direct execution of the extensionless POSIX
  `bin/bootstrap-project` script
