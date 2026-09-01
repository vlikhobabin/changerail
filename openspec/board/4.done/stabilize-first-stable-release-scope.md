# Стабилизировать scope первого stable release

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- none

## Series Index
- none

## Source
- Решение оператора от 2026-08-31: phase-routed delivery и runtime artifact
  retention не входят в первый stable release; retention возвращается в
  работу только после устранения общего долга проекта.
- Возобновление от опубликованной replacement base
  `origin/main@9d33d2a8db260af5f8ba7c5a75fec5ff280a778f` после merge PR #5.

## Summary
Зафиксировать поддерживаемый scope первого stable release на чистом
`origin/main`, вывести незавершенную phase-routed lineage из исполняемой
очереди, поставить retention за явный debt gate и подготовить однозначный
handoff к отдельной карточке выпуска без интеграции forensic payloads.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Depends On
- `replace-bounded-public-history-scan-and-align-release-suites` (published)

## Acceptance
- Первый stable release явно ограничен опубликованным generic core из
  `origin/main`; незавершенный phase-routed payload, его authorization и
  successor не входят в release candidate и pilot wave не запускается.
- Устаревшая карточка
  `implement-phase-routed-delivery-authorization-boundary` закрыта как
  superseded/deferred, а возможное возвращение к инициативе представлено одной
  backlog-карточкой с новым triage после stable release и сокращения долга.
- `manage-runtime-artifact-retention-and-cleanup` остается в backlog и содержит
  явный entry gate: не начинать investigation, authorization или реализацию до
  отдельного решения после устранения общего технического и операционного
  долга.
- Устаревшая live todo history-scanner card закрыта как superseded
  опубликованной replacement card и больше не блокирует release stabilization.
- README, roadmap и release discipline не заявляют deferred инициативы как
  готовые или release-blocking возможности и ведут к отдельной карточке
  подготовки `1.0.0`.
- Локальные worktree/branches инвентаризированы только в ignored runtime
  evidence; machine-specific пути и имена не попадают в tracked public
  surface, а никакой dirty/forensic payload не интегрируется автоматически.
- Чистый release candidate проходит последовательные core и extended suites с
  pinned dev dependencies, current/history public scans и strict checks либо
  фиксирует точный candidate-owned blocker до подготовки release metadata.

## Change Set
- `stabilize-first-stable-release-scope`

## Verify
- `python3 scripts/run-release-baseline.py`
- `python3 scripts/run-release-baseline.py --suite extended`
- `bin/openspec validate --all --strict`
- `python3 scripts/public-surface-scan.py`
- `python3 scripts/public-surface-scan.py --history`
- JSON/TOML parsing from `AGENTS.md`
- `git diff --check` including untracked tracked-candidate files

## Archive
- `openspec/changes/archive/2026-09-01-stabilize-first-stable-release-scope/`

## Related
- `README.md`
- `docs/release-discipline.md`
- `openspec/board/5.canceled/implement-phase-routed-delivery-authorization-boundary.md`
- `openspec/board/5.canceled/implement-bounded-public-history-scan-runtime.md`
- `openspec/board/4.done/replace-bounded-public-history-scan-and-align-release-suites.md`
- `openspec/board/1.backlog/manage-runtime-artifact-retention-and-cleanup.md`

## Result
Clean continuation materialized on exact published base
`9d33d2a8db260af5f8ba7c5a75fec5ff280a778f`; прежний history-scanner blocker
разрешен published replacement. Isolated candidate with only `main` and
`origin/main` refs passed sequential core `22/22` (including verify-project
`69/69`) and extended `12/12` suites on 2 CPUs. Final current/history scans
passed with `1313` files and `0` findings each; JSON/TOML, strict OpenSpec and
whitespace checks are green. Delta spec synced and change archived. Retained
ignored evidence is under `.runtime/changerail/release-scope/`; exact scope and
verification handoff are in
`.runtime/changerail/delivery-manifests/stabilize-first-stable-release-scope.json`,
and normalized review preflight is in
`.runtime/changerail/review-preflights/stabilize-first-stable-release-scope.json`.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `stabilize-first-stable-release-scope`

### Why
Stable release нельзя собирать из неоднозначной смеси опубликованного core,
отклоненных implementation payloads и локальных forensic веток.

### Goal
Зафиксировать один проверяемый release scope, закрыть устаревшую phase-routed
очередь, отложить retention за debt gate и подготовить чистый handoff к
выпуску `1.0.0`.

### Scope
- Обновить только board, roadmap/release docs и card-owned OpenSpec artifacts.
- Сохранить investigation history, но не создавать и не интегрировать
  phase-routed authorization/successor.
- Хранить локальную branch/worktree инвентаризацию только в ignored runtime
  evidence и не выполнять разрушительную очистку неоднозначных worktree.
- Не менять runtime code, schemas, skills, CLI, consumer templates или
  dependency pins.

### Acceptance
- Все card-level acceptance criteria выполнены и подтверждены release/public
  checks.
- Создан отдельный, не входящий в этот payload handoff для подготовки первого
  stable release после green baseline.

### Depends On
- `replace-bounded-public-history-scan-and-align-release-suites`

### Related
- `openspec/changes/stabilize-first-stable-release-scope/`

## Log
- 2026-08-31T00:00:00Z создано по явному решению оператора отложить
  phase-routed delivery и runtime artifact retention за stable/debt gates.
- 2026-08-31T00:00:00Z board/docs scope реализован; ignored inventory выявил
  135 worktree (47 dirty), удалены только два clean fully-merged worktree с
  сохранением refs.
- 2026-08-31T00:00:00Z release baseline остановлен bounded timeout; отдельная
  replacement lineage создана для bounded history scan и release suite split.
- 2026-08-31T19:45:10Z replacement опубликован через PR #5; merge/current base
  `9d33d2a8db260af5f8ba7c5a75fec5ff280a778f`, blocker снят.
- 2026-09-01T00:00:00Z clean continuation materialized semantically on exact
  published base; stale history investigation handoff не переносился.
- 2026-09-01T05:37:32Z ignored aggregate inventory recorded 139 worktrees
  (88 clean, 51 dirty) and 142 local branches; no destructive action taken.
- 2026-09-01T05:43:00Z isolated release candidate passed sequential core
  `22/22`, including verify-project `69/69`; initial setup-only invocation was
  rejected before lint because the pinned venv was not activated, then the
  exact command was rerun with the pinned venv and passed.
- 2026-09-01T05:47:00Z extended suite passed `12/12`; final current/history
  public scans passed `1313 files, 0 findings` each, config parsing and
  untracked-aware whitespace checks passed.
- 2026-09-01T05:48:00Z release-discipline delta synced; change archived at
  `openspec/changes/archive/2026-09-01-stabilize-first-stable-release-scope/`.
- 2026-09-01T05:51:24Z manifest exact working-tree scope-check passed;
  normalized deterministic preflight routed the ordinary payload to required
  fresh high-effort LLM review.
- 2026-09-01T06:20:43Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
