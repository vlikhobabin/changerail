# Добавить remote preflight diagnostics и resume

## Status
1.backlog

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
- none yet

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
not started

## Next
- После `020-02` выполнить `$changerail-ff` для этой карточки.

## Log
- 2026-08-01T15:07:29Z карточка нормализована из E1 runner feedback.
