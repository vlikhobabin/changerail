# Укрепить delivery pipeline для повторяемой эксплуатации

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived

## Source
- Практика supervised delivery нескольких OPSX-карточек через независимый
  review gate (2026-07), обобщенная до generic public-safe требований.
- `docs/how-it-works.md`
- `README.md`
- `openspec/board/README.md`
- `AGENTS.shared.md`
- `skills/opsx-do/SKILL.md`
- `skills/opsx-deliver/SKILL.md`
- `skills/opsx-review/SKILL.md`
- `skills/opsx-pub/SKILL.md`
- `schemas/opsx-delivery-manifest.schema.json`
- `schemas/opsx-delivery-run.schema.json`
- `schemas/opsx-review-cycle-history.schema.json`
- `schemas/opsx-review-verdict.schema.json`

## Summary
Сделать публичный OPSX delivery pipeline воспроизводимым не только на уровне
agent methodology, но и при реальной длительной эксплуатации. Зафиксировать
однозначный lifecycle карточки, полноту publish scope при перемещениях файлов,
проектно-объявленный verification floor, generic non-interactive runner со
структурированным статусом и метрики, основанные на машинных run records.

Карточка не меняет базовый порядок `ff -> do -> review -> pub`. OpenSpec changes
остаются архивированными до review, чтобы reviewer видел полный delivery
payload и freshness fingerprint не менялся перед его commit. При этом board
card остается в `3.inprogress` до успешного publish и переходит в `4.done`
только как детерминированная post-publish финализация.

## Motivation
- `opsx-do`, `opsx-review` и `opsx-pub` задают основные gates, но недостаточно
  явно разделяют archive change и завершение story на доске. Это допускает
  преждевременный перенос карточки в `4.done` до review или publish.
- Delivery manifest хранит committable paths, но не выражает операции
  `add`/`modify`/`delete`/`rename`. При переносе карточки между колонками
  удаление исходного board path может потеряться из claimed publish scope.
- Generic workflow обязан выполнять весь verification floor, объявленный
  проектом и OpenSpec artifacts, однако не должен безусловно навязывать каждому
  consumer одинаковые formatter, type checker или environment matrix.
- `bin/codex` уже передает Codex CLI аргументы, включая model/config overrides,
  но OPSX не предоставляет tracked runner contract для per-run overrides,
  terminal outcomes и наблюдения за длительным запуском.
- Runtime-логи и latest review verdict недостаточны для надежной аналитики:
  нет стабильного run record с model/effort, фазами, временем, usage и историей
  review cycles. Метрики не должны зависеть от скрейпинга свободного текста.
- Эксплуатационные случаи `CODEX_HOME`, auth/permissions, proxy connectivity,
  разрешения бинаря и закрытого stdin для фонового `codex exec` не описаны в
  публичном runbook.

## Acceptance
- Lifecycle contract и skills однозначно задают состояния story: `opsx-do`
  реализует, проверяет, синхронизирует и архивирует changes, но оставляет
  карточку в `3.inprogress`; independent review проверяет полный delivery
  payload; `opsx-pub` после свежего `go` публикует этот payload без
  содержательных code/docs/spec edits и затем финализирует карточку в `4.done`
  по документированному post-publish протоколу. Любое содержательное изменение
  после `go` инвалидирует verdict и требует re-review; детерминированные board
  metadata отделены от reviewed payload.
- Delivery manifest contract представляет удаление и rename обоими путями или
  эквивалентной структурированной операцией. Перемещение board card формирует
  полный staging proposal, включающий старый и новый path, и покрыто smoke-тестом.
- Verification contract требует выполнить все обязательные команды из
  `AGENTS.md`, `openspec/config.yaml`, tasks/design и затронутого toolchain с
  записанным outcome. Formatter, strict typing и clean/ambient environment
  matrix обязательны только когда объявлены проектом или следуют из измененного
  surface. Для измененных тестов сохраняется проверка, что тест способен упасть
  при заявленном регрессе и наблюдает нужный источник поведения.
- Добавлен tracked generic non-interactive runner или эквивалентный helper,
  который запускает delivery без private workspace assumptions, закрывает stdin,
  поддерживает per-run `model` и `reasoning_effort` через штатные Codex CLI
  overrides и сохраняет текущее поведение при отсутствии overrides.
- Runner атомарно пишет машинно-проверяемый runtime status/run record как
  минимум с `card`, `phase`, `result`, timestamps и `commit` при наличии.
  Терминальные исходы `DELIVERED`, `NO-GO` и `BLOCKED` одинаково явны;
  supervisor наблюдает status record, а не `pgrep` или свободный текст лога.
- Run records сохраняют доступные model/effort, wall-time и token usage, а review
  evidence сохраняет историю циклов без потери предыдущего `no-go`. Latest
  canonical verdict остается совместимым с publish freshness gate.
- Tracked metrics tool читает структурированные run records и review-cycle
  evidence, печатает per-run и aggregate результаты (first-pass go rate,
  findings по severity, acceptance outcomes, wall-time и доступный token usage)
  и поддерживает CSV. Отсутствующие необязательные поля отображаются явно, а не
  угадываются из логов.
- Public runbook описывает launcher/background-agent preflight: реальную
  connectivity-проверку proxy, композицию `CODEX_HOME`, stale symlinks и права,
  поиск Codex binary, auth state, закрытый stdin и диагностику по status record.
  Все примеры используют только `/opt/opsx`, `/opt/example-*` и placeholders.
- `docs/how-it-works.md` или `AGENTS.shared.md` содержит worked flow
  `over-claim -> no-go -> scoped rescue -> re-review -> go -> pub`, объясняет
  archive-before-review, hold-push-until-review и проектно-объявленный
  verification floor.

## Change Set
- `harden-delivery-lifecycle-contract`
- `declare-delivery-verification-floor`
- `add-generic-delivery-runner`
- `add-delivery-observability`

## Verify
- `./bin/openspec validate harden-delivery-lifecycle-contract --strict` - passed
- `./bin/openspec validate declare-delivery-verification-floor --strict` - passed
- `./bin/openspec validate add-generic-delivery-runner --strict` - passed
- `./bin/openspec validate add-delivery-observability --strict` - passed
- `python3 scripts/smoke-delivery-manifest.py` - passed
- `python3 scripts/smoke-delivery-runner.py` - passed
- `python3 scripts/smoke-delivery-metrics.py` - passed
- `python3 -m json.tool schemas/opsx-delivery-manifest.schema.json` - passed
- `python3 -m json.tool schemas/opsx-delivery-run.schema.json` - passed
- `python3 -m json.tool schemas/opsx-review-cycle-history.schema.json` - passed
- `./bin/openspec validate --all --strict` - passed
- `git diff --check` - passed
- Public-surface scan on local username markers, private absolute paths,
  credential markers, fixed local host/ports and runtime payload leakage -
  passed with no hits.
- Pre-fix review gate:
  `python3 scripts/opsx_review_verdict.py validate .runtime/opsx/reviews/harden-delivery-operations.json --check-fresh --workspace . --json`
  - passed; verdict was fresh and `result: no-go` for cycle-1 blockers R1-R7.
- Cycle-1 rescue coverage for R1-R7:
  `python3 scripts/smoke-delivery-runner.py` - passed; regression probes cover
  non-default `--workspace` child cwd, `CODEX_WORKDIR`, default
  `CODEX_HOME=<workspace>/.codex`, workspace `commit`, structured
  `external-review/no-go`, structured `awaiting-review`, printed terminal
  outcome, auth diagnostics and stale symlink preflight.
- Cycle-1 rescue coverage for review history:
  `python3 scripts/smoke-delivery-metrics.py` - passed; fixture retains prior
  no-go finding ids/details after a later go cycle and surfaces `R1;R2;R3`.
- Cycle-1 rescue schema/docs checks:
  `python3 -m json.tool schemas/opsx-delivery-manifest.schema.json`,
  `python3 -m json.tool schemas/opsx-delivery-run.schema.json` and
  `python3 -m json.tool schemas/opsx-review-cycle-history.schema.json` -
  passed.
- `python3 scripts/smoke-delivery-manifest.py` - passed after rescue changes.
- `./bin/openspec validate --all --strict` - passed; 13 specs passed, 0 failed.
- `git diff --check` - passed after rescue changes.
- Full `AGENTS.md` docs/config baseline rerun:
  `python3 -m json.tool .mcp.json` - passed (`MCP_JSON_OK`);
  TOML parse for `.codex/config.toml` - passed (`TOML_OK`);
  `git diff --check` - passed;
  `git status --short --ignored` - completed and showed card-owned dirty paths
  plus ignored runtime/local paths (`.runtime/`, `.codex/tmp/`,
  `.claude/settings.local.json`, `internal/`, `__pycache__/`) still ignored.
- Public-surface scan on local username markers, private absolute paths,
  credential/token markers and fixed local host/ports - passed
  (`PUBLIC_SURFACE_SCAN_OK`).
- Pre-fix review gate cycle 2:
  `python3 scripts/opsx_review_verdict.py validate .runtime/opsx/reviews/harden-delivery-operations.json --check-fresh --workspace . --json`
  - passed; verdict was fresh and `result: no-go` for cycle-2 blockers R1-R2.
- Cycle-2 rescue coverage for R1-R2:
  `python3 scripts/smoke-delivery-runner.py` - passed; regression probes cover
  non-OPSX git cwd invocation with both `--workspace` and `--runtime-root`
  omitted, default runtime root under `<workspace>/.runtime/opsx/delivery-runs`,
  child cwd, `CODEX_WORKDIR`, default `CODEX_HOME=<workspace>/.codex`,
  workspace `commit`, and command-run preflight failure printing
  `terminal_outcome: BLOCKED` before the status path.
- Cycle-2 rescue project verification floor:
  `./bin/openspec validate --all --strict` - passed; 13 specs passed,
  0 failed.
  `python3 scripts/smoke-delivery-manifest.py` - passed.
  `python3 scripts/smoke-delivery-runner.py` - passed.
  `python3 scripts/smoke-delivery-metrics.py` - passed.
  `python3 -m json.tool .mcp.json` plus delivery manifest/run/history schemas -
  passed (`JSON_OK`).
  TOML parse for `.codex/config.toml` - passed (`TOML_OK`).
  `git diff --check` - passed.
  Untracked-file whitespace scan over `git ls-files --others
  --exclude-standard` - passed (`UNTRACKED_WHITESPACE_OK`).
  `git status --short --ignored` - completed and showed card-owned dirty paths
  plus ignored runtime/local paths still ignored.
  Public-surface scan on existing public files for local username markers,
  private absolute paths, credential/token assignments and fixed local
  host/ports - passed (`PUBLIC_SURFACE_SCAN_OK`).

## Archive
- `openspec/changes/archive/2026-07-11-harden-delivery-lifecycle-contract/`
- `openspec/changes/archive/2026-07-11-declare-delivery-verification-floor/`
- `openspec/changes/archive/2026-07-11-add-generic-delivery-runner/`
- `openspec/changes/archive/2026-07-11-add-delivery-observability/`

## Public Surface / Consumer Impact
- Затрагивает generic methodology, lifecycle skills, schemas/contracts, tracked
  scripts и docs.
- Может расширить `opsx.*` runtime contracts; совместимость текущего
  `opsx.review-verdict.v1` publish gate должна быть сохранена или мигрирована
  явно.
- Consumer-проекты получают opt-in runner/metrics surface; default model и
  reasoning effort не меняются без per-run override.
- Machine-local runners, inventories, raw logs, verdicts и status files остаются
  ignored runtime state и не переносятся в public source.

## Related
- `docs/how-it-works.md`
- `docs/opsx-contracts.md`
- `README.md`
- `openspec/board/README.md`
- `AGENTS.shared.md`
- `skills/opsx-do/SKILL.md`
- `skills/opsx-deliver/SKILL.md`
- `skills/opsx-review/SKILL.md`
- `skills/opsx-pub/SKILL.md`
- `schemas/opsx-delivery-manifest.schema.json`
- `schemas/opsx-delivery-run.schema.json`
- `schemas/opsx-review-cycle-history.schema.json`
- `schemas/opsx-review-verdict.schema.json`
- `openspec/changes/archive/2026-07-11-harden-delivery-lifecycle-contract/`
- `openspec/changes/archive/2026-07-11-declare-delivery-verification-floor/`
- `openspec/changes/archive/2026-07-11-add-generic-delivery-runner/`
- `openspec/changes/archive/2026-07-11-add-delivery-observability/`

## Result
planned changes implemented, verified, specs synced and archived; cycle-1
blockers R1-R7 fixed and verified; cycle-2 blockers R1-R2 fixed and verified;
external independent review cycle 3 returned a fresh `go`; scoped publish
completed with runtime review evidence excluded from tracked files

## Next
- Continue with the next OPSX board card.

## Change 1: `harden-delivery-lifecycle-contract`

### Why
`do`, `review` и `pub` должны одинаково понимать, что архивированный change не
делает story опубликованной, а board move должен попадать в publish scope.

### Goal
Зафиксировать archive-before-review, done-after-publish и structured manifest
file operations.

### Scope
- Methodology/docs lifecycle language.
- Delivery/review/publish skill contracts.
- Delivery manifest schema/reference/helper and move/delete smoke coverage.

### Acceptance
- `opsx-do` оставляет карточку в `3.inprogress` после archive.
- `opsx-pub` финализирует `4.done` только после свежего `go` и publish.
- Manifest staging proposal выражает add/modify/delete/rename.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-11-harden-delivery-lifecycle-contract/`

## Change 2: `declare-delivery-verification-floor`

### Why
Generic OPSX должен требовать все объявленные checks, но не навязывать каждому
consumer project один и тот же toolchain floor.

### Goal
Сделать verification floor проектно-объявленным и проверяемым через concrete
evidence claims.

### Scope
- Shared methodology.
- Delivery/review skill evidence language.
- Docs for command/outcome evidence and RED applicability.

### Acceptance
- Mandatory checks discoverable from project rules, OpenSpec artifacts and
  affected toolchain.
- Formatter/type/environment checks mandatory only when declared.
- Review flags unbacked mandatory evidence claims.

### Depends On
- `harden-delivery-lifecycle-contract`

### Related
- `openspec/changes/archive/2026-07-11-declare-delivery-verification-floor/`

## Change 3: `add-generic-delivery-runner`

### Why
Supervised non-interactive delivery needs a tracked runner with structured
status instead of local scripts and log scraping.

### Goal
Add a public-safe runner/status contract with per-run Codex overrides, closed
stdin and explicit terminal outcomes.

### Scope
- Runner helper under tracked public surface.
- `opsx.delivery-run.v1` schema.
- Runner smoke tests and operational runbook docs.

### Acceptance
- Runner launches `codex exec` through repo launcher in the effective
  workspace, resolves omitted `--workspace` to the invocation repo/cwd, makes
  omitted `--runtime-root` follow that workspace, sets
  `CODEX_WORKDIR`/effective `CODEX_HOME` coherently and closes stdin.
- Per-run `model` and `reasoning_effort` overrides do not mutate defaults.
- Status/run record has card, phase, result, timestamps, terminal outcome and
  `commit` when workspace `HEAD` is available.
- Structured `external-review/no-go` and `awaiting-review` output produce
  explicit printed `NO-GO`/`BLOCKED` terminal outcomes.

### Depends On
- `declare-delivery-verification-floor`

### Related
- `openspec/changes/archive/2026-07-11-add-generic-delivery-runner/`

## Change 4: `add-delivery-observability`

### Why
Latest verdict and raw logs do not preserve review-cycle history or support
stable metrics.

### Goal
Add review-cycle history and metrics from structured run/review evidence.

### Scope
- Review-cycle evidence schema/docs.
- Metrics helper with text and CSV output.
- Worked no-go rescue flow in methodology docs.

### Acceptance
- Previous `no-go` findings remain available after later `go` through retained
  finding details or immutable cycle snapshots.
- Metrics report first-pass go rate, findings, acceptance outcomes, wall-time
  and available token usage.
- Missing optional metrics render as `unknown`.

### Depends On
- `add-generic-delivery-runner`

### Related
- `openspec/changes/archive/2026-07-11-add-delivery-observability/`

## Log
- 2026-07-11 карточка создана по итогам практического многокарточного
  supervised-прогона; оставлена в `1.backlog` для triage.
- 2026-07-11 после аудита public surface scope актуализирован: archive до review
  сохранен как freshness-инвариант; `4.done` перенесен в post-publish
  финализацию; log scraping заменен structured run records; universal toolchain
  checks заменены project-declared verification floor; change plan сокращен до
  четырех связанных направлений.
- 2026-07-11T18:28:29Z `$opsx-ff` создал apply-ready OpenSpec artifacts для
  четырех ordered changes и подготовил карточку к delivery.
- 2026-07-11T18:44:54Z `$opsx-do` реализовал, проверил, синхронизировал specs
  и архивировал четыре planned changes; карточка оставлена в `3.inprogress`
  для external review.
- 2026-07-11T18:58:52Z external review cycle 1 вернул свежий `result: no-go`
  с blocker findings R1-R7; verdict validated before rescue changes.
- 2026-07-11T19:11:22Z scoped rescue исправил R1-R7: runner honoring
  `--workspace`/`CODEX_WORKDIR`/`CODEX_HOME`, top-level `commit`,
  structured `NO-GO`/`BLOCKED`, retained review finding details, auth/stale
  symlink runbook/preflight diagnostics, docs/board methodology consistency and
  full `AGENTS.md` baseline evidence. Verification rerun passed; stopped for
  external review cycle 2 without publish, commit or push.
- 2026-07-11T19:21:41Z external review cycle 2 вернул свежий `result: no-go`
  с blocker findings R1-R2; verdict validated before rescue changes and
  snapshot/history preserved.
- 2026-07-11 scoped rescue исправил только fresh cycle-2 blockers R1-R2:
  omitted `--workspace` теперь резолвится в invocation repo/cwd, omitted
  `--runtime-root` следует effective workspace, command-run preflight failure
  печатает `terminal_outcome: BLOCKED` перед status path. Verification floor
  rerun passed; stopped for external review cycle 3 without publish, commit or
  push.
- 2026-07-11T19:36:39Z external review cycle 3 вернул свежий `result: go`;
  verdict validated before publish against HEAD `03841dd7` with fingerprint
  `sha256:fe768bf057162afd95d07a01372a3aebb538154617e8fa139edad95a0d2eb6c6`.
- 2026-07-11T19:41:34Z `$opsx-pub` выполнил scoped publish, исключив
  `.runtime/` manifest/review evidence; карточка финализирована в `4.done` как
  deterministic post-publish metadata.
