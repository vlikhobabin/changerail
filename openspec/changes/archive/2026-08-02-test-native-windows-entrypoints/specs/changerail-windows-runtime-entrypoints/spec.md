## ADDED Requirements

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
