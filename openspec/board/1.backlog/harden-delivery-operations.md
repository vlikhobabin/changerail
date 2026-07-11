# Укрепить delivery pipeline для повторяемой эксплуатации

## Status
1.backlog

## Owner
Codex

## OpenSpec Stage
story

## Source
- Практика supervised delivery нескольких OPSX-карточек через независимый
  review gate (2026-07), обобщенная до generic public-safe требований.
- `docs/how-it-works.md`
- `AGENTS.shared.md`
- `skills/opsx-do/SKILL.md`
- `skills/opsx-deliver/SKILL.md`
- `skills/opsx-review/SKILL.md`
- `skills/opsx-pub/SKILL.md`
- `schemas/opsx-delivery-manifest.schema.json`
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
- none yet

## Verify
- `./bin/openspec validate --all --strict`
- Парсинг и contract tests для новых или измененных JSON schemas.
- Smoke-тесты manifest move/delete, runner outcomes и metrics на generic fixtures.
- `git diff --check`
- Public-surface scan на private names, paths, hosts, ports и runtime payloads.

## Archive
- not started

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
- `AGENTS.shared.md`
- `skills/opsx-do/SKILL.md`
- `skills/opsx-deliver/SKILL.md`
- `skills/opsx-review/SKILL.md`
- `skills/opsx-pub/SKILL.md`
- `schemas/opsx-delivery-manifest.schema.json`
- `schemas/opsx-review-verdict.schema.json`

## Result
not started

## Next
- Triage scope и перевод `1.backlog -> 2.todo`.
- После принятия scope: `$opsx-ff openspec/board/2.todo/harden-delivery-operations.md`.

## Change Plan Notes
Ориентир для `$opsx-ff`; финальные slugs и dependencies определяются при
планировании:

1. `harden-delivery-lifecycle-contract` - state machine story/change,
   archive-before-review, done-after-publish и manifest file operations.
2. `declare-delivery-verification-floor` - project-declared verification matrix,
   evidence claims и test adequacy до handoff в review.
3. `add-generic-delivery-runner` - public-safe runner, per-run overrides,
   structured status/run contract, loud outcomes и operations runbook.
4. `add-delivery-observability` - review-cycle history, metrics tool, CSV и
   worked operational flow в methodology docs.

## Log
- 2026-07-11 карточка создана по итогам практического многокарточного
  supervised-прогона; оставлена в `1.backlog` для triage.
- 2026-07-11 после аудита public surface scope актуализирован: archive до review
  сохранен как freshness-инвариант; `4.done` перенесен в post-publish
  финализацию; log scraping заменен structured run records; universal toolchain
  checks заменены project-declared verification floor; change plan сокращен до
  четырех связанных направлений.
