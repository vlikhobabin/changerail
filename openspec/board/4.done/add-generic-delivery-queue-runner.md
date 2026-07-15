# Добавить generic delivery queue runner

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Operational feedback from multi-repository ChangeRail consumers.
- `docs/how-it-works.md`
- `docs/consumer-adoption-runbook.md`
- `docs/changerail-contracts.md`
- `openspec/specs/changerail-delivery-runner/spec.md`

## Summary
ChangeRail имеет надёжный non-interactive single-card runner, но consumer,
которому нужно провести dependency-ordered delivery через несколько независимых
git workspaces, вынужден писать собственный supervisor. Нужен generic,
public-safe queue-aware orchestration contract: consumer-owned declarative plan,
DAG/wave scheduling, полный preflight до первой live карточки, safe resume и
агрегированный structured status, при этом каждая карточка по-прежнему должна
запускаться существующим single-card runner и сохранять отдельный run record.

## Acceptance
- Tracked CLI предоставляет явные plan-oriented команды (`plan`,
  `preflight-plan`, `run-plan`, `resume-plan`, `status-plan`) либо эквивалентный
  отдельный queue helper, если design доказывает, что так лучше сохраняется
  compatibility существующего single-card interface.
- Consumer-owned declarative JSON plan валидируется по tracked public schema и
  описывает workspaces, cards, dependencies, waves и concurrency limits. YAML
  допускается только как optional extension без обязательной новой runtime
  dependency.
- Tracked schema и public examples используют workspace aliases или
  consumer-root-relative paths; credentials, secrets, machine-local state и
  machine-specific absolute paths в plan не допускаются.
- Validation fail-closed обнаруживает cycle, duplicate card, ambiguous card,
  missing card/workspace/dependency, invalid wave/dependency relation и
  несовместимые concurrency settings до первого live child launch.
- Card resolution выполняется по stable filename/card id и повторяется после
  board moves; missing, duplicate или canceled card останавливает plan.
- Карточки внутри одного workspace выполняются строго последовательно;
  параллельность разрешена только между dependency-independent workspaces и
  ограничена `max_parallel` и `per_workspace_parallelism`.
- Wave barriers и cross-workspace dependencies соблюдаются детерминированно;
  `plan`/list и dry-run выводят resolved cards, dependencies, waves и команды
  без запуска delivery children.
- `preflight-plan` проверяет все workspaces, git/card state и single-card runner
  readiness до первого live запуска. Любой fail оставляет очередь
  незапущенной и пишет structured aggregate status.
- Каждый live card вызывает существующий single-card runner, получает отдельный
  `changerail.delivery-run.v1` record и не меняет его compatibility contract.
- Queue runtime state содержит plan fingerprint, per-card state/run record
  references, aggregate status и terminal outcome без scraping свободного
  текста; runtime logs/status/locks остаются ignored.
- Resume не переиздаёт уже успешно опубликованные карточки, повторно разрешает
  ещё не завершённые карточки после board moves и fail-closed проверяет
  fingerprint и repository state перед продолжением.
- Workspace lock исключает два одновременных live run в одном repository;
  stale lock даёт безопасную диагностику и не удаляется автоматически без
  доказуемого безопасного условия или явного operator action.
- Queue fail-fast останавливается на terminal `NO-GO`, `BLOCKED`, stale/invalid
  verdict, push rejection, unexpected dirty scope или inconsistent card state
  и не запускает новые downstream cards.
- В push-enabled режиме card success признаётся только при `DELIVERED`, единственной
  card location под `openspec/board/4.done`, clean owning repository и
  `HEAD == upstream`.
- При explicit `--no-push` success требует committed clean tree и ожидаемого
  ahead-of-upstream состояния, записанного в status; режим явно передаётся
  каждому single-card invocation.
- Plan поддерживает per-card model/reasoning overrides, не меняя repository
  defaults.
- Aggregate metrics читают structured queue/card records и существующий
  delivery metrics surface без parsing произвольного текста.
- Public docs описывают создание plan, list/preflight/dry-run/live/resume/status,
  locks, terminal outcomes, push/no-push success и generic multi-workspace
  example только с путями `/opt/example-*`.
- Existing single-card CLI, schemas, smoke tests и consumer wiring остаются
  backward compatible.

## Change Set
- `openspec/changes/archive/2026-07-15-define-delivery-plan-contracts/`
- `openspec/changes/archive/2026-07-15-add-delivery-plan-preflight/`
- `openspec/changes/archive/2026-07-15-add-delivery-plan-run-resume/`

## Verify
- Fast-forward planning:
  - `./bin/openspec validate define-delivery-plan-contracts --strict` -> pass
  - `./bin/openspec validate add-delivery-plan-preflight --strict` -> pass
  - `./bin/openspec validate add-delivery-plan-run-resume --strict` -> pass
  - `./bin/openspec validate --all --strict` -> pass, 16 passed / 0 failed
  - `git diff --check` -> pass for current tracked diff
- Delivery verification floor:
  - `python3 -m py_compile bin/changerail-delivery-runner` -> pass
  - `python3 -m py_compile bin/changerail-delivery-runner
    bin/changerail-delivery-metrics` -> pass
  - focused queue/runner smoke for validation, scheduling, dry-run, resume,
    locking, board re-resolution, terminal outcomes and push/no-push success
    -> covered by `python3 scripts/smoke-delivery-runner.py`, pass
  - `python3 scripts/smoke-delivery-metrics.py` -> pass
  - `python3 scripts/smoke-contract-schemas.py` -> pass, 7 schemas
  - `./bin/openspec validate add-delivery-plan-preflight --strict` -> pass
  - `./bin/openspec validate add-delivery-plan-run-resume --strict` -> pass
  - `./bin/openspec validate --all --strict` -> pass, 13 passed / 0 failed
  - `git diff --check`, включая новые untracked files -> pass
  - `python3 scripts/public-surface-scan.py` -> pass, 463 files / 0 findings
  - Review cycle 1 rescue fixes covered duplicate resolved card identity,
    dirty child workspace preflight, global workspace locks, strict
    `--no-push` ahead-of-upstream success, live per-card model/reasoning
    propagation and regression smoke coverage.
  - `python3 -m py_compile bin/changerail-delivery-runner
    bin/changerail-delivery-metrics scripts/smoke-delivery-runner.py
    scripts/smoke-delivery-metrics.py scripts/smoke-contract-schemas.py` ->
    pass after rescue fixes
  - `python3 scripts/smoke-delivery-runner.py` -> pass after rescue fixes
  - `python3 scripts/smoke-delivery-metrics.py` -> pass after rescue fixes
  - `python3 scripts/smoke-contract-schemas.py` -> pass after rescue fixes,
    7 schemas
  - `./bin/openspec validate --all --strict` -> pass after rescue fixes,
    13 passed / 0 failed
  - `git diff --check` -> pass after rescue fixes
  - `python3 scripts/public-surface-scan.py` -> pass after rescue fixes,
    463 files / 0 findings
  - `python3 scripts/run-release-baseline.py` -> pass after rescue fixes,
    25/25 steps
  - Test adequacy: runner smoke asserts dry-run/preflight/status output,
    fail-closed invalid plans, live child invocation, fail-fast `NO-GO`, lock
    preservation, resume skip logic, push/no-push success checks and existing
    single-card compatibility; metrics smoke asserts queue status ingestion and
    existing child run/review metrics. These tests observe CLI/status behavior
    and would fail if the claimed queue contracts regressed.
  - RED evidence: not claimed; focused tests and implementation were updated in
    the same supervised delivery pass.

## Archive
- `openspec/changes/archive/2026-07-15-define-delivery-plan-contracts/`
- `openspec/changes/archive/2026-07-15-add-delivery-plan-preflight/`
- `openspec/changes/archive/2026-07-15-add-delivery-plan-run-resume/`

## Related
- `bin/changerail-delivery-runner`
- `bin/changerail-delivery-metrics`
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- `scripts/smoke-delivery-runner.py`
- `scripts/smoke-delivery-metrics.py`
- `docs/how-it-works.md`
- `docs/consumer-adoption-runbook.md`
- `docs/changerail-contracts.md`
- `docs/compatibility.md`
- `docs/release-discipline.md`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-delivery-observability/spec.md`

## Result
Implemented generic queue plan contracts, plan/preflight/status commands,
live run/resume queue orchestration, aggregate status, locks, queue metrics and
public docs. Review cycle 1 returned `no-go`; all six findings were remediated
and the card is awaiting fresh independent re-review.

Published reviewed payload as `f43d3bc54b057d3b20602e23e0b1873a2e56f096`; push status `pending` on `main`/`origin`.

## Next
- done

## Change 1: `define-delivery-plan-contracts`

### Why
Consumer projects need a public, declarative queue plan contract before any
multi-workspace runner can be implemented safely. The contract must be
consumer-owned, generic and schema-validated without embedding credentials,
secrets or machine-specific absolute paths.

### Goal
Define the queue plan and aggregate status wire contracts, update the relevant
ChangeRail specs, and make schema validation cover the new public contracts.

### Scope
- Add public Draft 2020-12 schemas for `changerail.delivery-plan.v1` and
  `changerail.delivery-plan-status.v1`.
- Extend ChangeRail contract/spec docs with queue plan and queue status
  semantics.
- Add schema smoke fixtures and public-safety constraints for workspace aliases,
  cards, dependencies, waves, concurrency limits, run records and terminal
  outcomes.

### Acceptance
- Schemas reject credentials, machine-local absolute workspace paths, duplicate
  identifiers and malformed concurrency/status fields.
- Existing single-card delivery run schema remains unchanged and compatible.
- Contract docs describe plan/status files as public schema contracts while
  keeping runtime status/logs ignored.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-15-define-delivery-plan-contracts/`

## Change 2: `add-delivery-plan-preflight`

### Why
Operators need deterministic plan listing, dry-run resolution and full preflight
diagnostics before the first live child delivery starts.

### Goal
Add plan-oriented runner commands for resolving, validating, dry-running,
preflighting and inspecting queue plans without launching child deliveries.

### Scope
- Add explicit plan-oriented CLI commands to `bin/changerail-delivery-runner`
  while preserving existing `run <single-card>` and `preflight <single-card>`
  behavior.
- Implement stable card resolution by filename/id across board moves, duplicate
  and canceled-card checks, DAG/wave validation and concurrency validation.
- Write structured aggregate status for plan/list/preflight/status operations.

### Acceptance
- `plan`/dry-run output lists resolved workspaces, cards, dependencies, waves
  and single-card runner commands without launching live children.
- `preflight-plan` fails closed on cycle, duplicate card, ambiguous card,
  missing card/workspace/dependency, invalid wave/dependency relation and
  incompatible concurrency before any live child launch.
- `status-plan` reads aggregate status without scraping raw logs.

### Depends On
- `define-delivery-plan-contracts`

### Related
- `openspec/changes/archive/2026-07-15-add-delivery-plan-preflight/`

## Change 3: `add-delivery-plan-run-resume`

### Why
A queue helper must supervise live child runner invocations safely across
independent repositories, with deterministic resume behavior and fail-fast
terminal outcomes.

### Goal
Implement live `run-plan` and `resume-plan` orchestration, workspace locks,
structured aggregate status, success criteria and metrics/docs integration.

### Scope
- Invoke the existing single-card runner once per live card and retain each
  card's separate `changerail.delivery-run.v1` record.
- Schedule dependency-independent workspaces up to `max_parallel`, keep cards
  within one workspace sequential, and enforce wave/dependency barriers.
- Implement workspace locks, fail-fast terminal outcome handling, safe resume
  fingerprint checks and push/no-push success validation.
- Update metrics and public docs for plan lifecycle, locks, resume, outcomes,
  push/no-push success and generic multi-workspace examples.

### Acceptance
- Live queue runs stop on `NO-GO`, `BLOCKED`, stale/invalid verdict, push
  rejection, unexpected dirty scope or inconsistent card state and do not launch
  downstream cards.
- Resume skips already successful published/committed cards, re-resolves
  unfinished cards after board moves and rejects mismatched plan fingerprint or
  repository state.
- Aggregate metrics read structured queue/card records without parsing arbitrary
  text.

### Depends On
- `define-delivery-plan-contracts`
- `add-delivery-plan-preflight`

### Related
- `openspec/changes/archive/2026-07-15-add-delivery-plan-run-resume/`

## Log
- 2026-07-15T00:00:00Z card created for generic multi-workspace queue-aware
  orchestration while preserving the existing single-card runner contract.
- 2026-07-15T04:24:42Z fast-forward planned three changes
  (`define-delivery-plan-contracts`, `add-delivery-plan-preflight`,
  `add-delivery-plan-run-resume`), created apply-ready OpenSpec artifacts and
  moved card to `3.inprogress` for delivery.
- 2026-07-15T04:51:15Z implemented all three changes, synced specs, archived
  OpenSpec changes, ran focused smokes plus release baseline, and left card in
  `3.inprogress` for independent review.
- 2026-07-15T05:09:51Z review cycle 1 returned `no-go` for duplicate resolved
  card detection, missing dirty workspace preflight, per-run lock scope,
  weak `--no-push` success, missing live model/reasoning overrides and smoke
  gaps; implemented scoped rescue fixes and reran focused smokes, public scan
  and release baseline successfully.
- 2026-07-15T05:17:56Z publish finalized card into `4.done` with commit `f43d3bc54b057d3b20602e23e0b1873a2e56f096` and push status `pending`.
