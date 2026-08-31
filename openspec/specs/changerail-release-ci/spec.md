# changerail-release-ci Specification

## Purpose

Зафиксировать release-facing CI gate для ChangeRail: OpenSpec validation,
docs/config checks, Python smoke checks, templates/bootstrap/verify/drift and
wiring discovery.
## Requirements
### Requirement: Release CI workflow
ChangeRail MUST provide a tracked CI workflow that runs the release verification
baseline on pushes, pull requests and manual dispatch.
Release CI MUST run the strengthened public-surface scan for current public
roots and reachable history.

#### Scenario: CI runs for repository changes
- **WHEN** the ChangeRail CI workflow is triggered by `push`, `pull_request` or
  `workflow_dispatch`
- **THEN** it runs OpenSpec validation, docs/config parsing checks and Python
  syntax checks
- **AND** it exits non-zero when any required command fails

#### Scenario: CI runs strengthened public-safety scan
- **WHEN** the ChangeRail CI workflow runs
- **THEN** it runs the public-surface scanner self-test
- **AND** it runs the scanner against current public roots and reachable
  history

### Requirement: Template and bootstrap smoke in CI

ChangeRail CI MUST exercise project templates and bootstrap/verify behavior through
red/green smoke commands.

#### Scenario: Template or bootstrap drift breaks generated projects
- **WHEN** template, bootstrap or verification wiring is broken
- **THEN** the CI workflow runs `scripts/smoke-verify-project.py` and
  `scripts/smoke-bootstrap-project.py`
- **AND** the workflow fails before release-facing changes can be accepted

### Requirement: Drift and wiring smoke in CI

ChangeRail CI MUST run drift and wiring discovery checks without requiring private
workspace inventory.

#### Scenario: CI checks drift and wiring safely
- **WHEN** CI reaches smoke verification
- **THEN** it runs `scripts/smoke-wiring-discovery.py`
- **AND** it runs `scripts/smoke-drift.py` against a generated generic runtime
  project
- **AND** committed workflow content contains no private workspace inventory

### Requirement: CI workflow contract smoke
ChangeRail MUST provide a local smoke check that validates the tracked CI workflow
contains the required release gates.
CI workflow contract smoke MUST require the strengthened scanner commands.

#### Scenario: Maintainer edits the workflow
- **WHEN** `python3 scripts/smoke-release-ci.py` runs
- **THEN** it fails if the CI workflow is missing required triggers or command
  strings
- **AND** it passes only when all required release gates are present

#### Scenario: CI smoke requires history scan command
- **WHEN** `python3 scripts/smoke-release-ci.py` runs
- **THEN** it fails if the CI workflow no longer invokes the scanner history
  mode

### Requirement: Release CI validates ChangeRail fixtures
Release CI MUST run bootstrap, verify, wiring and drift smoke against generated
ChangeRail fixtures after the rename.

#### Scenario: Release CI runs
- **WHEN** the release CI workflow executes after the rename
- **THEN** generated fixture paths and reports use the ChangeRail runtime
  namespace
- **AND** release smoke fails if generated defaults still use OPSX wiring

### Requirement: CI covers generated workflow guidance
Release CI MUST run bootstrap smoke coverage that fails when generated workflow
guidance drifts from the current ChangeRail process.

#### Scenario: Template workflow guidance regresses
- **WHEN** release CI runs `scripts/smoke-bootstrap-project.py`
- **THEN** missing lifecycle, role model, fresh review or board finalization
  guidance in generated files fails the CI smoke

### Requirement: Release CI inventory coverage
ChangeRail release CI MUST discover and compile tracked Python helper and smoke
files under `bin/` and `scripts/` from repository inventory instead of relying
on a manually maintained incomplete file list.

#### Scenario: New Python helper is tracked
- **WHEN** a Python helper or smoke script is tracked under `bin/` or `scripts/`
- **THEN** release CI includes that file in the syntax compile gate
- **AND** a syntax error in that file fails the release workflow

### Requirement: Release CI focused smoke inventory
ChangeRail release CI MUST run the focused smoke scripts that protect delivery
runner, delivery metrics, review fingerprint, review verdict validation,
review preflight,
manifest derivation, bootstrap, verify, wiring discovery, archive diagnostics,
release workflow contract and drift fixture behavior.

#### Scenario: Focused smoke coverage regresses
- **WHEN** the tracked CI workflow no longer invokes a required focused smoke
  command
- **THEN** `scripts/smoke-release-ci.py` fails before the workflow change can
  be accepted

### Requirement: Release CI lint gate
ChangeRail release CI MUST run a pinned lint gate for tracked Python helpers and
scripts.

#### Scenario: Unused import reaches release gate
- **WHEN** `ruff check bin scripts` reports an unused import or equivalent
  lint failure
- **THEN** release CI exits non-zero before publish

### Requirement: Local release baseline command
ChangeRail MUST provide a single local command that reproduces the mandatory
release CI baseline from the repository checkout and exits non-zero when any
mandatory check fails.

#### Scenario: Maintainer runs local release baseline
- **WHEN** a maintainer runs the documented local release baseline command
- **THEN** it executes OpenSpec validation, config parsing, schema validation,
  Python syntax inventory, lint, focused smoke checks, generated drift fixture,
  public-surface scans and whitespace checks
- **AND** the command returns non-zero if any required check fails

#### Scenario: Drift smoke needs inventory
- **WHEN** the local release baseline checks drift
- **THEN** it invokes `scripts/smoke-drift.py` with a generated public-safe
  project fixture rather than requiring no-argument drift behavior

### Requirement: Consumer Codex auth setup smoke coverage
ChangeRail release baseline MUST include focused smoke coverage for the
consumer Codex auth setup contract across bootstrap, verification and delivery
runner preflight surfaces.

#### Scenario: Release baseline checks auth setup contract
- **WHEN** the local release baseline or release CI focused smoke set runs
- **THEN** it covers bootstrap opt-in auth link behavior, verification readiness
  advisory behavior and delivery runner auth remediation diagnostics
- **AND** it does not require real Codex credentials

#### Scenario: Smoke keeps credentials out of output
- **WHEN** smoke tests create temporary fake auth marker contents
- **THEN** tracked test output and structured status assertions do not include
  credential contents or token-like values

### Requirement: Release baseline validates skill frontmatter
The local release baseline and release CI MUST include deterministic validation
for complete bundled skill YAML frontmatter.

#### Scenario: Maintainer runs local release baseline after skill edits
- **WHEN** `python3 scripts/run-release-baseline.py` runs
- **THEN** the mandatory focused smoke set parses all `skills/*/SKILL.md`
  frontmatter as YAML
- **AND** the command returns non-zero if any bundled skill frontmatter is
  invalid

#### Scenario: Release CI runs without Codex credentials
- **WHEN** the ChangeRail CI workflow executes the release baseline checks
- **THEN** skill frontmatter validation uses repository-local parser behavior
- **AND** it does not require a networked `codex exec` call or real Codex
  credentials

#### Scenario: String-only frontmatter parsing regresses
- **WHEN** the release baseline executes the wiring discovery smoke
- **THEN** the smoke includes a negative fixture for an unquoted `: ` scalar
- **AND** the baseline fails if the parser path accepts that fixture

### Requirement: Release baseline covers Python runtime selection
ChangeRail release baseline MUST include focused smoke coverage for shared
Python runtime selection and diagnostics.

#### Scenario: Runtime smoke covers supported and failing selectors
- **WHEN** `python3 scripts/smoke-python-runtime.py` runs
- **THEN** it verifies successful helper startup through a supported runtime
- **AND** it verifies old-version simulation, missing dependency simulation and
  invalid override diagnostics

#### Scenario: Local release baseline runs runtime smoke
- **WHEN** `python3 scripts/run-release-baseline.py` runs
- **THEN** it includes the focused Python runtime smoke in the mandatory step
  list

### Requirement: Release baseline covers Windows entrypoints
ChangeRail release baseline MUST include deterministic smoke coverage for
native Windows entrypoint wrapper contracts.

#### Scenario: Local release baseline runs Windows entrypoint smoke
- **WHEN** `python3 scripts/run-release-baseline.py` runs
- **THEN** it includes `python3 scripts/smoke-windows-entrypoints.py` in the
  mandatory step list
- **AND** the baseline fails if the focused smoke reports a wrapper inventory,
  argv, cwd, environment, exit-code or unsupported-launch finding

#### Scenario: Release CI workflow runs Windows entrypoint smoke
- **WHEN** the ChangeRail CI workflow executes release checks
- **THEN** it runs `python3 scripts/smoke-windows-entrypoints.py`
- **AND** `scripts/smoke-release-ci.py` treats that command as required CI
  inventory

### Requirement: Release baseline covers Windows wiring Git safety
The local release baseline and tracked CI smoke inventory MUST include focused
coverage for Windows wiring Git safety gates.

#### Scenario: Local baseline runs Windows wiring Git safety smoke
- **WHEN** `python3 scripts/run-release-baseline.py` runs
- **THEN** it executes the focused smoke command that validates generated,
  symlink and junction Git safety fixtures
- **AND** the baseline fails if the smoke reports unsafe status, dry-run add or
  index behavior

#### Scenario: CI workflow runs Windows wiring Git safety smoke
- **WHEN** the tracked ChangeRail CI workflow executes release checks
- **THEN** it runs the same focused Windows wiring Git safety smoke command
- **AND** `scripts/smoke-release-ci.py` treats that command as required CI
  inventory

### Requirement: Release baseline covers Windows smoke matrix
The local release baseline and tracked CI smoke inventory MUST include the
platform-neutral Windows smoke matrix contract.

#### Scenario: Local baseline runs Windows smoke matrix
- **WHEN** `python3 scripts/run-release-baseline.py` runs
- **THEN** it executes `python3 scripts/smoke-windows-matrix.py` as a mandatory
  step
- **AND** the baseline fails if the smoke matrix reports a failed mandatory
  local matrix item

#### Scenario: CI workflow runs Windows smoke matrix
- **WHEN** the tracked ChangeRail CI workflow executes release checks
- **THEN** it runs `python3 scripts/smoke-windows-matrix.py`
- **AND** `scripts/smoke-release-ci.py` treats that command as required CI
  inventory

### Requirement: Generated consumer CI regression gate
The ChangeRail release baseline and tracked CI MUST validate the generated
consumer workflow contract and execute a local clean-clone fixture against an
exact strict consumer lock.

#### Scenario: Release baseline runs consumer CI smoke
- **WHEN** `python3 scripts/run-release-baseline.py` executes
- **THEN** it includes structured validation of the generated workflow
- **AND** it includes the local strict-lock clean-clone consumer fixture

#### Scenario: Workflow uses a floating ChangeRail reference
- **WHEN** the template no longer reads an exact lock revision
- **THEN** release CI smoke fails

#### Scenario: Workflow gains write authority
- **WHEN** the template adds repository write, commit, push or publish behavior
- **THEN** release CI smoke fails before release publication

### Requirement: Consumer CI failure fixtures
Release smoke MUST cover absent/malformed/advisory locks, unavailable revision,
owned wiring conflict and successful exact-revision verification.

#### Scenario: CI negative matrix runs
- **WHEN** focused consumer CI smoke executes
- **THEN** every unsafe or non-reproducible fixture exits non-zero
- **AND** the successful fixture proves the same local and CI verification path

### Requirement: Bounded release-reachable public history scan
ChangeRail release baseline MUST scan every unique public blob reachable from
the single fully resolved release `HEAD` commit, MUST preserve commit/path
attribution for findings and MUST keep Git process launches constant with
respect to commit, path and blob cardinality. The history scan MUST NOT include
unrelated local refs and MUST fail closed when full reachable history or valid
Git framing cannot be proven. Raw history MUST use config-independent
`--format=tformat:%x1e%H` commit markers with NUL-terminated raw fields and MUST
validate marker, header and path states before accepting a history pass.

#### Scenario: Release checkout contains unrelated local refs
- **WHEN** history mode runs in a complete checkout whose `HEAD` has reachable
  public history and another local ref contains unrelated history
- **THEN** the scanner checks every unique public blob reachable from resolved
  `HEAD`
- **AND** it does not make the release result depend on the unrelated ref

#### Scenario: A public blob is reused across commits and paths
- **WHEN** the same blob object is reachable at multiple public commit/path
  occurrences
- **THEN** the scanner reads and applies public-safety rules to that blob once
- **AND** any finding retains existing structured commit/path attribution

#### Scenario: Git framing or lifecycle is incomplete
- **WHEN** raw history or batch-object framing is malformed, truncated,
  unexpected or a required Git process fails
- **THEN** history mode returns a structured redacted history finding and a
  non-zero result
- **AND** it does not emit a pass or expose raw blob or token-like content

#### Scenario: Release history verification is bounded
- **WHEN** the public-safe 250-commit regression fixture is scanned
- **THEN** history enumeration uses no more than three Git process launches and
  completes within 30 seconds
- **AND** the complete clean-checkout release baseline completes within 300
  seconds

#### Scenario: Existing scanner safety behavior is retained
- **WHEN** current-tree, history, binary, invalid UTF-8 and secret-redaction
  regression fixtures run
- **THEN** current public roots and every release-reachable unique text blob are
  checked with the existing detection rules
- **AND** binary/invalid UTF-8 handling remains unchanged while secret-redaction
  failures remain fail closed at the release gate
