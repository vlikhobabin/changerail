# Design: consumer Codex auth setup docs

## Context

Delivery runner уже вычисляет effective `CODEX_HOME`: explicit environment
value выигрывает, иначе используется `<workspace>/.codex`. Preflight
fail-closed, если auth marker отсутствует, но consumer adoption docs и
bootstrap guidance не дают оператору clear setup path до первого
`preflight-plan`.

## Goals / Non-Goals

**Goals:**
- Описать auth prerequisite для single-card и plan-oriented runner commands.
- Дать remediation examples с project-local ignored symlink и explicit
  `CODEX_HOME`.
- Объяснить, почему ChangeRail не копирует credentials silently.

**Non-Goals:**
- Не менять runner preflight behavior в этом change.
- Не добавлять bootstrap option; это делает `bootstrap-opt-in-auth-link`.
- Не требовать real auth для public CI или template smoke.

## Decisions

- Canonical docs section будет в `docs/consumer-adoption-runbook.md`, с
  cross-reference из `docs/how-it-works.md` и `docs/changerail-contracts.md`.
  Это дает операторам setup path и сохраняет contract-level overview коротким.
- Examples используют `/opt/example-project` и `$HOME`, а не реальные consumer
  paths. Это соответствует public-surface rules.
- Symlink example показывает local ignored marker, но не предлагает copy
  credentials by default.

## Risks / Trade-offs

- [Risk] Docs могут разойтись с future CLI option.
  → Mitigation: next changes добавляют bootstrap option, verify advisory и
  runner diagnostics, которые ссылаются на тот же canonical section.
