# Закрыть пробелы после greenfield bootstrap consumer-проекта

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

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
not started

## Next
- triage

## Change Plan Notes
При triage разделить изменения по ownership boundaries: bootstrap/templates,
verification/runtime diagnostics и runbook documentation. Не добавлять
неограниченное копирование пользовательского global config; нужен явный
allowlist/profile contract.

## Log
- 2026-08-15T09:04:38Z card created from observed greenfield bootstrap gaps
