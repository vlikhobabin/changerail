# Программа 000: Release hardening и native Windows support

## Status
4.done

## Owner
ChangeRail core + operator

## OpenSpec Stage
epic

## Series
`000-release-hardening-and-windows-support-program`

## Series Index
`00`

## Delivery Mode
coordination-only; не запускать `$chrl-deliver` для этой program epic-карточки

## Source
- Operator orchestration plan от 2026-08-01.
- Пересборка backlog в series `010`, `020`, `030` и `040`.

## Summary
Удерживать общий execution contract для последовательного запуска ChangeRail
series через bootstrap delivery, per-series readiness pass и package runner.
Эта карточка фиксирует стабильные gates, порядок и состав серий, но не является
единицей реализации.

## Program Goal
Довести ChangeRail до состояния, в котором core release contracts надежны,
`$chrl-deliver`/runner путь является основным one-command delivery surface, а
native Windows support исследован, реализован и проверен на двух operator-managed
Windows hosts.

## Common Constraints
- Текущая orchestration session остается control plane; delivery выполняется в
  отдельных foreground sessions.
- Coordination-only epic-карточки `000`, `010-00`, `020-00`, `030-00` и `040-00`
  не входят в runner plans.
- Каждый runner plan содержит только текущую executable story series и создается
  после readiness/refresh gate этой серии.
- Рабочее дерево должно быть clean перед `preflight-plan`, `run-plan` и scoped
  publish.
- Public board/docs не должны содержать private hostnames, usernames, local
  paths, credentials, raw logs или runtime state.
- Native Windows support обязателен; research и tests по Windows ведутся
  отдельной серией до реализации.

## Program Series
1. `010-core-release-contracts` - базовые release/runtime/review contracts.
2. `020-one-command-delivery-experience` - надежный `$chrl-deliver`/runner путь.
3. `030-native-windows-discovery` - исследование двух native Windows hosts.
4. `040-native-windows-implementation` - реализация после architecture decision.

## Execution Recommendations
- Опубликовать board baseline до запуска runner, потому что package runner
  fail-closed на dirty workspace.
- Выполнить `010-01` как bootstrap delivery в отдельной fresh `$chrl-deliver`
  session, чтобы исправить skill metadata до runner queue.
- Для `010` создать tracked plan только на `010-02`..`010-05`; первый card не
  включать в package runner.
- После каждой серии проводить exit audit, актуализировать следующую series epic
  и story cards, затем публиковать readiness/plan перед запуском runner.
- Перед `030` подготовить ignored Windows lab inventory и проверить SSH-доступ к
  двум hosts без записи host identities в tracked files.
- Перед `040` полностью перепланировать provisional cards по итогам `030-03`.

## Exit Gate
- Series `010`, `020`, `030` и `040` опубликованы или явно закрыты с
  replacement/canceled rationale.
- Full release baseline проходит на primary Linux environment.
- Native Windows support matrix, implementation и verification evidence
  отражены в public docs/specs без private runtime traces.
- Board не содержит устаревших executable cards без явного `5.canceled`
  решения.

## Related
- `openspec/board/4.done/010-00-core-release-contracts-epic.md`
- `openspec/board/4.done/020-00-one-command-delivery-experience-epic.md`
- `openspec/board/4.done/030-00-native-windows-discovery-epic.md`
- `openspec/board/4.done/040-00-native-windows-implementation-epic.md`
- `bin/changerail-delivery-runner`
- `skills/chrl-deliver/SKILL.md`

## Result
Program exit passed. Series `010`..`040` are published, Linux release baseline
is green, and native Windows generated-copy support has retained two-host
clean-clone evidence. This coordination epic has no remaining executable work.

## Next
- done

## Log
- 2026-08-01T15:34:23Z program epic создана для orchestration серий `010`-`040`.
- 2026-08-01T21:24:05Z series `010` завершена post-push baseline 26/26;
  series `020` прошла readiness pass и получила tracked runner plan.
- 2026-08-02T00:51:40Z series `020` завершена tracked runner plan:
  `020-01`..`020-05` delivered, workspace clean, `HEAD == origin/main`.
- 2026-08-02T00:58:19Z exit audit после `020` прошел release baseline 27/27.
  Readiness для `030` заблокирован до появления ignored mapping для двух
  Windows hosts.
- 2026-08-02T08:16:40Z series `030` завершена tracked runner plan:
  `030-01`..`030-03` delivered, workspace clean, `HEAD == origin/main`.
- 2026-08-02T08:24:42Z exit audit после `030` прошел release baseline 27/27;
  series `040` перепланирована и готовится к package runner.
- 2026-08-10T08:00:00Z board audit подтвердил, что `040-01`..`040-05`
  опубликованы, two-host support proof записан, а stale runner handoff больше не
  актуален; program epic закрыта как выполненная.
- 2026-08-10T08:11:52Z post-closure release baseline прошел 31/31; current и
  reachable-history public-surface scans прошли без findings.
