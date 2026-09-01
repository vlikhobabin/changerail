# changerail-release-discipline Specification

## Purpose

Зафиксировать release discipline для ChangeRail как самостоятельной публичной
технологии: semver, changelog, compatibility notes и migration notes.
## Requirements
### Requirement: Semantic version source

ChangeRail MUST publish the current project version in a root `VERSION` file using
semantic version format `MAJOR.MINOR.PATCH`.

#### Scenario: Maintainer checks current version
- **WHEN** a maintainer reads `VERSION`
- **THEN** the file contains exactly one semantic version string
- **AND** release docs explain how pre-1.0 and stable releases use semver

### Requirement: Changelog with breaking markers

ChangeRail MUST maintain a root `CHANGELOG.md` that records public changes by
version and marks breaking changes explicitly.

#### Scenario: Consumer checks whether an update is breaking
- **WHEN** a consumer reads changelog entries for a target ChangeRail version
- **THEN** any breaking workflow, schema, template, skill, command or helper
  change is marked with a `BREAKING:` prefix
- **AND** non-breaking additions and fixes are grouped separately from breaking
  entries

### Requirement: Release publication bundle
ChangeRail release discipline MUST publish each public release as a coherent
versioned bundle that includes version source, changelog entries, migration
notes and compatibility notes.

#### Scenario: Maintainer publishes a pre-stable minor release
- **WHEN** a maintainer prepares a pre-stable minor release
- **THEN** `VERSION` MUST contain the target semantic version
- **AND** `CHANGELOG.md` MUST include a dated section for that version
- **AND** migration guide MUST include a version-to-version entry or explicitly
  say that no consumer action is required

#### Scenario: Release has no tool compatibility changes
- **WHEN** a release changes workflow policy without changing executable tool
  pins
- **THEN** compatibility notes MUST still identify the current ChangeRail
  version
- **AND** they MUST not imply that MCP, Codex, Claude or OpenSpec pins changed

### Requirement: Versioned release metadata
Before publishing a ChangeRail release, release metadata MUST name the release
version, summarize user-facing changes since the previous release, include
operator migration notes and pass the local release baseline.

#### Scenario: Release metadata is ready
- **WHEN** a maintainer publishes a ChangeRail release
- **THEN** `VERSION`, `CHANGELOG.md`, compatibility notes and migration guide
  all identify the release version
- **AND** `CHANGELOG.md` has an empty `Unreleased` section for future work
- **AND** the release card records the verification commands and observed
  outcomes used before publish

### Requirement: Tool compatibility notes
ChangeRail MUST document compatibility expectations for Codex CLI, Claude Code and
OpenSpec CLI.
Compatibility notes MUST document executable MCP dependency pins and their
tracked integrity source and trusted setup verification.
Compatibility notes MUST identify approved optional browser MCP package pins
without presenting them as default bootstrap or root ChangeRail dependencies.

#### Scenario: Operator prepares to update local tools
- **WHEN** an operator reviews ChangeRail compatibility notes
- **THEN** the notes identify Codex CLI, Claude Code and OpenSpec CLI support
  status
- **AND** the OpenSpec CLI compatibility note references the pin used by
  `bin/openspec`

#### Scenario: Maintainer reviews MCP supply-chain pins
- **WHEN** a maintainer reads ChangeRail compatibility notes
- **THEN** the notes identify the exact npm MCP package pins and the tracked
  integrity lock used to audit them
- **AND** the notes identify approved optional browser MCP package pins
- **AND** the notes identify the `verify-project`/`npm view` trusted setup
  check that compares tracked integrity with npm registry metadata

### Requirement: Migration notes between versions
ChangeRail MUST maintain migration notes for version-to-version updates that affect
consumer projects or operator workflow.
Workflow contract changes MUST have migration notes even when symlink-based
consumer projects do not need tracked file rewiring.
Release discipline MUST describe how maintainers update executable dependency
pins in a reviewable way.
Release verification MUST include security disclosure policy and public-safety
checks for public ChangeRail releases.

#### Scenario: Consumer updates ChangeRail
- **WHEN** a consumer moves from one ChangeRail version to another
- **THEN** migration notes describe required update steps, verification gates
  and rollback considerations
- **AND** migration examples use public generic paths only

#### Scenario: Consumer updates workflow policy only
- **WHEN** a release changes lifecycle skill behavior, review/publish gates or
  autonomous agent policy without changing consumer tracked files
- **THEN** migration notes describe session restart, verification commands and
  local-copy refresh steps
- **AND** changelog marks breaking workflow contract changes with `BREAKING:`

#### Scenario: Maintainer updates executable dependency pins
- **WHEN** a release updates default or approved optional npm MCP package pins
  or CI action SHAs
- **THEN** release docs describe the update command, verification commands and
  review expectations
- **AND** optional browser MCP package upgrades are documented as explicit
  release work rather than silent consumer adoption changes

#### Scenario: Release checks security disclosure policy
- **WHEN** a maintainer prepares a public ChangeRail release
- **THEN** release verification confirms that tracked security disclosure
  policy exists and is linked from public docs
- **AND** public-safety scans pass for the final tracked payload

### Requirement: Security disclosure policy
ChangeRail MUST maintain a tracked public security disclosure policy for
reporting vulnerabilities without publishing sensitive details.

#### Scenario: Public user reports a vulnerability
- **WHEN** a public user reads `SECURITY.md`
- **THEN** the policy identifies supported versions, preferred private
  disclosure channel and report content guidelines
- **AND** it tells reporters not to include secrets, credentials, exploit
  payloads or private workspace details in public issues

### Requirement: Product rename migration notes
ChangeRail release discipline MUST treat the OPSX to ChangeRail rename as a
breaking migration for consumers.

#### Scenario: Consumer reads rename release notes
- **WHEN** a consumer reads the release notes for the rename version
- **THEN** the notes mark source path, command namespace, skill namespace,
  helper and schema namespace changes as breaking where applicable
- **AND** the notes describe `/opt/changerail` as the canonical source-of-truth
  path

#### Scenario: Operator renames the GitHub repository
- **WHEN** the GitHub repository is renamed from `opsx` to `changerail`
- **THEN** migration docs describe updating local `origin` to the new
  repository URL
- **AND** old repository URLs are treated as compatibility redirects, not
  canonical documentation targets

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

### Requirement: Public release docs reflect current surface
ChangeRail public release docs MUST describe tracked runner, metrics, schema,
manifest, review-history, public-safety and finalization surfaces as current
when those files are present in the repository.

#### Scenario: Consumer reads current status
- **WHEN** a consumer reads `README.md`, `CHANGELOG.md`, compatibility notes or
  migration guide
- **THEN** implemented delivery runner, metrics, manifest/review contracts,
  aliases, public-safety scan helper and publish finalization behavior are not
  described as future planned work

### Requirement: Drift command documentation
Release and user-facing docs MUST describe `scripts/smoke-drift.py` as an
inventory-driven gate unless it is invoked through a generated public-safe
fixture wrapper or baseline command.

#### Scenario: Maintainer runs drift check manually
- **WHEN** the maintainer follows public docs for workspace drift
- **THEN** the docs show `--config`, `--workspace-root` or `--project`
  invocation
- **AND** local release baseline docs explain that generated fixture coverage is
  used for public CI/local smoke

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

### Requirement: First stable release candidate has an explicit clean core scope
ChangeRail MUST build the first stable release candidate from the exact
published generic core reference and MUST exclude dirty, forensic, rejected or
explicitly deferred payloads unless each additional payload completes its own
scoped delivery, verification and independent review before release metadata is
prepared.

#### Scenario: Maintainer prepares the first stable release candidate
- **WHEN** a maintainer starts preparation of the first stable ChangeRail
  release
- **THEN** the candidate starts from the exact published `origin/main`
  reference
- **AND** local branch or worktree existence does not admit a payload into the
  candidate
- **AND** phase-routed delivery and runtime artifact retention remain outside
  the candidate while their board cards are explicitly deferred
- **AND** core and extended release suites complete sequentially in an isolated
  clone containing only release-reachable refs before version, tag or
  distribution publication

#### Scenario: Deferred or forensic work appears locally
- **WHEN** the release workspace can observe dirty, forensic, rejected or
  deferred work outside the candidate branch
- **THEN** that work MUST NOT be merged, staged, described as released or used
  as verification evidence solely because it exists locally
- **AND** machine-specific inventory remains ignored runtime evidence
- **AND** any later inclusion requires a separate scoped card, verification and
  fresh review

#### Scenario: Linked worktree shares unrelated local refs
- **WHEN** an implementation worktree shares a Git directory with forensic,
  rejected or deferred local refs
- **THEN** it is not used as the final reachable-history proof
- **AND** the exact candidate filesystem is verified in an isolated clone whose
  refs are limited to the release candidate lineage
- **AND** current-file scans still inspect the exact candidate payload while
  history scans inspect every commit reachable from the future release ref

#### Scenario: Stable release metadata work begins
- **WHEN** the clean core candidate has green core and extended suites and
  deferred work is absent from its tracked payload
- **THEN** version, changelog, compatibility, migration, tag and distribution
  metadata are prepared by a separate final-certification release card
- **AND** a scope-normalization card does not itself authorize release
  publication

### Requirement: First stable post-commit resume boundary investigation decision
ChangeRail MUST опубликовать отдельное decision-only investigation перед
bounded authorization exact successor, который устраняет недостижимый
post-commit publication resume entry первого stable release.

#### Scenario: Final review blocker is classified before replacement delivery
- **WHEN** final predecessor review установил, что normal current-worktree
  freshness и dirty scope gates безусловно выполняются для clean payload commit
- **THEN** investigation MUST зафиксировать state-specific normal/resume entry
  boundary и committed lineage/scope/remote proofs
- **AND** оно MUST сохранить normal pre-staging gates и существующую exact
  release identity machine
- **AND** оно MUST NOT реализовывать successor, создавать release objects,
  менять schemas/source classification или выдавать inline/free-form waiver

#### Scenario: Exact successor requires a separate bounded authorization
- **WHEN** measured predecessor baseline равен 299 added production-counted LOC
  и минимальный successor forecast равен 359..399
- **THEN** hard successor ceiling MUST быть 400 cumulative added
  production-counted LOC
- **AND** отдельный published authorization MUST связать investigation
  `investigate-post-commit-release-resume-entry-boundary` с exact successor
  `enable-post-commit-release-resume-entry`
- **AND** authorization MUST объявить `production_loc_ceiling: 400` и
  `allow_new_authority_or_wire_protocol: false`
- **AND** authorization-card MUST объявить
  `investigate-post-commit-release-resume-entry-boundary` в `Depends On`
- **AND** exact successor MUST объявить тот же investigation id в `Depends On`
  в дополнение к two-field published authorization reference
- **AND** canonical deterministic preflight MUST проверить обе dependency edges
  и fail closed при missing или mismatched relation
- **AND** measurement 401 или больше MUST остановить successor для split или
  нового investigation без ослабления classification или regression floor

#### Scenario: Successor implementation boundary remains minimal and observable
- **WHEN** exact successor получает matching clean published authorization
- **THEN** implementation MUST ограничиться early pub/deliver routing,
  read-only committed target существующего manifest helper, focused committed
  scope и wiring probes, существующими specs и release docs
- **AND** implementation MUST NOT добавлять workflow, provider, credential
  type, execution target, wire schema или новую mutation authority
- **AND** focused probes MUST наблюдать разные normal/resume gate sets и
  fail-closed wrong lineage, scope, card, remote и release identity outcomes

#### Scenario: Exact successor reaches final review
- **WHEN** bounded successor готов к independent review
- **THEN** deterministic preflight MUST принять exact published authorization,
  cumulative LOC не выше 400 и единый manifest всего successor payload
- **AND** на одном exact tree MUST последовательно пройти core, extended и
  release-CI suites, public/history scans, dependency integrity, reproducible
  distribution и strict config/OpenSpec/diff checks
- **AND** fresh-context xhigh review MUST проверить тот же exact tree до любой
  publication mutation
