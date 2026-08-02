## ADDED Requirements

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
- **AND** it does not require direct extensionless POSIX launch or implicit Bash

#### Scenario: Pinned OpenSpec launch fails
- **WHEN** the pinned OpenSpec invocation cannot start
- **THEN** `openspec.cmd` exits non-zero
- **AND** the failure is attributable to the pinned OpenSpec launch path rather
  than an implicit fallback to another shell or unpinned binary
