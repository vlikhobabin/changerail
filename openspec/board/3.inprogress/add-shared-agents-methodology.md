# Добавить общую OPSX-методологию для агентов

## Status
3.inprogress

## Owner
Codex

## OpenSpec Stage
apply-ready

## Source
- OPSX bootstrap planning session от 2026-07-08.
- `README.md`
- `docs/opsx-source-of-truth-architecture.md`
- `AGENTS.md`
- `CLAUDE.md`

## Summary
Создать первый self-hosted OPSX change: добавить `AGENTS.shared.md` как
reusable methodology block для consumer projects и использовать собственную
OpenSpec-доску репозитория как dogfooding surface.

## Acceptance
- OPSX содержит минимальную структуру `openspec/` для board-driven dogfooding.
- Change `add-shared-agents-methodology` находится в apply-ready состоянии.
- `AGENTS.shared.md` задает generic methodology без private workspace
  references.
- Verification покрывает OpenSpec validation, config parsing, whitespace checks
  и public-surface scan.

## Change Set
- `add-shared-agents-methodology`

## Verify
- passed: `openspec validate --all --strict --json`
- passed: `python3 -m json.tool .mcp.json`
- passed: `.codex/config.toml` parsed with Python `tomllib`
- passed: `git diff --check`
- passed: Python whitespace scan over `git ls-files --modified --others --exclude-standard`
- passed: `git status --short --ignored`
- passed: public-surface scan for private paths and workspace names relevant to
  this machine

## Archive
- not started

## Related
- `openspec/changes/add-shared-agents-methodology/`
- `AGENTS.shared.md`

## Result
Реализован `AGENTS.shared.md`, инициализирован OPSX dogfooding OpenSpec
skeleton и добавлены первые change artifacts.

## Next
- Повторить independent review / publish flow по запросу.
- Архивировать OpenSpec change после подтверждения review policy для bootstrap
  stage.

## Change 1: `add-shared-agents-methodology`

### Why
OPSX нужен reusable methodology artifact до того, как consumer templates и
bootstrap scripts смогут безопасно генерировать проектные `AGENTS.md`.

### Goal
Добавить `AGENTS.shared.md` и зафиксировать его как generic agent methodology
source для OPSX consumers.

### Acceptance
- `AGENTS.shared.md` покрывает pipeline, board lifecycle, OpenSpec lifecycle,
  review gate, evidence policy, commit/push policy, public-safety rules и
  generated-section drift expectations.
- Файл остается generic и public-safe.
- Текущий root `AGENTS.md` остается repo-specific и ссылается на shared
  methodology только там, где это уместно.

### Depends On
- none

### Related
- `openspec/changes/add-shared-agents-methodology/`

## Log
- 2026-07-08T09:00:00Z card created during OPSX dogfooding bootstrap.
- 2026-07-08T09:10:00Z реализована shared methodology и завершена baseline verification.
- 2026-07-08T09:20:00Z исправлены No-Go findings: public surface, language policy и untracked whitespace evidence.
