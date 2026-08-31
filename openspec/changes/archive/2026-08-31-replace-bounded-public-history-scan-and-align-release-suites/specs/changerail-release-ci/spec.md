## MODIFIED Requirements

### Requirement: Release CI focused smoke inventory
ChangeRail release CI MUST separate Linux-focused stable admission from heavy
regression coverage. The default push/pull-request workflow MUST own only the
exact ordered `core` inventory exposed by
`python3 scripts/run-release-baseline.py --suite core --list`. A separate
scheduled/manual workflow MUST invoke exactly
`python3 scripts/run-release-baseline.py --suite extended` and MUST own only the
exact ordered `extended` inventory. Both inventories MUST reject missing,
extra, duplicate or overlapping commands, and the one-command delivery
regression `python3 scripts/smoke-delivery-runner.py` MUST belong only to
`extended`.

Command identity MUST be exact argv, not shell-equivalent prose. The ordered
`core` inventory MUST be exactly:

1. `["./bin/openspec", "validate", "--all", "--strict"]`
2. `["python3", "-m", "json.tool", ".mcp.json"]`
3. `["python3", "-c", "import tomllib; tomllib.load(open('.codex/config.toml', 'rb')); print('TOML_OK')"]`
4. `["python3", "scripts/smoke-contract-schemas.py"]`
5. `["python3", "scripts/compile-python-inventory.py"]`
6. `["python3", "scripts/smoke-python-runtime.py"]`
7. `["ruff", "check", "bin", "scripts"]`
8. `["python3", "scripts/smoke-release-ci.py"]`
9. `["python3", "scripts/public-surface-scan.py", "--self-test"]`
10. `["python3", "scripts/smoke-public-surface-history.py"]`
11. `["python3", "scripts/public-surface-scan.py"]`
12. `["python3", "scripts/public-surface-scan.py", "--history"]`
13. `["python3", "scripts/smoke-wiring-discovery.py"]`
14. `["python3", "scripts/smoke-verify-project.py"]`
15. `["python3", "scripts/smoke-runtime-diagnostics.py"]`
16. `["python3", "scripts/smoke-bootstrap-project.py"]`
17. `["python3", "scripts/smoke-consumer-ci.py"]`
18. `["rm", "-rf", ".runtime/changerail/ci-drift"]`
19. `["./bin/bootstrap-project", ".runtime/changerail/ci-drift/example-project", "--name", "example-project", "--kind", "generic", "--lock-enforcement", "none"]`
20. `["python3", "scripts/smoke-drift.py", "--project", ".runtime/changerail/ci-drift/example-project"]`
21. `["git", "diff", "--check"]`
22. `["git", "status", "--short", "--ignored"]`

The ordered `extended` inventory MUST be exactly:

1. `["python3", "scripts/smoke-review-verdict-validation.py"]`
2. `["python3", "scripts/smoke-review-fingerprint.py"]`
3. `["python3", "scripts/smoke-review-fingerprint-benchmark.py"]`
4. `["python3", "scripts/smoke-review-fingerprint-cache.py"]`
5. `["python3", "scripts/smoke-review-preflight.py"]`
6. `["python3", "scripts/smoke-retained-evidence.py"]`
7. `["python3", "scripts/smoke-maintenance-runner.py"]`
8. `["python3", "scripts/smoke-delivery-manifest.py"]`
9. `["python3", "scripts/smoke-delivery-manifest-derive.py"]`
10. `["python3", "scripts/smoke-delivery-runner.py"]`
11. `["python3", "scripts/smoke-delivery-metrics.py"]`
12. `["python3", "scripts/smoke-openspec-archive-diagnostics.py"]`

Windows entrypoint, wiring Git-safety and aggregate matrix commands MUST remain
explicit opt-in diagnostics outside both suites.

#### Scenario: Core focused smoke coverage regresses
- **WHEN** the tracked default workflow or runner loses, adds, reorders or
  duplicates a required core command
- **THEN** `scripts/smoke-release-ci.py` fails before the workflow change can be
  accepted

#### Scenario: Default CI invokes core runner
- **WHEN** the tracked default push/pull-request workflow runs after dependency
  setup
- **THEN** it invokes exactly `python3 scripts/run-release-baseline.py`
- **AND** it does not invoke the extended suite or an extended-owned smoke
  directly

#### Scenario: Extended focused smoke coverage regresses
- **WHEN** the tracked extended workflow is missing, loses its schedule/manual
  trigger or no longer invokes the exact extended suite command
- **THEN** `scripts/smoke-release-ci.py` fails
- **AND** default CI does not silently absorb or duplicate extended coverage

#### Scenario: Suite command ownership regresses
- **WHEN** a command is assigned to both inventories, an undeclared command is
  added, or an expected command is removed
- **THEN** the CI contract smoke fails closed

#### Scenario: One-command delivery ownership regresses
- **WHEN** `python3 scripts/smoke-delivery-runner.py` is missing from extended
  or appears in default core
- **THEN** the exact inventory oracle fails
- **AND** release evidence cannot claim either suite passed

### Requirement: Local release baseline command
ChangeRail MUST provide one local runner with explicit non-overlapping `core`
and `extended` suites. Default invocation MUST run the mandatory Linux-focused
core stable admission and exit non-zero when any core check fails. The exact
extended invocation
`python3 scripts/run-release-baseline.py --suite extended` MUST run the retained
heavy regression inventory without repeating core checks. `--list` MUST emit
the selected deterministic ordered inventory without executing it, and a
combined `all` suite MUST NOT be provided.

#### Scenario: Maintainer runs default local release baseline
- **WHEN** a maintainer runs `python3 scripts/run-release-baseline.py`
- **THEN** it executes only core OpenSpec, config, schema, syntax, lint,
  public-safety, wiring, verify, runtime, bootstrap, consumer-CI, generated
  drift and repository-integrity checks
- **AND** it returns non-zero if any core check fails

#### Scenario: Maintainer runs extended local regression suite
- **WHEN** a maintainer runs
  `python3 scripts/run-release-baseline.py --suite extended`
- **THEN** it executes only review, retained-evidence, delivery, maintenance
  and archive-diagnostics regressions
- **AND** it executes `python3 scripts/smoke-delivery-runner.py` exactly once

#### Scenario: Maintainer audits suite ownership
- **WHEN** a maintainer requests `--list` for either suite
- **THEN** the runner emits a deterministic ordered command inventory
- **AND** core and extended have no missing, extra, duplicate or common command

#### Scenario: Drift smoke needs inventory
- **WHEN** the local release baseline checks drift
- **THEN** it invokes `scripts/smoke-drift.py` with a generated public-safe
  project fixture rather than requiring no-argument drift behavior

### Requirement: Release baseline covers Windows entrypoints
ChangeRail MUST retain deterministic smoke coverage for native Windows
entrypoint wrapper contracts as an explicit opt-in diagnostic. The default
Linux-focused release baseline, extended suite and tracked CI workflows MUST
NOT execute this Windows-only smoke until native Windows returns to the reviewed
support claim.

#### Scenario: Maintainer runs Windows entrypoint diagnostic explicitly
- **WHEN** a maintainer prepares a native Windows capability change or future
  support claim
- **THEN** they can run `python3 scripts/smoke-windows-entrypoints.py`
- **AND** the command fails on wrapper inventory, argv, cwd, environment,
  exit-code or unsupported-launch findings

#### Scenario: Release suites run
- **WHEN** default core or extended executes for the current Linux-focused claim
- **THEN** neither suite executes `scripts/smoke-windows-entrypoints.py`
- **AND** syntax and lint inventory continue to cover the retained script

### Requirement: Release baseline covers Windows wiring Git safety
ChangeRail MUST retain focused Windows wiring Git-safety smoke as an explicit
opt-in diagnostic. The default Linux-focused release baseline, extended suite
and tracked CI workflows MUST NOT execute this Windows-only smoke until native
Windows returns to the reviewed support claim.

#### Scenario: Maintainer runs Windows wiring diagnostic explicitly
- **WHEN** a maintainer changes generated, symlink or junction Windows wiring
- **THEN** they can run `python3 scripts/smoke-windows-wiring-git-safety.py`
- **AND** the command fails on unsafe status, dry-run add or index behavior

#### Scenario: Release suites run
- **WHEN** current default core or extended executes
- **THEN** neither suite executes
  `scripts/smoke-windows-wiring-git-safety.py`
- **AND** the retained script remains covered by syntax and lint inventory

### Requirement: Release baseline covers Windows smoke matrix
ChangeRail MUST retain the platform-neutral and live Windows smoke matrix as an
explicit opt-in diagnostic. The default Linux-focused release baseline,
extended suite and tracked CI workflows MUST NOT execute the aggregate matrix
until a reviewed native Windows support claim is restored.

#### Scenario: Maintainer requests Windows matrix evidence
- **WHEN** a maintainer explicitly runs `python3 scripts/smoke-windows-matrix.py`
- **THEN** the matrix executes its configured local or live Windows evidence
  path
- **AND** it fails when a mandatory matrix item fails

#### Scenario: Release suites run
- **WHEN** current default core or extended executes
- **THEN** neither suite executes `scripts/smoke-windows-matrix.py`
- **AND** CI contract smoke fails if the command is silently restored without
  a reviewed contract update

### Requirement: Bounded release-reachable public history scan
ChangeRail release baseline MUST scan every unique public blob reachable from
the single fully resolved release `HEAD` commit, MUST preserve commit/path
attribution for findings and MUST keep Git process launches constant with
respect to commit, path and blob cardinality. The history scan MUST NOT include
unrelated local refs and MUST fail closed when full reachable history or valid
Git framing cannot be proven. Raw history MUST use config-independent
`--format=tformat:%x1e%H` commit markers with NUL-terminated raw fields and MUST
validate marker, header, path, object mode/type and status transitions before
accepting a history pass. The mandatory core release baseline MUST run
`python3 scripts/smoke-public-surface-history.py`.

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

#### Scenario: Raw mode or framing is invalid
- **WHEN** raw history contains a malformed marker/header/path state, invalid
  mode/status/OID transition, extra field or truncated record
- **THEN** history mode returns a structured redacted history finding and a
  non-zero result
- **AND** it does not accept the record or expose raw framing bytes

#### Scenario: Git lifecycle times out or exits non-zero
- **WHEN** resolve, raw-history or batch-object processing times out, exits
  non-zero, closes early or fails a pipe operation
- **THEN** history mode returns a generic redacted finding and non-zero result
- **AND** it does not emit a pass or copy stderr/blob content into the report

#### Scenario: Release history verification is bounded
- **WHEN** the public-safe 250-commit regression fixture is scanned
- **THEN** history enumeration uses no more than three Git process launches and
  completes within 30 seconds
- **AND** the complete clean-checkout core release baseline completes within
  300 seconds

#### Scenario: Core release baseline runs bounded-history regression
- **WHEN** `python3 scripts/run-release-baseline.py` runs
- **THEN** it executes `python3 scripts/smoke-public-surface-history.py` as a
  mandatory core check
- **AND** the baseline fails when semantic, framing, lifecycle or process-count
  oracle fails

#### Scenario: Release CI checks complete history
- **WHEN** either tracked release-suite workflow checks out the repository
- **THEN** its pinned checkout requests `fetch-depth: 0`
- **AND** `scripts/smoke-release-ci.py` fails if the full-checkout contract is
  lost

#### Scenario: Existing scanner safety behavior is retained
- **WHEN** current-tree, history, binary, invalid UTF-8 and secret-redaction
  regression fixtures run
- **THEN** current public roots and every release-reachable unique text blob are
  checked with the existing detection rules
- **AND** binary/invalid UTF-8 handling remains unchanged while
  secret-redaction failures remain fail closed at the release gate
