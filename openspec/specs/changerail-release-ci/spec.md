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
ChangeRail release CI MUST разделять Linux-focused stable admission и тяжёлое
regression coverage. Default push/pull-request workflow MUST владеть только
точным упорядоченным `core` inventory, который выводит
`python3 scripts/run-release-baseline.py --suite core --list`. Отдельный
scheduled/manual workflow MUST вызывать ровно
`python3 scripts/run-release-baseline.py --suite extended` и MUST владеть только
точным упорядоченным `extended` inventory. Оба inventory MUST отклонять
missing, extra, duplicate или overlapping commands, а one-command delivery
regression `python3 scripts/smoke-delivery-runner.py` MUST принадлежать только
`extended`.

Command identity MUST задаваться как exact argv, а не shell-equivalent prose.
Упорядоченный `core` inventory MUST быть ровно таким:

1. `["./bin/openspec", "validate", "--all", "--strict"]`
2. `["python3", "-m", "json.tool", ".mcp.json"]`
3. `["python3", "-c", "import tomllib; tomllib.load(open('.codex/config.toml', 'rb')); print('TOML_OK')"]`
4. `["python3", "scripts/smoke-codex-launcher.py"]`
5. `["python3", "scripts/smoke-contract-schemas.py"]`
6. `["python3", "scripts/compile-python-inventory.py"]`
7. `["python3", "scripts/smoke-python-runtime.py"]`
8. `["ruff", "check", "bin", "scripts"]`
9. `["python3", "scripts/smoke-source-distribution.py"]`
10. `["python3", "scripts/smoke-release-ci.py"]`
11. `["python3", "scripts/public-surface-scan.py", "--self-test"]`
12. `["python3", "scripts/smoke-public-surface-history.py"]`
13. `["python3", "scripts/public-surface-scan.py"]`
14. `["python3", "scripts/public-surface-scan.py", "--history"]`
15. `["python3", "scripts/smoke-wiring-discovery.py"]`
16. `["python3", "scripts/smoke-verify-project.py"]`
17. `["python3", "scripts/smoke-runtime-diagnostics.py"]`
18. `["python3", "scripts/smoke-bootstrap-project.py"]`
19. `["python3", "scripts/smoke-consumer-ci.py"]`
20. `["rm", "-rf", ".runtime/changerail/ci-drift"]`
21. `["./bin/bootstrap-project", ".runtime/changerail/ci-drift/example-project", "--name", "example-project", "--kind", "generic", "--lock-enforcement", "none"]`
22. `["python3", "scripts/smoke-drift.py", "--project", ".runtime/changerail/ci-drift/example-project"]`
23. `["git", "diff", "--check"]`
24. `["git", "status", "--short", "--ignored"]`

Упорядоченный `extended` inventory MUST быть ровно таким:

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

Windows entrypoint, wiring Git-safety и aggregate matrix commands MUST
оставаться explicit opt-in diagnostics вне обеих suites.

#### Scenario: Core focused smoke coverage regresses
- **WHEN** tracked default workflow или runner теряет, добавляет, переставляет
  или дублирует required core command
- **THEN** `scripts/smoke-release-ci.py` завершается с ошибкой до принятия
  workflow change

#### Scenario: Default CI invokes core runner
- **WHEN** tracked default push/pull-request workflow запускается после
  dependency setup
- **THEN** он вызывает ровно `python3 scripts/run-release-baseline.py`
- **AND** не вызывает extended suite или принадлежащий ей smoke напрямую

#### Scenario: Extended focused smoke coverage regresses
- **WHEN** tracked extended workflow отсутствует, теряет schedule/manual trigger
  или больше не вызывает exact extended suite command
- **THEN** `scripts/smoke-release-ci.py` завершается с ошибкой
- **AND** default CI не поглощает и не дублирует extended coverage неявно

#### Scenario: Suite command ownership regresses
- **WHEN** command назначена обоим inventory, добавлена undeclared command или
  удалена expected command
- **THEN** CI contract smoke завершается fail-closed

#### Scenario: One-command delivery ownership regresses
- **WHEN** `python3 scripts/smoke-delivery-runner.py` отсутствует в extended или
  появляется в default core
- **THEN** exact inventory oracle завершается с ошибкой
- **AND** release evidence не может утверждать, что какая-либо suite прошла

### Requirement: Release CI lint gate
ChangeRail release CI MUST run a pinned lint gate for tracked Python helpers and
scripts.

#### Scenario: Unused import reaches release gate
- **WHEN** `ruff check bin scripts` reports an unused import or equivalent
  lint failure
- **THEN** release CI exits non-zero before publish

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
