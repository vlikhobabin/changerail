# Упростить архитектуру регрессии verify-project

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
- Карточка обновлена относительно SSH-advertised `origin/main`
  `12769188dcb74d1ee7d883108d7d1dcd2f2f1a2a`.
- На этой базе `scripts/smoke-verify-project.py` имеет Git blob
  `7e189bbdb9018f65206251205968905615d98a69`. Статический разбор его
  канонического `SHARD_SCENARIOS` даёт два shard-а размером `39` и `30`, всего
  `69` уникальных scenario IDs без дубликатов.
- Завершённая immediate remediation опубликована commit
  `89abc53fd29075ab1715ea07a146622225e04ef1` и зафиксирована в
  `openspec/board/4.done/replace-bounded-public-history-scan-and-align-release-suites.md`.
  Её focused oracle находится в `scripts/smoke-verify-project-sharding.py`.
- Архитектурный контекст завершённой remediation находится в
  `openspec/changes/archive/2026-08-31-replace-bounded-public-history-scan-and-align-release-suites/`.

## Summary
Исследовать глубокое упрощение внутренней архитектуры
`scripts/smoke-verify-project.py`, сохранив полный fail-closed регрессионный
смысл. Цель — отделить чистые проверки parsing, policy и classification от
небольшого явно обоснованного набора настоящих CLI end-to-end canaries,
уменьшить повторную материализацию consumer fixtures и повтор инвариантных
OpenSpec/npm-проверок.

Предпочтительное направление исследования — неизменяемая content-addressed
base fixture с copy-on-write клонированием либо эквивалентной доказанной
изоляцией. Переиспользование результатов допустимо только по точной проверяемой
identity входов и policy внутри ограниченной границы; оно не является
квитанцией прохождения всего smoke, release baseline или publish authority.

## Current Context
- Immediate `39 + 30` process sharding уже завершён и остаётся текущим
  обязательным поведением, а не будущей работой этой карточки.
- Parent сейчас сохраняет порядок всех `69` результатов и fail closed при
  scenario failure, exception, crash, timeout, missing, duplicate или malformed
  terminal result; focused sharding oracle проверяет parity, isolation и cleanup.
- Каждый из двух текущих worker-ов независимо создаёт собственную базовую
  `example-project` fixture, после чего сценарии многократно клонируют её и
  вызывают реальные verification/bootstrap/drift boundaries. Sharding снял
  непосредственный runtime blocker, но не разделил pure rules и CLI canaries и
  не ввёл content-keyed reuse инвариантных проверок.
- Эта карточка не заявляет актуальное числовое wall-time или RSS: тяжёлый полный
  smoke в preparation не запускался, а опубликованные ранее измерения являются
  историческим контекстом, не baseline будущей реализации.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Карточка не разрешает ослаблять mandatory release coverage, менять public
report schema, вводить whole-suite receipt, превращать reuse в новую authority
или переносить настоящую CLI-интеграцию целиком в mocks.

## Scope Boundary
- Это backlog/investigation work, а не implement-ready authority и не release
  blocker. Текущий release route продолжает выполнять обязательный
  `scripts/smoke-verify-project.py` в форме `39 + 30`.
- До отдельного triage нельзя менять production, test или release scripts,
  создавать `openspec/changes/`, delivery manifest или review verdict по этой
  карточке.
- Исследование должно сначала выбрать проверяемые semantic seams, bounded
  CLI-canary registry, fixture/reuse boundary, benchmark protocol и
  implementation-sized split. Оно не предрешает copy-on-write механизм или
  конкретный cache format.
- Изменение смысла, удаление или объединение существующего mandatory scenario
  требует отдельного явного решения; simplification сама по себе такого
  решения не даёт.

## Investigation Gate
- Заморозить machine-checkable inventory всех `69` уникальных IDs из blob
  `7e189bbdb9018f65206251205968905615d98a69`, их порядок, oracle и ожидаемый
  terminal result. При refresh на более новой базе новые IDs можно добавить,
  но эти `69` нельзя потерять, молча заменить или объединить без traceability и
  отдельного решения об изменении scenario semantics.
- Для каждого ID определить единственного будущего владельца: pure rule test
  либо явно обоснованный real CLI canary. Зафиксировать, почему выбранной
  границе нужен или не нужен реальный process/filesystem/tool wrapper.
- Проверить, какие parsing, policy и classification функции можно выделить без
  изменения observable поведения `bin/verify-project`, и какой минимальный
  набор canaries сохраняет process, argv, cwd, environment, filesystem,
  OpenSpec wrapper и npm integration boundaries.
- Спроектировать неизменяемую fixture identity, безопасную изоляцию изменяемых
  roots и bounded fallback для платформ без выбранного copy-on-write
  механизма. Отдельно доказать отсутствие cross-scenario leakage.
- Определить exact tracked inputs, tool/package versions, policy digest и
  релевантный environment contract для допустимого reuse OpenSpec/npm checks;
  изменение любого входа обязано инвалидировать reuse.
- До изменения кода выполнить отдельный воспроизводимый benchmark, записать
  environment/tool identities, отбросить два warmup и собрать пять monotonic
  samples sequential reference и bounded parallel modes. По этим данным до
  implementation заморозить числовой wall-time threshold и допустимую variance;
  preparation-карточка не подставляет историческое число вместо такого замера.
- Тем же pre-implementation benchmark определить и обосновать числовые
  per-child и aggregate RSS ceilings для разрешённого числа jobs. Sampling не
  реже одного раза в `100 ms`; missing measurement или превышение уже
  замороженного ceiling должно делать benchmark non-zero. Числа нельзя
  ослаблять по результатам реализации.
- Назначить owner, оценить complexity и разбить принятый scope на bounded
  implementation-sized changes до перехода карточки в `2.todo`.

## Acceptance
- Все `69` исходных scenario IDs имеют exact one-to-one ownership в новой
  архитектуре. Fault injection либо эквивалентная mutation каждого oracle
  делает общий запуск red в его стабильной позиции.
- Pure rule tests проверяют parsing, policy, classification и другие выделенные
  функции без повторной сборки consumer checkout. Bounded CLI canaries
  сохраняют реальные process, argv, cwd, environment, filesystem, OpenSpec
  wrapper и npm boundaries; список canaries и обоснование каждого остаются
  явными и ограниченными.
- Reusable base fixture неизменяема и content-addressed. Каждый изменяющий
  filesystem сценарий получает отдельный copy-on-write root либо безопасный
  bounded fallback; проверки доказывают отсутствие leakage при success,
  failure, crash и timeout. Изменение base после публикации identity завершает
  запуск non-zero.
- Инвариантные OpenSpec и npm checks переиспользуются только при exact match
  tracked inputs, tool/package versions, policy digest и релевантного
  environment contract. Drift любого входа запускает fresh check; отсутствие
  или нечитаемость authentic input завершает smoke non-zero.
- Missing, truncated, malformed, mismatched, oversized или corrupt reusable
  metadata не может дать false green: запись отклоняется и безопасно
  пересчитывается, а невозможность доказать authentic result завершает запуск
  fail closed с ограниченной публично безопасной диагностикой.
- Для каждого scenario ID отчёт содержит monotonic duration, execution class
  (`pure` или `cli-canary`), reuse hit/miss и terminal status. Group и total
  timings агрегируются явно, не меняют pass/fail и позволяют локализовать
  регрессию без raw logs или private paths.
- Порядок завершения не влияет на результат: parent принимает ровно один
  terminal result для каждого ID, печатает summary и diagnostics в frozen
  inventory order, считает missing, duplicate, crash и timeout ошибкой и
  гарантированно reap-ит children и временные roots.
- Sequential reference и bounded parallel modes дают одинаковые IDs,
  normalized diagnostics, terminal statuses и общий exit code на positive,
  negative, corruption, invalidation и fail-closed fixtures.
- Fresh benchmark соответствует замороженному до implementation протоколу и
  проходит заранее зафиксированные wall-time, variance и RSS ceilings; missing
  samples, неполная identity или превышение любого ceiling завершают benchmark
  non-zero.
- Focused checks, strict OpenSpec validation, current public-surface scan,
  whitespace validation и полный mandatory release route остаются green без
  пропуска `smoke-verify-project`; reuse не становится whole-baseline receipt
  или новой publish authority.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `openspec/board/4.done/replace-bounded-public-history-scan-and-align-release-suites.md`
- `openspec/changes/archive/2026-08-31-replace-bounded-public-history-scan-and-align-release-suites/`
- `scripts/smoke-verify-project.py`
- `scripts/smoke-verify-project-sharding.py`
- `bin/verify-project`
- `scripts/run-release-baseline.py`

## Result
not started

## Next
- После явного решения о приоритете запустить
  `$changerail-explore openspec/board/1.backlog/simplify-verify-project-regression-architecture.md`,
  выполнить Investigation Gate и только затем решать, готова ли карточка к
  triage в `2.todo`.

## Change Plan Notes
Если investigation подтвердит целесообразность, будущий ordered plan должен как
минимум отдельно ограничить: frozen scenario oracle и ownership, pure-rule/CLI
separation, reusable fixture layer, content-keyed invariant reuse и
deterministic reporting с benchmark gates. Это направление не является готовым
change plan и не создаёт implementation authority.

## Log
- 2026-09-02 карточка обновлена как post-sharding backlog investigation на
  точной live базе; числовой performance/RSS baseline оставлен обязательным
  будущим измерением, а не неподтверждённым текущим claim.
