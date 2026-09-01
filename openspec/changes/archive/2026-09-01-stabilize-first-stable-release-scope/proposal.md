## Why

Первый stable release сейчас имеет неоднозначный scope: опубликованный core
смешан в локальной среде с отклоненной phase-routed lineage и большим числом
forensic worktree, а backlog retention не содержит принятого оператором debt
gate. Перед подготовкой `1.0.0` нужно зафиксировать release candidate только на
поддерживаемом `origin/main` и явно вывести обе инициативы из release path.

## What Changes

- Закрыть устаревший phase-routed implementation successor как
  superseded/deferred и оставить одну backlog-точку для нового triage после
  stable release и сокращения долга.
- Оставить runtime artifact retention в backlog с явным запретом начинать
  investigation, authorization или implementation до отдельного решения после
  устранения общего долга.
- Обновить roadmap и release discipline так, чтобы первый stable release
  строился только из clean reviewed core и проверялся в изолированном clone
  release refs, а dirty, forensic и deferred payloads не могли неявно войти в
  release candidate или раздувать history gate.
- Сохранить machine-local branch/worktree inventory только как ignored runtime
  evidence и не выполнять автоматическую интеграцию либо разрушительную
  очистку неоднозначных worktree.
- Подготовить отдельный board handoff для выпуска `1.0.0` после полного green
  baseline; version metadata, tag и distribution publication не входят в этот
  scope-normalization change.
- Закрыть устаревшую live todo history-scanner card как superseded
  опубликованной replacement card, не создавая новый investigation handoff.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-discipline`: первый stable release получает явный clean
  core scope и fail-closed исключение deferred/forensic payloads до release
  metadata и publication.

## Impact

- Tracked scope: `README.md`, `docs/release-discipline.md`, board cards,
  `changerail-release-discipline` spec и OpenSpec artifacts этого change.
- Runtime code, schemas, skills, CLI, consumer templates, dependency pins и
  существующие опубликованные investigation artifacts не меняются.
- Consumer behavior не меняется; изменение устраняет неоднозначность release
  claims и очереди разработки.
