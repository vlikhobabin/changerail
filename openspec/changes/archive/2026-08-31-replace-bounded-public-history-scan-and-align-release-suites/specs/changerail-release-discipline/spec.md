## MODIFIED Requirements

### Requirement: Release docs name reproducible local baseline
ChangeRail release discipline documentation MUST name the Linux-focused core
release baseline command, MUST name the separate exact extended regression
command and MUST describe their relationship to the default and
scheduled/manual CI routes.

#### Scenario: Maintainer prepares a release
- **WHEN** a maintainer reads release discipline docs before publish
- **THEN** the docs identify `python3 scripts/run-release-baseline.py` as the
  default core admission command
- **AND** the docs identify
  `python3 scripts/run-release-baseline.py --suite extended` as the separate
  heavy regression command required before release publish
- **AND** the docs identify any trusted-network checks outside both public-safe
  suites

### Requirement: Release baseline includes one-command delivery regression
The ChangeRail release discipline MUST require deterministic one-command
delivery regression coverage only in the extended release suite. The default
core baseline MUST NOT execute that regression. The exact normative invocation
MUST be `python3 scripts/run-release-baseline.py --suite extended`, and its
inventory MUST include `python3 scripts/smoke-delivery-runner.py` exactly once.

#### Scenario: Maintainer runs default core admission
- **WHEN** a maintainer runs `python3 scripts/run-release-baseline.py`
- **THEN** core does not execute `scripts/smoke-delivery-runner.py`
- **AND** core remains limited to Linux-focused stable-admission ownership

#### Scenario: Maintainer runs extended regression
- **WHEN** a maintainer runs
  `python3 scripts/run-release-baseline.py --suite extended`
- **THEN** extended executes the one-command delivery regression smoke with
  success, transient preflight resume and fail-closed review-gated scenarios
- **AND** release documentation lists that coverage only in the extended
  inventory

#### Scenario: Normative ownership drifts
- **WHEN** docs, CI inventory or another normative requirement assigns the
  one-command delivery regression to default core or removes it from extended
- **THEN** release verification fails closed before publish

### Requirement: Native Windows support claim release gate
ChangeRail release-facing documentation MUST identify the current stable
support claim as Linux-focused and MUST state that native Windows is not
release-certified while Windows admission gates remain opt-in. Before
publishing a future native Windows support claim, documentation MUST require
final Windows proof, public-surface scans and both Linux release suites.

#### Scenario: Maintainer prepares current stable release
- **WHEN** native Windows is outside the reviewed support claim
- **THEN** release and compatibility documentation explicitly state the
  Linux-focused admission boundary and native Windows caveat
- **AND** missing Windows matrix evidence does not block current core or
  extended release verification

#### Scenario: Maintainer prepares Windows support claim
- **WHEN** maintainer documentation describes native Windows support readiness
- **THEN** it names the live clean-clone lifecycle proof command or aggregate
  live matrix command
- **AND** it names `python3 scripts/run-release-baseline.py`
- **AND** it names
  `python3 scripts/run-release-baseline.py --suite extended` and current/history
  public-surface scans

#### Scenario: Final proof is missing or blocked
- **WHEN** the final clean-clone proof is missing, stale or blocked
- **THEN** release-facing docs require an explicit blocker/caveat before any
  native Windows support claim is published
