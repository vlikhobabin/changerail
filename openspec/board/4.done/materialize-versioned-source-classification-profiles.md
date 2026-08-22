# Добавить версионируемые профили классификации исходников

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

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
- Published investigation authorization: `{"authorization_card":"openspec/board/4.done/authorize-bounded-source-profile-payload.md","authorization_id":"authorize-bounded-source-profile-payload"}`

Критический уровень нужен потому, что изменение влияет на расчет объема
прикладного кода и выбор обязательной независимой проверки.

Published investigation `investigate-bounded-field-validation-batch` закрывает
repeated-defect classification для одного bounded source-profile hypothesis.
Exact authorization source `authorize-bounded-source-profile-payload`
публикует bounded source для новых profile/check contracts.

## Depends On
- `investigate-bounded-field-validation-batch`
- `authorize-bounded-source-profile-payload`

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
- GREEN: `python3 -m py_compile scripts/changerail_source_classification.py scripts/changerail_review_preflight.py scripts/smoke-contract-schemas.py scripts/smoke-review-preflight.py scripts/smoke-bootstrap-project.py scripts/smoke-verify-project.py`.
- GREEN: `python3 scripts/smoke-contract-schemas.py` - `SMOKE_CONTRACT_SCHEMAS_OK (28 schemas)`.
- GREEN: `python3 scripts/smoke-review-preflight.py` - `review preflight smoke: PASS`; includes source-profile helper detect/materialize/check smoke, duplicate selector dedupe, check report rule-summary assertions, idempotence, migration-required, drift blocking and dirty-tree HEAD-bound detection.
- GREEN: `python3 scripts/smoke-bootstrap-project.py` - report `.runtime/changerail/bootstrap-smoke/20260821T202608Z-3f78a655/report.json`, 23/23 passed.
- GREEN: `python3 scripts/smoke-verify-project.py` - report `.runtime/changerail/verify-project-smoke/20260821T202608Z-e2ae9030/report.json`, 69/69 passed.
- GREEN: `bin/changerail-source-classification --json check` - blocking=0, advisory=0 for the ChangeRail-owned classification policy.
- GREEN: `bin/openspec validate changerail-contracts --strict`, `bin/openspec validate changerail-project-verification --strict`, `bin/openspec validate changerail-project-templates --strict`.
- GREEN: `bin/openspec validate --all --strict` - 26 items passed before archive.
- GREEN: `git diff --check -- ':!*.cmd'` - passed before archive; final whitespace check is rerun before review/publish with untracked files included.
- GREEN: `python3 scripts/smoke-windows-matrix.py` - report `.runtime/changerail/windows-smoke/20260821T205101Z-2d0943fe/report.json`, 6/7 passed, 0 failed, live two-host smoke not-run by default.
- GREEN: `python3 scripts/run-release-baseline.py` - 36/36 steps passed; final Windows matrix report `.runtime/changerail/windows-smoke/20260821T215742Z-81cf925a/report.json` passed with the same live two-host not-run caveat.
- GREEN: `bin/changerail-review-verdict preflight openspec/board/3.inprogress/materialize-versioned-source-classification-profiles.md --workspace . --normalize --output .runtime/changerail/review-preflights/materialize-versioned-source-classification-profiles.json --json` - ready-for-llm-review, critical route, `added_production_loc=498/500`.

## Archive
- `openspec/changes/archive/2026-08-21-define-source-classification-profile-contract/`
- `openspec/changes/archive/2026-08-21-detect-and-materialize-source-classification-profiles/`
- `openspec/changes/archive/2026-08-21-report-source-classification-profile-drift/`

## Related
- `schemas/changerail-source-classification.schema.json`
- `schemas/changerail-source-classification-profile.schema.json`
- `schemas/changerail-source-classification-check.schema.json`
- `.changerail/source-classification.yaml`
- `profiles/source-classification/`
- `bin/changerail-source-classification`
- `scripts/changerail_review_preflight.py`
- `scripts/changerail_source_classification.py`
- `scripts/smoke-review-preflight.py`
- `scripts/smoke-contract-schemas.py`
- `scripts/smoke-bootstrap-project.py`
- `scripts/smoke-verify-project.py`
- `templates/project/AGENTS.md.tpl`
- `templates/project/openspec/board/README.md.tpl`
- `templates/project/consumer-README.md.tpl`
- `openspec/specs/changerail-contracts/spec.md`
- `openspec/specs/changerail-project-templates/spec.md`
- `openspec/specs/changerail-project-verification/spec.md`
- `openspec/changes/archive/2026-08-21-define-source-classification-profile-contract/`
- `openspec/changes/archive/2026-08-21-detect-and-materialize-source-classification-profiles/`
- `openspec/changes/archive/2026-08-21-report-source-classification-profile-drift/`

## Result
Реализация завершена: добавлен data-only profile contract, built-in profile
data, `bin/changerail-source-classification` с `detect`, `materialize` и
`check`, интеграция с review preflight и `verify-project`, project-owned
ChangeRail source classification для явного production/non-production
accounting, contract/docs/templates и focused smoke coverage.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

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
- 2026-08-21T20:31:50Z `$changerail-do` реализовал profile/detect/materialize/check flow,
  синхронизировал main specs, добавил focused smokes, зафиксировал
  ChangeRail-owned source classification policy для явного production LOC
  accounting и архивировал три card-owned OpenSpec changes; карточка оставлена
  в `3.inprogress` до independent review и publish.
- 2026-08-21T21:41:36Z release baseline passed all 36 steps after stabilizing
  generated project instruction-budget guidance; Windows live two-host smoke
  remains an explicit not-run caveat outside local matrix coverage.
- 2026-08-21T21:22:13Z deterministic review preflight passed at the exact
  published source ceiling: 500/500 added production LOC.
- 2026-08-21T21:54:00Z independent review cycle 1 returned `no-go` with two
  blockers: duplicate profile selectors could create schema-invalid
  provenance, and `check` report did not expose effective rule/override
  summaries.
- 2026-08-21T21:55:42Z same-card rescue fixed both blockers: duplicate
  selectors dedupe before merge, materialized classification is schema-checked
  before preview/write, and `check` reports source-kind roots,
  non-production roots and declared override paths; focused smokes and
  deterministic preflight passed with 498/500 added production LOC.
- 2026-08-21T22:16:27Z post-rescue release baseline passed all 36 steps;
  Windows matrix report `.runtime/changerail/windows-smoke/20260821T215742Z-81cf925a/report.json`
  passed with live two-host smoke not-run by default.
- 2026-08-21T22:29:04Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
