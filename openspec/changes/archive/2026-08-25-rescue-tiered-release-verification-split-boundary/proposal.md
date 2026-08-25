## Why

Опубликованные tiered decision и broad authorization связали release authority
core и Windows scheduler в один `<=499` successor. Два независимых pre-capture
аудита показали, что такой combined scope нельзя завершить fail-closed в этом
лимите; неопубликованный payload исчерпал свой bounded путь и остается только
forensic input.

## What Changes

- Заменить будущий combined implementation двумя независимо авторизованными
  `<=499` scopes: A для release authority core и B для Windows process
  scheduler/duplicate removal.
- Зафиксировать exact non-overlapping ownership A и B, включая staged boundary,
  на которой A не меняет Windows scheduling/process topology.
- Зафиксировать по одному exact six-field authorization object с ceiling `500`
  и protocol allowance `true` для каждого нового implementation successor.
- Установить порядок publication: A, отдельный clean scanner-v2, B, отдельные
  verify-project и release-smoke successors.
- Требовать fresh Sol/`xhigh` pre-capture audit, один atomic terminal
  `full-release` capture без retry и fresh formal review для каждого
  executable successor.
- Явно запретить перенос code, tests, diff, evidence, receipt или runtime state
  из старого неопубликованного combined payload.

## Capabilities

### New Capabilities

Нет.

### Modified Capabilities

- `changerail-release-ci`: разделить broad tiered implementation boundary на
  две exact independently authorized lineage без ослабления frozen semantic
  coverage или release authority.

## Impact

Изменяются только board/OpenSpec/spec документы ChangeRail. Production, test и
runtime LOC остаются нулевыми; executable successors, history scan, benchmark и
full baseline в этом change не создаются и не запускаются. Consumer contracts
не меняются до отдельных опубликованных implementations.
