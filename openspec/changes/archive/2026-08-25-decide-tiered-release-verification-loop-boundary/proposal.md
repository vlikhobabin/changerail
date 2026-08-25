## Why

Полный release baseline запускает дорогую Windows matrix до проверки всего
необходимого toolchain и повторно выполняет четыре уже принадлежащие matrix
semantic checks. Один поздний missing `ruff` поэтому тратит минуты без
verification value, а единственный полный профиль используется и как частый
inner loop, и как publish authority.

## What Changes

- Зафиксировать fail-fast admission exact release toolchain до первого
  semantic child и frozen full-release inventory со stable semantic IDs,
  exactly-one owner, deterministic order и fail-closed completeness.
- Передать шесть local Windows IDs одной bounded parallel matrix и убрать
  четыре standalone duplicate processes, сохранив их semantic coverage.
- Сохранить explicit local/live boundary: обычный release gate не читает host
  inventory и не контактирует с Windows hosts, а live proof остаётся отдельным
  operator action.
- Ввести non-authoritative `affected` profile с bounded Git path selector,
  который при unknown, ambiguity или self-change расширяется до полного
  inventory. Только `full-release` может служить review, publish и CI gate.
- Разделить будущую реализацию на три authorization lineage: tiered
  orchestration `<=499` production LOC относительно `45a2de9`, isolated
  `verify-project` cases `<=500` LOC относительно опубликованного tiered HEAD
  и independently authorized clean scanner v2 `<=300` LOC относительно того же
  tiered HEAD.
- Не создавать successor cards и не менять executable surface в этом
  decision-only change.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-ci`: заменить process-invocation authority frozen
  semantic inventory, fail-fast toolchain admission и tiered verification
  profiles без ослабления полного release coverage.

## Impact

Decision меняет только target board card и apply-ready OpenSpec artifacts.
Будущая tiered implementation затронет release baseline, Windows matrix,
release-CI contract smoke, tracked CI workflow и gate-facing documentation;
следующие отдельные implementation затронут `verify-project` isolation и
structural public-history scanner.
Production, tests, runtime state, authorization/successor cards и main spec в
этом planning pass не изменяются.
