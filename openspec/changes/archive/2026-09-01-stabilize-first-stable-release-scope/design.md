## Context

`origin/main` является последним опубликованным source of truth, но локальная
среда содержит множество worktree и веток с forensic, rejected и
экспериментальными payloads. Отдельная phase-routed implementation lineage
исчерпала review/rescue budget и породила новые investigation/authorization
ветви, тогда как оператор явно исключил эту инициативу из первого stable
release. Runtime artifact retention уже находится в backlog и также отложена
до устранения общего долга.

Первый stable release должен готовиться из чистого reviewed core. Локальное
наличие ветки или worktree не делает ее частью публичного release scope.
Machine-specific inventory не может попадать в tracked public files.

Публикация replacement card
`replace-bounded-public-history-scan-and-align-release-suites` устранила
прежний history-scanner blocker: exact base теперь
`origin/main@9d33d2a8db260af5f8ba7c5a75fec5ff280a778f`, а release contract требует
последовательные core и extended suites с сохранением 69 verify-project
scenarios в shards `39 + 30`.

## Goals / Non-Goals

**Goals:**

- Зафиксировать `origin/main` как единственную базу первого stable release до
  появления reviewed release payload.
- Закрыть устаревший исполняемый phase-routed successor и сохранить только одну
  backlog-точку для будущего повторного triage.
- Закрыть противоречивую live todo history-scanner card как superseded уже
  опубликованным replacement, сохранив published decision history.
- Поставить retention за явный debt gate без начала destructive design.
- Сделать попадание dirty, forensic или deferred payload в release candidate
  явной fail-closed ошибкой процесса.
- Получить ignored локальную инвентаризацию веток/worktree и green core плюс
  extended baseline до подготовки version/tag/distribution metadata.

**Non-Goals:**

- Исправлять, публиковать или переносить phase-routed implementation,
  authorization либо successor.
- Проектировать или реализовывать retention/cleanup.
- Удалять dirty, locked или неоднозначные worktree в tracked delivery change.
- Менять runtime code, schemas, skills, CLI, templates или dependency pins.
- Публиковать `1.0.0`, создавать tag или distribution metadata в этом change.

## Decisions

### 1. Release candidate строится только от опубликованного core

Clean integration branch создается от точного `origin/main`. В нее не
переносятся локальные commits по имени ветки, давности или кажущейся готовности.
Любое дополнительное изменение может войти только отдельным scoped reviewed
payload, если полный baseline обнаружит реальный blocker.

Final baseline выполняется на exact filesystem snapshot в изолированном clone,
содержащем только release-reachable refs. Linked worktree используется для
implementation/review, но не является final history proof: его Git directory
разделяет весь локальный ref graph, включая deferred и forensic ветки.

Core и extended release suites запускаются строго последовательно на 2 CPU.
Published suite split и verify-project sharding не меняются.

### 2. Устаревшая phase-routed карточка закрывается, будущее представлено одной backlog-точкой

`implement-phase-routed-delivery-authorization-boundary` перемещается в
`5.canceled` с результатом `superseded/deferred`. Новые authorization и
replacement successor не создаются. Одна новая backlog-карточка хранит только
problem statement и entry gates: stable release опубликован, общий долг
сокращен, есть подтвержденный consumer use case и заново принят bounded scope.

Опубликованные investigations остаются в `4.done` как исторические решения;
их не переписывают и не выдают за готовую runtime capability.

### 3. Published replacement закрывает прежнюю history todo

`implement-bounded-public-history-scan-runtime` больше не является live work:
его bounded цель и release-suite alignment опубликованы replacement card
`openspec/board/4.done/replace-bounded-public-history-scan-and-align-release-suites.md`.
Исходная todo перемещается в `5.canceled` как superseded; новый investigation
или implementation change не создается.

### 4. Retention остается исходной backlog-карточкой с debt gate

Карточка получает явную секцию `Entry Gate` и `Next`, запрещающие начинать
investigation, authorization или implementation до отдельного operator
решения после общей debt-reduction работы. Значения policy candidate остаются
гипотезами и не дают authority на удаление данных.

### 5. Локальная инвентаризация является ignored evidence

Инвентаризация записывается под
`.runtime/changerail/release-scope/` и содержит counts, clean/dirty state,
relation к `origin/main` и безопасную классификацию. Tracked docs не содержат
реальные machine paths, частные имена веток или содержимое dirty worktree.

Эта карточка не удаляет worktree. После review/publish оператор может удалить
только доказанно clean, fully merged либо явно deferred worktree, сохранив
необходимые refs. Dirty и неоднозначные цели остаются на месте.

### 6. Stable release publication остается отдельным final-certification payload

После green baseline создается отдельная deliver-ready карточка подготовки
`1.0.0`. Она владеет `VERSION`, changelog, compatibility/migration notes,
tag/distribution contract, trusted-network checks и final independent review.
Так scope-normalization не получает полномочия на publication boundary.

## Risks / Trade-offs

- [Risk] Deferred phase-routed work будет трудно восстановить. → Сохранить
  опубликованные investigations, одну backlog-карточку и локальные refs до
  отдельной подтвержденной очистки.
- [Risk] Слишком широкий debt gate превратит retention в вечный backlog. →
  Будущий triage обязан определить измеримый debt exit criterion, но текущая
  карточка намеренно не изобретает его без отдельного решения.
- [Risk] Release baseline может выявить blockers, отсутствующие в текущем
  плане. → Создавать отдельные bounded fix cards и не расширять этот docs/board
  payload runtime-изменениями.
- [Risk] Локальный inventory раскроет private/machine state. → Хранить raw
  inventory только под ignored `.runtime` и публиковать лишь generic process
  rule.

## Migration Plan

1. Обновить board и public roadmap/release docs.
2. Последовательно проверить exact candidate core и extended suites, current и
   history public surface, strict OpenSpec и whitespace.
3. Синхронизировать release-discipline requirement и архивировать change.
4. Передать exact payload независимому review и опубликовать scoped change.
5. После публикации использовать отдельную `1.0.0` card; при rollback вернуть
   board/docs/spec payload одним scoped revert без изменения forensic refs.

## Open Questions

- Конкретный packaged distribution format определяется отдельной `1.0.0`
  карточкой; решение об stable release снимает прежний gate, но не выбирает
  формат автоматически.
