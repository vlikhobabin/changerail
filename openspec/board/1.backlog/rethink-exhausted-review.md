# Выход из двух подряд NO-GO: разбор, выбор, продолжение

## Status
1.backlog

## Lifecycle
openspec-v1

## OpenSpec Stage
artifacts

## Owner
unassigned

## Source
- Поручение оператора 2026-09-12: два NO-GO — это рабочая ситуация, а не тупик; оркестратор должен разобрать каждый случай, найти системное решение или предложить оператору варианты, и после решения продолжить карточку.
- Реальный прогон `.runtime/changerail/runs/20260912T091333Z-restore-accepted-task-wording`: цикл 1 — R1–R4 blocker и не пройдены C1/C2/C3; цикл 2 — «R1 still lacks…», «R2 remains… Finish prior R2», C3 стал pass.
- Текущий код: `orchestrate_delivery` после NO-GO вызывает `review_allowance.require_remaining`, который при исчерпании бросает `DeliveryError`.

## Summary
После второго подряд NO-GO доставка останавливается ошибкой, и разбора причин не
делает никто: следующий заход (если оператор выдаст +1) идёт по тому же шаблону
«починить перечисленные findings». На реальном прогоне это привело к тому, что
ремонт повторил те же R1/R2, а требуемое доказательство для C1/C2 так и не
появилось.

Нужен ограниченный разбор: после каждого NO-GO — детерминированный анализ
повторяемости, при исчерпании — стадия диагностики, которая классифицирует
ситуацию и предлагает варианты. Если системный путь внутри scope есть — работа
продолжается; если вариантов несколько, нужен пересмотр плана или архитектуры,
либо это инфраструктурный блокер — оператор получает структурированный выбор, и
после решения работа продолжается по той же карточке.

## Acceptance
### Requirement: Разбор каждого NO-GO
#### Scenario: Детерминированный разбор истории
- [C1] Для каждой завершённой пары и более NO-GO строится разбор: какие findings повторяются, какие закрыты, какие новые, менялись ли условия и пути. Разбор не изменяет вердикты, план и карточку и попадает в контекст следующего ремонта.

### Requirement: Классификация при исчерпании
#### Scenario: Ограниченная диагностика
- [C2] При исчерпании остатка выполняется одна идемпотентная диагностика, привязанная к точному состоянию линии: она относит ситуацию к классу из закрытого набора (`repeat_defect`, `incomplete_work`, `plan_conflict`, `evidence_model_gap`, `unreproducible`, `infrastructure`, `unsatisfiable`) и формирует варианты. Повтор при неизменном состоянии не создаёт второй разбор; изменившееся состояние делает прежний разбор неприменимым.

### Requirement: Диагностика не даёт полномочий
#### Scenario: Предложение, а не разрешение
- [C3] Диагностика не расходует и не выдаёт review-слот, не меняет Acceptance и scope, не ослабляет гейты и не продолжает доставку. Runtime проверяет класс по сохранённому состоянию и отклоняет противоречащий разбор. Worker не может использовать разбор как полномочие.

### Requirement: Операторский выбор и продолжение
#### Scenario: Штатная остановка, выбор, продолжение
- [C4] Когда системного пути нет, доставка останавливается штатным состоянием `awaiting-operator-decision` с сохранением истории, accounting и frozen identity, и оператор получает варианты с эффектом, ценой, предусловиями и рекомендацией. Выбор фиксируется неизменяемой записью и продолжает работу по той же карточке: системный ремонт с обычным независимым ревью, либо закрытие неуспешной попытки и отдельное принятие нового плана, либо маршрут технического восстановления. Автоматического продолжения без решения оператора нет; недопустимый выбор отклоняется до запуска writer.

## Scope
- `scripts/changerail/exhaustion_diagnosis.py` (новый модуль), `native_workflow.py`, `local_delivery.py`, `review_allowance.py`: разбор повторяемости, стадия диагностики, состояние ожидания, запись выбора, маршруты продолжения.
- `tools/changerail/schemas/exhausted-review-diagnosis.schema.json`: схема разбора.
- `tools/changerail/skills/chrl-exhaustion-diagnosis/SKILL.md`: навык сессии диагностики; затронутые навыки deliver/review.
- `tools/changerail/tests/test_exhaustion_diagnosis.py` и затронутые execution-contract тесты: синтетические регрессии C1–C4, включая реальный случай двух NO-GO.
- `docs/operations.md`, `templates/profile.toml`, `tools/changerail/templates/profile.toml`: инструкция и роль диагностики.

## Non-Goals
- Автоматическое третье ревью без слота и отмена лимита двух автономных ревью.
- Автоматическое изменение Acceptance, scope или архитектуры.
- Замена технического восстановления при инфраструктурных отказах.
- Универсальный планировщик и переписывание истории или accounting.

## Affected Capabilities
- `native-delivery`

## Depends On
- none

## OpenSpec Changes
1. `rethink-exhausted-review`

## Design
- Реализация принадлежит `design.md`: дешёвый разбор повторяемости после каждого NO-GO и модельная диагностика один раз на исчерпание.
- Evidence seams: повторяющийся и закрытый дефект, идемпотентность разбора, проверка класса runtime'ом, отсутствие полномочий, штатная остановка, запись выбора и три маршрута продолжения.
- Runtime-safety: разбор неизменяем, привязка к точному состоянию линии, отказ при изменившемся payload, запрет записи writer без решения.
- Граница доверия такая же, как у `review-allow`: кооперативный протокол одного UID без заявки на OS-аутентификацию.

## Delivery Budget
- primary_invariant: исчерпание двух ревью даёт обоснованный выбор и продолжение работы вместо тупика, не ослабляя ни один гейт и не давая диагностике полномочий
- expected_wall_minutes: 300
- production_owners: 1
- runtime_contours: 1
- estimated_product_files: 10
- estimated_production_loc: 900

## Canonical Specs
- `openspec/specs/native-delivery/spec.md`

## Verify
- Планируемые проверки; реализация не начата.
```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {"condition": "C1", "seam": "recurrence across verdicts", "precondition": "Synthetic lineage with two NO-GO verdicts where one condition closes and others repeat", "action": "Build the recurrence digest and inspect it", "expected": "Repeated and closed findings are labelled; verdicts, plan and card are byte-identical", "method": {"kind": "test", "target": "tools/changerail/tests/test_exhaustion_diagnosis.py"}, "stage": "implementation"},
    {"condition": "C2", "seam": "bounded idempotent diagnosis", "precondition": "Exhausted lineage state", "action": "Run diagnosis twice on unchanged state, then change the payload and re-run", "expected": "One diagnosis per state; the stale one becomes inapplicable; class is cross-checked against observations", "method": {"kind": "test", "target": "tools/changerail/tests/test_exhaustion_diagnosis.py"}, "stage": "implementation"},
    {"condition": "C3", "seam": "no authority from diagnosis", "precondition": "A diagnosis proposing an in-scope systemic repair with no granted slot", "action": "Attempt to continue delivery and to change Acceptance from the diagnosis", "expected": "Writer does not start, criteria and scope stay unchanged, refusal is explicit", "method": {"kind": "test", "target": "tools/changerail/tests/test_native_execution_contract.py"}, "stage": "implementation"},
    {"condition": "C4", "seam": "operator choice and continuation", "precondition": "No supported automatic path", "action": "Observe the awaiting state, record each option, and exercise in-scope repair, plan revision and technical recovery routes", "expected": "Stop is a normal state with preserved history; each choice continues on the same card or closes and replans separately; invalid choices are rejected before any writer", "method": {"kind": "test", "target": "tools/changerail/tests/test_exhaustion_diagnosis.py"}, "stage": "final"}
  ],
  "risks": [
    {"kinds": ["input_safety"], "applies": true, "decision": "Closed class set, runtime cross-check of the class against observations, and refusal of diagnoses that contradict state", "conditions": ["C2", "C3"]},
    {"kinds": ["mutation", "restart"], "applies": true, "decision": "Idempotent diagnosis bound to exact lineage state; immutable operator choice record; history and accounting preserved byte-for-byte", "conditions": ["C1", "C2", "C4"]},
    {"kinds": ["concurrency"], "applies": true, "decision": "Project delivery lock and single-writer rules apply; operator choice is exclusive and non-accumulating", "conditions": ["C3", "C4"]},
    {"kinds": ["publication"], "applies": true, "decision": "Diagnosis cannot publish or declare success; closure never creates GO, archive, commit or push", "conditions": ["C4"]},
    {"kinds": ["external_effects"], "applies": false, "decision": "Local synthetic lineages and git fixtures only; no network or provider runtime changes", "conditions": []}
  ]
}
```
- `./.changerail/openspec validate rethink-exhausted-review --strict --no-interactive`
- `./bin/test-changerail`
- `./.venv/bin/python -m ruff check scripts tools/changerail/tests distribution.py`
- `git diff --check`

## Related
- `openspec/changes/rethink-exhausted-review/proposal.md`
- `openspec/changes/rethink-exhausted-review/design.md`
- `openspec/changes/rethink-exhausted-review/specs/native-delivery/spec.md`
- `openspec/changes/rethink-exhausted-review/tasks.md`
- `openspec/board/1.backlog/add-operator-review-allowance.md` — существующий операторский +1, используется как один из маршрутов
- `openspec/changes/close-exhausted-native-delivery/` — закрытие попытки как один из вариантов
- `.runtime/changerail/runs/20260912T091333Z-restore-accepted-task-wording` — реальный случай двух NO-GO

## Result
План подготовлен, реализация не начата. Диагностика спроектирована как
предложение без полномочий: она не расходует review и не продолжает доставку.
Ожидает решения оператора по открытым вопросам (модель роли, формат отчёта).

## Next
- Подтвердить дизайн и открытые вопросы, затем реализовать по группам tasks.md.

## Log
- 2026-09-12T18:30:00Z карточка создана по поручению оператора; change и план подготовлены, код не менялся.
