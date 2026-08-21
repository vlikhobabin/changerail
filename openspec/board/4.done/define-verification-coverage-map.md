# Определить минимальную карту verification coverage

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
- Сравнение ChangeRail с Orca от 2026-08-12.
- [Orca reliability gates](https://github.com/stablyai/orca/blob/main/config/reliability-gates.jsonc)
- `skills/changerail-do/SKILL.md`
- `skills/changerail-review/SKILL.md`
- `templates/project/openspec/config.yaml.tpl`
- `openspec/specs/changerail-project-verification/spec.md`

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `yes`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `{"authorization_card":"openspec/board/4.done/authorize-bounded-verification-coverage-payload.md","authorization_id":"authorize-bounded-verification-coverage-payload"}`

Published investigation `investigate-bounded-field-validation-batch` закрывает
repeated-defect classification для одного bounded verification-coverage
hypothesis. Field evidence обосновывает contract, но перед implementation
review новый verification-admission protocol требует exact published source
`authorize-bounded-verification-coverage-payload`.

## Depends On
- `investigate-bounded-field-validation-batch`
- `authorize-bounded-verification-coverage-payload`

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
- `define-verification-coverage-map`
- `enforce-verification-coverage-ledger`

## Verify
- `python3 scripts/smoke-contract-schemas.py`
- `python3 scripts/smoke-review-preflight.py`
- `python3 scripts/smoke-verify-project.py`
- `python3 scripts/smoke-bootstrap-project.py`
- `python3 scripts/smoke-drift.py --project .runtime/changerail/ci-drift/verification-coverage-map-project`
- `bin/openspec validate --all --strict`
- `git diff --check`
- `python3 scripts/public-surface-scan.py`

## Archive
- `openspec/changes/archive/2026-08-21-define-verification-coverage-map/`
- `openspec/changes/archive/2026-08-21-enforce-verification-coverage-ledger/`

## Related
- `AGENTS.shared.md`
- `skills/changerail-ff/SKILL.md`
- `skills/changerail-do/SKILL.md`
- `skills/changerail-review/SKILL.md`
- `templates/project/openspec/config.yaml.tpl`
- `openspec/specs/changerail-agent-methodology/spec.md`
- `openspec/specs/changerail-project-verification/spec.md`
- `openspec/changes/define-verification-coverage-map/`
- `openspec/changes/enforce-verification-coverage-ledger/`
- `openspec/board/4.done/authorize-bounded-verification-coverage-payload.md`

## Result
Implementation complete: project-owned coverage map, fingerprint-bound
plan/ledger contracts, deterministic review-preflight enforcement and lifecycle
skill guidance delivered.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Triage Decision
- Перевести в `2.todo`: field validation доказала verification gap, а выбранный
  contract ссылается на acceptance/tasks/evidence вместо их копирования.
- Priority: high. Source classification остается отдельным complexity guard и
  не заменяет invariant/oracle/evidence coverage.

## Change Plan Notes
Tracked project map содержит только five-field rules; per-change plan хранит
rule ids/acceptance hashes, ignored ledger — fingerprints и evidence refs.
Review verdict остается единственным acceptance authority. Реализация
ограничена generic extension boundary и одним synthetic Python proof.

## Change 1: `define-verification-coverage-map`

### Why
Current floor не может детерминированно отличить green known commands от
пропущенного known invariant/oracle.

### Goal
Добавить optional five-field project map, tracked per-change references,
ignored runtime ledger schema и namespaced domain extension boundary.

### Acceptance
- Entries ограничены `id`, `applies_to`, `invariant`, `oracle`,
  `required_evidence` и fail closed на unsafe/incomplete policy.
- Map/card остаются sources; plan/ledger хранят ids, hashes and refs.
- No-map consumers сохраняют current verification floor.
- Generic Python example и domain namespaced IDs не встраивают 1С rules в core.

### Depends On
- `investigate-bounded-field-validation-batch`
- separate exact published investigation authorization for this card's
  verification coverage protocol

### Related
- `openspec/changes/define-verification-coverage-map/`
- `openspec/board/4.done/investigate-bounded-field-validation-batch.md`

## Change 2: `enforce-verification-coverage-ledger`

### Why
Schema не предотвращает false-green без reconciliation actual scope и evidence
до independent review.

### Goal
Связать `ff -> do -> deterministic preflight -> review` через один
fingerprint-bound plan/ledger и существующий evidence index/manifest/verdict.

### Acceptance
- `ff` объявляет selected ids, `do` reconciles actual scope/evidence.
- Missing/stale applicable coverage blocks deterministic preflight.
- Reviewer проверяет published boundary/test adequacy; path/exit zero не дают
  automatic acceptance pass.
- Synthetic Python proof ловит missing positive route, internal-only timeout и
  disconnected integration paths.

### Depends On
- `define-verification-coverage-map`

### Related
- `openspec/changes/enforce-verification-coverage-ledger/`

## Log
- 2026-08-12T09:30:49Z карточка создана по итогам сравнения ChangeRail с Orca;
  полный reliability catalog и domain-specific core явно исключены из scope.
- 2026-08-19T14:05:00Z triage оставил карточку как deferred exploration:
  `changerail.source-classification.v1` закрыл source complexity, но не
  verification coverage; реализация без concrete false-green пока не
  обоснована.
- 2026-08-20T17:30:00Z field validation supplied the missing concrete case:
  three critical 1C deliveries reached independent review with retained
  evidence, but reviewers still found an unproved positive route, a timeout
  assertion that did not exercise the published boundary, and a renderer/form
  proof that used disconnected paths. Promote this from strategic/deferred to
  high-priority exploration of a deterministic pre-review acceptance ledger.
- 2026-08-21T07:43:31Z research accepted an optional project map plus tracked
  id/hash plan and ignored evidence ledger; contract and enforcement changes
  reached apply-ready state.
- 2026-08-21T09:10:00Z bounded field-validation investigation зафиксировало
  exact verification-coverage hypothesis, one shared loader boundary, ceiling
  500 и requirement нового split при повторе того же blocker.
- 2026-08-21T11:06:12Z linked exact published authorization source
  `authorize-bounded-verification-coverage-payload`; successor remains queued
  until that source is published in `4.done`.
- 2026-08-21T19:01:43Z delivered and archived
  `define-verification-coverage-map` and
  `enforce-verification-coverage-ledger`; verification gates passed and card
  moved to review handoff.
- 2026-08-21T19:55:10Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
