# Определить минимальную карту verification coverage

## Status
1.backlog

## Owner
ChangeRail maintainer

## OpenSpec Stage
story

## Series
- none

## Series Index
- none

## Source
- Сравнение ChangeRail с Orca от 2026-08-12.
- [Orca reliability gates](https://github.com/stablyai/orca/blob/main/config/reliability-gates.jsonc)
- `skills/changerail-do/SKILL.md`
- `skills/changerail-review/SKILL.md`
- `templates/project/openspec/config.yaml.tpl`
- `openspec/specs/changerail-project-verification/spec.md`

## Summary
ChangeRail требует concrete verification commands, retained evidence и
per-acceptance review, но выбор обязательных проверок по затронутой
функциональной поверхности остается распределенным между `AGENTS.md`, OpenSpec
artifacts, project config и рассуждением агента. Для сложных Python-решений, а
в дальнейшем для 1С, это оставляет риск false-green: известные проверки
выполнены, но необходимая runtime или domain-specific поверхность не была
классифицирована и поэтому не получила oracle/evidence.

Исследовать минимальную project-owned карту, которая связывает changed surface
с invariant, oracle и required evidence. Взять из Orca только дисциплину явных
reliability gates, не переносить полный каталог maturity/promotion/soak и не
встраивать domain-specific правила в generic ChangeRail core.

## Acceptance
- Exploration описывает текущий путь формирования verification floor в `ff`,
  `do` и independent `review`, включая места, где решение остается только в
  prose или agent inference.
- Предложена минимальная модель не шире полей `id`, `applies_to`, `invariant`,
  `oracle` и `required_evidence`; дополнительные поля допускаются только при
  доказанной необходимости.
- Определено, должна ли карта быть tracked project config, OpenSpec artifact,
  skill-produced runtime artifact или сочетанием этих поверхностей, без
  создания второго источника истины для acceptance и tasks.
- Для каждой применимой обязательной проверки описан fail-closed flow:
  planning объявляет coverage, delivery сохраняет observed evidence, reviewer
  обнаруживает missing или invalid evidence.
- Концепция проверена на одном generic Python example с project-owned
  test/lint/type/runtime policy; ChangeRail не делает formatter, typing или
  environment matrix обязательными без явной project policy.
- Для будущей 1С-интеграции определена extension boundary, способная различать
  BSL, metadata, managed forms, roles, posting, reports, migrations и runtime
  UI evidence, при этом сами 1С-правила остаются вне generic core.
- Design сравнивает пользу deterministic coverage с ценой новой schema/config
  и допускает решение не реализовывать новый contract, если существующих
  OpenSpec tasks и domain skills достаточно.
- Public examples используют только generic paths и не содержат private
  project names, runtime reports или machine-specific evidence.

## Non-Goals
- Копирование полного Orca reliability-gate catalog.
- Универсальная test matrix для всех Python-проектов.
- Встроенные в ChangeRail core BSL, metadata, TestClient или 1С runtime tools.
- Автоматический pass на основании совпадения file glob без observed oracle.
- Замена acceptance criteria, OpenSpec tasks, delivery manifest или review
  verdict новым параллельным workflow.
- Реализация same-repository parallel workers или worktree orchestration.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `AGENTS.shared.md`
- `skills/changerail-ff/SKILL.md`
- `skills/changerail-do/SKILL.md`
- `skills/changerail-review/SKILL.md`
- `templates/project/openspec/config.yaml.tpl`
- `openspec/specs/changerail-agent-methodology/spec.md`
- `openspec/specs/changerail-project-verification/spec.md`

## Result
not started

## Next
- Оставить exploration до появления конкретного воспроизводимого случая, где
  project-declared verification floor и acceptance mapping дали false-green.
- После такого evidence выполнить `$chrl-explore` на минимальном generic
  contract и одном Python proof.

## Triage Decision
- Keep в `1.backlog`, но не переводить в `2.todo` без доказанного verification
  gap: новая schema не должна дублировать OpenSpec tasks и review acceptance.
- Priority: strategic/deferred. Доставленная source classification учитывает
  BSL и Designer XML в complexity guard, но не связывает changed surface с
  invariant, oracle и required evidence, поэтому не supersede эту exploration.

## Change Plan Notes
Карточка намеренно остается exploration story. До перевода в `2.todo` нужно
доказать, что новый machine-readable contract уменьшает реальные пропуски
verification и не дублирует OpenSpec tasks, project instructions и review
acceptance mapping. Первая реализация, если она будет обоснована, должна
ограничиться generic extension boundary и одним Python proof.

## Log
- 2026-08-12T09:30:49Z карточка создана по итогам сравнения ChangeRail с Orca;
  полный reliability catalog и domain-specific core явно исключены из scope.
- 2026-08-19T14:05:00Z triage оставил карточку как deferred exploration:
  `changerail.source-classification.v1` закрыл source complexity, но не
  verification coverage; реализация без concrete false-green пока не
  обоснована.
