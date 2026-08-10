## ADDED Requirements

### Requirement: Portable POSIX wiring path modes
POSIX symlink bootstrap MUST support `absolute` and `relative` wiring path modes.
Independent consumer bootstrap MUST default to absolute targets resolved from
the declared ChangeRail root, while relative targets MUST require explicit
operator opt-in.

#### Scenario: Independent POSIX consumer uses default wiring
- **WHEN** an operator bootstraps a POSIX consumer without a path-mode override
- **THEN** generated symlinks target the resolved declared ChangeRail root
- **AND** moving the consumer checkout alone does not change the target meaning

#### Scenario: Operator selects relative workspace wiring
- **WHEN** an operator passes `--wiring-path-mode relative`
- **THEN** bootstrap records that explicit path mode in tracked intent
- **AND** dry-run reports the relative topology requirement

#### Scenario: Path mode is incompatible with backend
- **WHEN** an operator supplies a POSIX path mode for an incompatible backend
- **THEN** bootstrap exits non-zero before target mutation

### Requirement: Consumer source and wiring lock generation
Bootstrap MUST support a tracked `openspec/changerail-consumer-lock.json` that
validates as `changerail.consumer-lock.v1`. Locked modes MUST record ChangeRail
version/revision, canonical source reference, wiring intent, selected profiles
and enforcement without machine-local paths or credential-bearing URLs.

#### Scenario: Advisory lock is generated
- **WHEN** bootstrap uses a clean tracked ChangeRail source and advisory lock
  enforcement
- **THEN** it writes a schema-valid public-safe consumer lock

#### Scenario: Strict lock is generated
- **WHEN** bootstrap uses strict lock enforcement
- **THEN** the lock records an exact Git revision suitable for CI reproduction

#### Scenario: Source checkout is dirty
- **WHEN** locked bootstrap sees uncommitted ChangeRail source changes
- **THEN** it fails before target mutation and does not claim a reproducible
  revision

### Requirement: Manifest-owned POSIX wiring refresh
Bootstrap MUST refresh or repair POSIX wiring only for paths declared by the
consumer lock and MUST fail closed on project-owned content, scope escape,
symlink parent escape or unrelated dirty state.

#### Scenario: Disposable checkout is relocated
- **WHEN** lock-driven refresh is run with the same revision at a new declared
  ChangeRail root
- **THEN** only known symlink targets are updated
- **AND** verification can proceed without manual rewiring

#### Scenario: Owned path contains a real file
- **WHEN** a declared wiring path contains project-owned non-symlink content
- **THEN** refresh exits non-zero without replacing that content
