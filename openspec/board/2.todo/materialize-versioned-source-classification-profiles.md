# Добавить версионируемые профили классификации исходников

## Status
2.todo

## Owner
ChangeRail maintainer

## OpenSpec Stage
artifacts

## Series
- none

## Series Index
- none

## Source
- Практическая проверка `changerail.source-classification.v1` в подключенном
  проекте с предметно-специфичными исходниками.
- `schemas/changerail-source-classification.schema.json`.
- `scripts/changerail_review_preflight.py`.
- `templates/project/openspec/board/README.md.tpl`.

## Summary
ChangeRail поддерживает проектный файл
`.changerail/source-classification.yaml`, но не помогает выбрать, создать и
сопровождать его для нового проекта. Встроенный классификатор учитывает
распространенные языки, а предметно-специфичные исходники остаются неучтенными,
пока каждый проект вручную не опишет суффиксы, корневые каталоги и способ
измерения.

Добавить универсальный механизм версионируемых профилей, безопасного
определения предполагаемого состава технологий и явного создания
отслеживаемой классификации. Автоматическое определение должно только
предлагать профиль. Проверка риска использует исключительно явно выбранную и
зафиксированную конфигурацию и никогда не меняет правила посреди проверки
текущего изменения.

## Current Behavior
- Без `.changerail/source-classification.yaml` предварительная проверка
  использует встроенный список распространенных суффиксов исходников.
- Предметные форматы, включая неизвестные ChangeRail языки и структурные XML,
  по одному расширению файла прикладным кодом не считаются.
- Начальная настройка проекта сообщает о возможности классификации, но не
  создает прикладные корневые каталоги и не предлагает готовые профили.
- Проверка не сообщает, что в репозитории появился вероятный исходный код,
  который не покрывается ни встроенными правилами, ни проектной
  классификацией.

## Problem
Ручное копирование YAML между проектами создает четыре риска:

- новый проект может начать поставку кода до появления классификации, поэтому
  расчет сложности и требование исследования будут занижены;
- разные проекты одного технологического стека постепенно получают разные
  правила без объяснимой причины;
- повторное автоматическое угадывание может незаметно изменить проверку риска
  после добавления нового файла-маркера;
- жесткое встраивание каждого языка и структуры каталогов в ChangeRail core
  превратит универсальный продукт в набор несвязанных предметных исключений.

## Design Direction
- ChangeRail владеет форматом профиля, командами определения, создания и
  проверки, сведениями о происхождении и правилами безопасного объединения.
- Интеграции предметных продуктов могут поставлять версионируемые профили как
  данные, не добавляя предметные условия в код ChangeRail.
- Определение состава технологий является неизменяющей операцией и возвращает
  кандидатов с объясняющими признаками и степенью уверенности.
- Создание классификации выполняется только для явно выбранного профиля либо
  типа проекта, уже подтвержденного вызывающим продуктом.
- Итоговым источником истины остается отслеживаемый проектом файл
  `.changerail/source-classification.yaml`.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `yes`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Критический уровень нужен потому, что изменение влияет на расчет объема
прикладного кода и выбор обязательной независимой проверки.

Published investigation `investigate-bounded-field-validation-batch` закрывает
repeated-defect classification для одного bounded source-profile hypothesis.
Перед implementation review все еще требуется отдельная exact published
authorization card для новых profile/check contracts.

## Depends On
- `investigate-bounded-field-validation-batch`
- separate exact published authorization source for
  `materialize-versioned-source-classification-profiles`

## Acceptance
- Определен версионируемый договор профиля классификации, который может
  выразить `source_kinds`, суффиксы, корневые каталоги, способ измерения и
  непроизводственные каталоги без абсолютных и машинно-зависимых путей.
- Профиль имеет устойчивые идентификатор, версию и контрольную сумму; отчет
  создания показывает их вместе с источником профиля.
- ChangeRail принимает как встроенные универсальные профили, так и явно
  переданный локальный профиль интеграции, проверяя оба одной схемой и не
  загружая исполняемый код или данные из сети.
- Неизменяющая команда определения возвращает машиночитаемый список кандидатов,
  обнаруженные признаки, степень уверенности, неоднозначности и рекомендуемое
  действие; она не создает и не изменяет файлы.
- Определение использует состояние репозитория до проверяемого изменения либо
  явно переданный снимок, чтобы само изменение не могло незаметно поменять
  правила собственной оценки.
- Команда создания требует явно выбранный профиль и выводит предварительный
  план или разницу до записи файла.
- При отсутствии классификации подтвержденное создание формирует
  `.changerail/source-classification.yaml`, проходящий существующую схему и
  предварительную проверку.
- Повторное создание с тем же профилем и параметрами ничего не меняет и
  сообщает, что состояние совпадает.
- Существующий отличающийся проектный файл не перезаписывается. Команда
  останавливается с объяснимой разницей и требует отдельного явного решения о
  миграции.
- Сочетание нескольких профилей имеет однозначный порядок; пересекающиеся
  правила с разными способами измерения блокируются вместо выбора по порядку
  обнаружения.
- Предварительная проверка продолжает использовать только отслеживаемую
  классификацию. Обнаруженный, но не принятый профиль не влияет на
  `added_production_loc`, уровень риска или решение о допуске.
- Проверка состояния сообщает о вероятных исходниках, не покрытых встроенными
  или проектными правилами, и различает предупреждение с низкой уверенностью и
  блокирующее расхождение с подтвержденным профилем.
- Отчет объясняет итоговые правила: профиль, проектные переопределения,
  покрытые и исключенные каталоги, но не копирует содержимое исходников.
- Отсутствие нового профиля сохраняет обратную совместимость с текущим
  встроенным классификатором и схемой `changerail.source-classification.v1`.
- Шаблоны и руководство описывают поток `detect -> review -> materialize ->
  check`, а также явно запрещают скрытое включение найденного стека.
- Проверки используют только искусственные общие репозитории, включая один
  смешанный стек, неизвестный предметный суффикс, структурный XML, конфликт
  профилей, повторное создание и защиту существующего файла.

## Scope
- Схемы и команды ChangeRail для профилей, определения, создания и проверки.
- Связь с `changerail-review-preflight` и средствами проверки проекта.
- Начальные универсальные примеры и договор подключения внешнего предметного
  профиля.
- Документация начальной настройки и обновления классификации.

## Non-Goals
- Встраивание названий объектов, каталогов или средств выполнения конкретной
  прикладной платформы в ChangeRail core.
- Семантический анализ или компиляция каждого обнаруженного языка.
- Скрытое создание классификации при обычной предварительной проверке,
  выполнении карточки или независимой проверке.
- Автоматическая фиксация созданного файла в Git.
- Загрузка профилей из сети или выполнение поставляемого профилем кода.
- Замена `.gitignore`, правил владения исходниками или проектных команд
  проверки.

## Dependencies
- Доставленный договор `changerail.source-classification.v1`.
- Доставленный расчет сложности по видам исходников.

## Change Set
- `define-source-classification-profile-contract`
- `detect-and-materialize-source-classification-profiles`
- `report-source-classification-profile-drift`

## Verify
- Проверки схемы профиля и недопустимых путей.
- Проверки неизменяющего и воспроизводимого определения.
- Проверки предварительного плана, создания, повторного создания, конфликта и
  миграции существующего файла.
- Проверки смешанного стека и конфликтующих правил.
- Предварительная проверка, доказывающая, что непринятый кандидат не влияет на
  расчет риска, а созданная классификация влияет.
- Полная проверка начальной настройки проекта и открытой поверхности продукта.

## Archive
- not started

## Related
- `schemas/changerail-source-classification.schema.json`
- `scripts/changerail_review_preflight.py`
- `scripts/smoke-review-preflight.py`
- `templates/project/openspec/board/README.md.tpl`
- `openspec/specs/changerail-contracts/spec.md`
- `openspec/specs/changerail-project-templates/spec.md`
- `openspec/changes/define-source-classification-profile-contract/`
- `openspec/changes/detect-and-materialize-source-classification-profiles/`
- `openspec/changes/report-source-classification-profile-drift/`

## Result
Проработка завершена; три apply-ready changes созданы, реализация не начата.

## Next
- После published investigation authorization выполнить
  `$chrl-deliver openspec/board/2.todo/materialize-versioned-source-classification-profiles.md`.

## Change Plan Notes
Профиль выбран как отдельный versioned data document. Optional provenance с
ordered id/version/checksum/source and exact override paths хранится внутри
существующего `.changerail/source-classification.yaml`; конечные rules этого
файла остаются единственным input для review preflight. Реализация сначала
добавляет contract, затем explicit detection/materialization и только потом
blocking/advisory drift reporting.

## Change 1: `define-source-classification-profile-contract`

### Why
Current classification file не имеет reusable profile identity, checksum,
detection signals или deterministic merge semantics.

### Goal
Добавить data-only profile schema, canonical checksum, built-in/local source
validation, fail-closed merge и backward-compatible provenance.

### Acceptance
- Profile выражает classification payload и path-only signals без code/network.
- Same id/version with another checksum и measurement conflicts block.
- Existing v1 files without provenance remain valid and effective.
- Final project file остается единственным risk-policy source.

### Depends On
- delivered `changerail.source-classification.v1` and source-kind complexity
- `investigate-bounded-field-validation-batch`
- separate exact published investigation authorization for this card's
  profile/check contracts

### Related
- `openspec/changes/define-source-classification-profile-contract/`
- `openspec/board/4.done/investigate-bounded-field-validation-batch.md`

## Change 2: `detect-and-materialize-source-classification-profiles`

### Why
Новый project не может read-only определить кандидатов и preview/создать
classification без ручного YAML copying.

### Goal
Добавить `detect` against tracked HEAD и explicit preview-first
`materialize --write` с idempotence/existing-file protection.

### Acceptance
- Detect emits candidates/signals/confidence/ambiguities and writes nothing.
- Explicit profile selection and preview precede atomic creation.
- Same selection is no-op; differing existing file is never overwritten.
- Unaccepted candidate never affects current preflight risk.

### Depends On
- `define-source-classification-profile-contract`

### Related
- `openspec/changes/detect-and-materialize-source-classification-profiles/`

## Change 3: `report-source-classification-profile-drift`

### Why
После materialization нет safe report для provenance, intentional overrides,
confirmed drift и likely uncovered source.

### Goal
Добавить read-only `check`, project/preflight integration и explicit
`detect -> review -> materialize -> check` guidance.

### Acceptance
- Confirmed checksum/measure/undeclared profile drift blocks verification.
- Unaccepted low/high-confidence candidate remains advisory and cannot change
  risk calculation.
- Report explains effective profile/overrides/covered/excluded/uncovered rules
  without source contents or machine paths.
- Migration remains a separate explicit reviewed edit; no force overwrite.

### Depends On
- `detect-and-materialize-source-classification-profiles`

### Related
- `openspec/changes/report-source-classification-profile-drift/`

## Log
- 2026-08-21T04:33:11Z карточка создана по результатам проверки подключения
  предметно-специфичного проекта: ручная классификация работает, но следующий
  проект не получает ее воспроизводимо.
- 2026-08-21T07:43:31Z research selected a separate versioned data profile plus
  optional provenance in the final classification; contract,
  detect/materialize and drift changes reached apply-ready state.
- 2026-08-21T09:10:00Z bounded field-validation investigation зафиксировало
  exact source-profile hypothesis, single effective classification source,
  ceiling 500 и requirement нового split при повторе того же blocker.
