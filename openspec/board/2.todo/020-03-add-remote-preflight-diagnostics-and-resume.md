# Добавить remote preflight diagnostics и resume

## Status
2.todo

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`020-one-command-delivery-experience`

## Series Index
`03`

## Source
- Consumer runner дважды остановился на execution-surface-dependent remote
  preflight, после чего тот же publish target оказался доступен.

## Summary
Классифицировать remote-push preflight failures, сохранять sanitized evidence
и поддержать explicit resume после transient failure с обязательным fresh
повторным proof.

## Acceptance
- Failure classes различают SSH config, DNS, auth, missing branch, timeout и
  unknown remote failure.
- Status использует canonical `changerail.delivery-run.v1` fields и не вводит
  дублирующие top-level `id/status/started_at` aliases.
- Structured preflight evidence содержит sanitized command/result/detail.
- Ограниченный retry/backoff применяется только к transient classes.
- Explicit resume принимает prior status, повторяет полный fresh preflight и
  продолжает только при доказанном publish target.
- Auth/branch uncertainty остается fail-closed.
- Smokes воспроизводят failure classes и later-success resume без сети.

## Scope
- Single-card и queue runner preflight/status/resume contracts.
- Operator diagnostics и migration docs.

## Non-Goals
- Автоматический бесконечный retry.
- Credential storage или обход SSH policy.

## Depends On
- `020-02-add-retained-delivery-evidence`
- `010-03-fix-publish-finalization-ledger`

## Implementation Notes
- Сохранять raw stderr только в ignored evidence; compact status должен быть
  bounded и secret-free.
- Fallback `ssh -F /dev/null` допустим только как явно документированный probe,
  а не скрытая замена approved operator config.

## Change Set
- `add-remote-preflight-diagnostics-and-resume` (planned)

## Change 1: `add-remote-preflight-diagnostics-and-resume`

### Why
Remote-push preflight failures can be transient, but current runner status does
not preserve enough sanitized evidence or resume semantics to continue safely
without manual reconstruction.

### Goal
Classify remote preflight failures, retain sanitized evidence, and make resume
repeat a full fresh publish-target proof before continuing.

### Scope
- Single-card and queue runner preflight/status/resume contracts.
- Operator diagnostics and migration docs.

### Acceptance
- Failure classes различают SSH config, DNS, auth, missing branch, timeout и
  unknown remote failure.
- Status использует canonical `changerail.delivery-run.v1` fields и не вводит
  дублирующие top-level `id/status/started_at` aliases.
- Structured preflight evidence содержит sanitized command/result/detail.
- Ограниченный retry/backoff применяется только к transient classes.
- Explicit resume принимает prior status, повторяет полный fresh preflight и
  продолжает только при доказанном publish target.
- Auth/branch uncertainty остается fail-closed.
- Smokes воспроизводят failure classes и later-success resume без сети.

### Depends On
- `add-retained-delivery-evidence`
- `fix-publish-finalization-ledger`

### Related
- `openspec/changes/add-remote-preflight-diagnostics-and-resume/`

## Verify
- Fake remote/SSH/DNS/auth fixtures.
- Resume fingerprint и stale-status negative cases.
- Delivery runner smoke, schema smoke и release baseline.

## Related
- `openspec/board/1.backlog/020-00-one-command-delivery-experience-epic.md`
- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-run.schema.json`
- `docs/changerail-contracts.md`

## Result
deliver-ready after series `010` exit audit

## Next
- `$chrl-deliver openspec/board/2.todo/020-03-add-remote-preflight-diagnostics-and-resume.md`

## Log
- 2026-08-01T15:07:29Z карточка нормализована из E1 runner feedback.
- 2026-08-01T21:24:05Z readiness pass после серии `010`: карточка переведена
  в `2.todo`, добавлен ordered Change 1 для package runner.
