# Changelog

Все публичные изменения ChangeRail фиксируются в этом файле.

Формат следует release discipline ChangeRail: версии используют semver, а breaking
changes помечаются префиксом `BREAKING:`.

## Unreleased

### Added
- none

### Changed
- none

### Fixed
- none

### Breaking
- none

## 1.0.0 - 2026-09-01

### Added
- Добавлены contracts для declared execution-target identity,
  verification-coverage plans/ledgers, retained external-blocker resume,
  recovery-aware delivery episodes и public source classification.
- Добавлен risk-aware deterministic review preflight с machine/ordinary/
  critical routing, bounded complexity authorization и fresh independent
  semantic review gate.
- Добавлен воспроизводимый generic source distribution: exact Git archive,
  version/license/source-revision metadata, SHA-256 sidecar, tracked builder и
  core release smoke.

### Changed
- Release verification разделена на последовательные exact core и extended
  suites; public history scan ограничен release-reachable refs и проверяется в
  isolated clone exact candidate.
- Delivery runner и manifest gates теперь строже проверяют remote target,
  scoped paths, staged rename, child authority, bounded discovery, structured
  progress и fail-closed resume/finalization handoffs.
- Первый stable release ограничен reviewed generic core; phase-routed delivery
  и runtime artifact retention остаются deferred до отдельного post-release
  triage.

### Fixed
- Исправлены remote-preflight parity, unpublished child outcomes, malformed
  review handoffs, manifest staged-scope reconciliation и containment
  parent-owned runtime evidence.
- Исправлены false-positive/timeout границы reachable-history scan и ownership
  one-command delivery regression между core/extended suites.

### Breaking
- BREAKING: declared execution target запрещает неявную замену provider,
  platform, service или database на delivery/verification/review/publish пути.
- BREAKING: final publish требует risk-appropriate fresh review; process
  defects исправляются до semantic review, а bounded rescue exhaustion ведет к
  linked rescue/investigation вместо исключительного in-place continuation.
- BREAKING: consumer lock с предыдущей source revision не ремонтируется blind
  `--refresh-wiring`; принятие новой ChangeRail revision является отдельной
  reviewed consumer migration.

## 0.5.0 - 2026-08-11

### Added
- Added tracked repository knowledge and maintenance contracts: catalog,
  generated index, policy, deterministic scan/report/triage, baseline/waiver,
  card preview/deduplication, feedback normalization and quality rollup.
- Added `bin/changerail-maintenance`, `bin/changerail-maintenance-runner`,
  native `.cmd` wrappers, `changerail-maintain`/`chrl-maintain` Codex skills
  and Claude command wrappers for read-only audit and bounded triage.
- Added maintenance opt-in bootstrap templates, public scheduler examples and
  an end-to-end maintenance operations runbook for consumer repositories.
- Added `changerail.consumer-lock.v1`, bootstrap topology/profile controls,
  opt-in generated consumer CI and greenfield README/Git initialization
  support.
- Added static Codex instruction-budget checks and opt-in runtime diagnostics
  smoke coverage.

### Changed
- `bootstrap-project` now uses canonical profile/surface/Codex policy options,
  defaults new POSIX wiring to absolute symlink targets, can write advisory or
  strict consumer locks, and limits `--configure-existing` to explicit
  allowlisted actions.
- `verify-project` now validates consumer locks, generated wiring ownership,
  maintenance opt-in contracts, maintenance schemas, instruction budgets and
  optional runtime diagnostics more explicitly.
- The release baseline and CI contract now include repository-knowledge,
  maintenance-runner, runtime-diagnostics, consumer-CI and expanded schema
  coverage.
- Compatibility, migration, adoption, wiring and contract docs now cover the
  maintenance surface and portable consumer bootstrap model.

### Fixed
- Fixed maintenance opt-in bootstrap so a fresh `--with-maintenance` consumer
  passes `validate-catalog`, `render-index --check` and `scan --json` without
  manual catalog/index edits.
- Fixed greenfield bootstrap safety around existing projects, generated-owned
  refresh, project-owned files, local Git initialization and no implicit
  stage/commit/push behavior.
- Fixed consumer verification gaps for missing or stale maintenance quality and
  proposal-decision schemas.
- Fixed release/public-surface fixtures so generated docs and clean-clone
  smokes stay public-safe and deterministic.

### Breaking
- BREAKING: New consumer bootstrap defaults now render Codex
  `safe-interactive` authority instead of implicit trusted automation.
  Unattended automation must pass `--codex-policy trusted-automation`
  explicitly.

## 0.4.0 - 2026-08-02

### Added
- Added a shared Python runtime selector `bin/changerail-python` plus
  `.cmd` entrypoints for the supported helper surface, including bootstrap,
  OpenSpec, verification, review verdict, retained evidence, delivery runner
  and delivery metrics helpers.
- Added generated-copy native Windows project wiring with bootstrap refresh,
  verifier/drift ownership checks, Git-safety coverage and deterministic
  local fixtures.
- Added native Windows lab protocol, support matrix, smoke aggregation and
  two-host clean-clone lifecycle evidence for prepared operator-managed
  Windows hosts.
- Added retained delivery evidence indexing, manifest scope/handoff summaries,
  verification profiles, severity reporting and one-command delivery
  regression coverage.
- Added review-cycle rescue-budget metrics and aggregate queue status metrics.

### Changed
- Review verdict freshness now binds reviewed evidence to Git tree identity and
  diff fingerprints.
- Publish finalization now separates payload commits from published commits and
  keeps mutable publish ledger data in ignored manifests.
- Delivery runner preflight now proves remote publish targets, classifies
  failure causes and supports resume after a fresh transient remote proof.
- Delivery cards now have an explicit deliver-ready contract, and board series
  docs cover the release, delivery operations and Windows implementation waves.
- Compatibility, migration, adoption and release docs now include the native
  Windows generated-copy support claim and its prerequisites.

### Fixed
- Fixed skill frontmatter validation and publish-target preflight enforcement.
- Fixed stale/impossible publish finalization metadata and manifest handoff
  gaps.
- Fixed Windows probe cleanup/import issues and native launcher assumptions
  around extensionless POSIX wrappers, implicit Bash and unsafe staging.
- Fixed generated board template docs so clean-clone bootstrap smoke does not
  leak machine-local checkout paths.
- Fixed delivery contract smoke so custom/fake launchers do not require a
  locally installed `codex` binary in `PATH`; the default `bin/codex` launcher
  still requires `codex`.

### Breaking
- BREAKING: ChangeRail Python helper entrypoints now enforce Python `3.11+`
  and runtime dependencies from `requirements-runtime.txt` through
  `bin/changerail-python`.
- BREAKING: Review verdict freshness validation now requires tree/diff identity
  to match the reviewed workspace state.

## 0.3.0 - 2026-07-26

### Added
- Added consumer Codex auth setup support for unattended delivery: bootstrap
  opt-in auth marker symlink, `verify-project` delivery readiness advisory,
  runner remediation diagnostics and focused smoke coverage.
- Added locked approved optional browser MCP package metadata for
  `@playwright/mcp@0.0.68` and `chrome-devtools-mcp@0.20.3` without adding
  those packages to default ChangeRail config or templates.
- Added `bin/changerail-delivery-runner generate-plan` to produce
  schema-backed `changerail.delivery-plan.v1` queue plans from ordered card
  paths and optional dependencies.
- Added compact queue child preflight diagnostics in aggregate
  `preflight-plan` and `status-plan` output while retaining full child status
  references as ignored runtime evidence.

### Changed
- Delivery runner and lifecycle guidance now preserve
  `fix_budget_exhausted` as a non-delivered safety-stop reason, fail closed on
  unpublished child exit `0`, and resume queue recovery through explicit
  `recovery_for` cards before downstream work.
- Consumer documentation now distinguishes the plan runner, single-card runner
  and Codex launcher, and clarifies that a consumer repository does not need a
  tracked repo-local `bin/codex`.
- `verify-project` recognizes exact npm package pins passed as direct package
  arguments, `--package=<package>@<version>` and
  `--package <package>@<version>`.

### Fixed
- Fixed delivery runner aggregate preflight output that could hide actionable
  child failure details behind truncated nested JSON.
- Fixed consumer auth setup verification so tracked `.codex/auth.json` and
  `.codex/auth.toml` are rejected while ignored local markers remain allowed.
- Fixed release baseline coverage for consumer auth setup, optional browser MCP
  package forms and delivery-plan operator UX.

### Breaking
- none

## 0.2.0 - 2026-07-18

### Added
- Added release discipline docs: semver policy, compatibility notes and
  migration guide.
- Added initial release CI plan through OpenSpec change
  `add-release-ci-gate`.
- Added `bin/changerail-delivery-runner` for supervised single-card
  non-interactive delivery with structured runtime status records.
- Added `bin/changerail-delivery-metrics` for aggregate metrics from delivery
  run records and review-cycle history.
- Added public contract schemas for delivery run records and review-cycle
  history, plus schema-backed validation for review verdict and delivery
  manifest helpers.
- Added delivery manifest derivation/finalization helpers and review freshness
  fingerprint coverage.
- Added short daily aliases `$chrl-*` and `/chrl:*` while preserving canonical
  `changerail` runtime names.
- Added public-surface scan helper coverage for current files and reachable
  history.
- Added local release baseline command `scripts/run-release-baseline.py`,
  inventory-based Python compile checks, contract schema smoke, pinned
  `ruff`/`jsonschema` release tooling and focused runner/metrics/fingerprint
  CI smokes.

### Changed
- Renamed the public product/toolchain identity from OPSX to ChangeRail across
  docs, lifecycle skills, Claude commands, helpers, schemas, templates and
  smoke checks.
- Bumped pinned OpenSpec CLI `1.3.0` -> `1.3.1` in `bin/openspec` and refreshed
  `skills/openspec-*` via `openspec update` (sharper `contextFiles` guidance in
  apply-change/verify-change). Updated compatibility and lifecycle docs.
- Clarified review-gated publish finalization: delivery leaves reviewed cards in
  `3.inprogress`, and publish records deterministic board metadata after a
  fresh `go` verdict and scoped commit.
- Changed autonomous repeated `NO-GO` handling: default same-card rescue budget
  is now five bounded rescue/review cycles, and exhausted budgets escalate to a
  linked rescue/replacement or investigation card instead of a manual
  exceptional-authorization stop.
- Documented `scripts/smoke-drift.py` as an inventory-driven gate; release CI
  and the local baseline use generated public-safe fixtures.

### Fixed
- Fixed release CI drift where runner, metrics, review fingerprint, schema
  validation and lint coverage were not all part of the mandatory gate.
- Fixed stale public documentation that still treated tracked bootstrap,
  verify, template and script surfaces as planned work.

### Breaking
- BREAKING: OPSX source path, command namespace, skill namespace, helper names,
  runtime namespace and schema ids are renamed to ChangeRail. Consumers must
  migrate `/opt/opsx`, `/opsx:*`, `$opsx-*`, `bin/opsx-*`,
  `.runtime/opsx` and `opsx.*.v1` wiring to the ChangeRail equivalents.
- BREAKING: The default repeated `NO-GO` workflow contract changed from two
  scoped rescue attempts plus manual exceptional authorization to five bounded
  same-card rescue attempts followed by autonomous linked rescue/replacement
  or investigation card escalation. Consumers with local copied skills or
  runbooks must refresh them; active agent sessions must be restarted to load
  the new policy.

## 0.1.0 - 2026-07-08

### Added
- Initial public ChangeRail baseline: shared methodology, lifecycle skills, Claude
  command wrappers, OpenSpec lifecycle helpers, contract schemas, project
  templates, bootstrap, verify-project, drift gate and wiring smoke.

### Changed
- none

### Fixed
- none

### Breaking
- none
