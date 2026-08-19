# Закрыть пробелы после greenfield bootstrap consumer-проекта

## Status
5.canceled

## Owner
ChangeRail maintainer

## OpenSpec Stage
superseded

## Series
- none

## Series Index
- none

## Source
- greenfield consumer bootstrap session, 2026-08-15

## Summary
Штатный bootstrap успешно создаёт и статически проверяет consumer, но первый
реальный запуск выявляет несколько неописанных переходов: project-local
`CODEX_HOME` не получает все разрешённые системные MCP, launcher не создаётся,
auth link нельзя добавить до первого commit, а runtime proof, remote state,
domain tailoring и остаток instruction budget не собраны в единый runbook flow.

Нужно сделать greenfield путь воспроизводимым от пустого каталога до реально
работающего Codex/ChangeRail окружения без ручных догадок.

## Acceptance
- Bootstrap или явный профиль создаёт POSIX/Windows launcher для project-local
  Codex и документирует изоляцию `CODEX_HOME`.
- MCP policy явно определяет allowlisted inheritance/merge и проверяет полный
  выбранный набор, включая remote MCP без npm pin.
- Auth marker можно безопасно подключить в исходном greenfield запуске либо
  штатным post-bootstrap шагом до первого commit.
- Runbook различает unavailable, empty и non-empty Git remote до инициализации.
- Runbook включает domain-tailoring checklist, безопасные runtime probes и
  правила хранения redacted evidence.
- Bootstrap выводит свободный instruction budget для проектных правил и
  предлагает перенос деталей в docs/skills до достижения warning threshold.
- Smoke coverage воспроизводит перечисленные сценарии на поддерживаемых
  платформах.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `README.md`
- `docs/consumer-adoption-runbook.md`
- `templates/project/`
- `bin/bootstrap-project`
- `bin/verify-project`

## Result
Canceled as superseded by delivered greenfield bootstrap, consumer auth,
runtime diagnostics and lockless wiring work. The remaining launcher and MCP
inheritance expectations were deliberately not adopted: consumers may launch
the ChangeRail runner with an explicit `CODEX_HOME` without a tracked
`bin/codex`, and MCP configuration remains explicit/allowlisted instead of
copying an operator's global config.

## Next
- none; reopen only for a new reproducible greenfield gap not covered by the
  delivered contracts below

## Change Plan Notes
При triage разделить изменения по ownership boundaries: bootstrap/templates,
verification/runtime diagnostics и runbook documentation. Не добавлять
неограниченное копирование пользовательского global config; нужен явный
allowlist/profile contract.

## Log
- 2026-08-15T09:04:38Z card created from observed greenfield bootstrap gaps
- 2026-08-19T14:05:00Z canceled after board triage: actionable scope is covered
  by `050-harden-greenfield-consumer-bootstrap`,
  `harden-consumer-codex-auth-setup` and
  `migrate-lockless-consumer-wiring`; unrestricted MCP inheritance and a
  mandatory tracked consumer launcher conflict with current product decisions.
