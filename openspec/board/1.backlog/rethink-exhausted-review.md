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
Фактический объём (сверен с реализацией 2026-09-12; плановая оценка называла
отдельный файл схемы и отдельный skill — по design.md диагностика является
режимом сессии доставки, а схема живёт константой в модуле):
- `scripts/changerail/exhaustion_diagnosis.py` (новый модуль): разбор повторяемости, классы, варианты, артефакт диагностики, запись выбора и амендмента, автоматический маршрут инфраструктуры, состояние решения.
- `scripts/changerail/local_delivery.py`, `review_allowance.py`, `contracts.py`: `ReviewExhausted`/`AwaitingDecision`, состояние `awaiting-operator-decision`, продолжение по записанному выбору, CLI `rethink`.
- `scripts/changerail/native_workflow.py`: `stop_state` и `awaiting_decision` в `status`.
- `tools/changerail/skills/chrl-native-deliver/SKILL.md`: правило `CHRL_DIAGNOSIS_CONTEXT` (диагностика — не ревью и не полномочие).
- `tools/changerail/tests/test_exhaustion_diagnosis.py`, `test_review_allowance_integration.py`: регрессии C1–C4, включая форму реального случая двух NO-GO, отсутствие полномочий на реальном resume-маршруте, дохождение решения до продолжения, остановку на отдельном маршруте и неприменимость решения после изменения payload.
- `docs/operations.md`, `templates/profile.toml`, `tools/changerail/templates/profile.toml`: инструкция и необязательный route `[models.diagnosis]`.

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
    {"condition": "C3", "seam": "no authority from diagnosis", "precondition": "A diagnosis proposing an in-scope systemic repair with no granted slot", "action": "Record the choice, then attempt to continue delivery and to change Acceptance from the diagnosis", "expected": "Writer does not start, allowance, criteria and scope stay unchanged, refusal is explicit", "method": {"kind": "test", "target": "tools/changerail/tests/test_review_allowance_integration.py::test_diagnosis_grants_no_slot_and_never_continues_delivery"}, "stage": "implementation"},
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
Выполнено 2026-09-12 для решения `5a12c46` (проверки воспроизводимы на этом
коммите):
- `./.changerail/openspec validate --all --strict --no-interactive` — 4 passed.
- `./.venv/bin/python -m pytest -q tools/changerail/tests/test_exhaustion_diagnosis.py tools/changerail/tests/test_review_allowance_integration.py tools/changerail/tests/test_native_execution_contract.py tools/changerail/tests/test_native_openspec_integration.py` — 116 passed.
- `./.venv/bin/python -m pytest -n 16 tools/changerail/tests -q` — 1278 passed за 4:53.
- `./.venv/bin/python -m ruff check scripts tools/changerail/tests distribution.py` — All checks passed.
- `git diff --check` — clean.
- `./.venv/bin/python scripts/public-surface-scan.py` — pass, 0 findings.
- Регрессии проверены на осмысленность: те же тестовые файлы из `5a12c46`,
  запущенные против прежнего кода `f399917` во временном worktree, падают
  11 раз (`test_recorded_decision_reaches_the_continuation`,
  `test_re_review_decision_skips_repair_and_reviews_the_unchanged_payload`,
  `test_separate_route_decision_stops_instead_of_repairing`,
  `test_payload_change_makes_the_decision_and_diagnosis_stale`, плюс семь тестов
  диагностики), то есть они действительно доказывают исправления, а не
  повторяют текущее поведение.
- `./bin/test-changerail` не запускался: dev-лаунчер осознанно отказывает в
  checkout'е инструмента, полный набор принадлежит CI ChangeRail.

## Related
- `openspec/changes/rethink-exhausted-review/proposal.md`
- `openspec/changes/rethink-exhausted-review/design.md`
- `openspec/changes/rethink-exhausted-review/specs/native-delivery/spec.md`
- `openspec/changes/rethink-exhausted-review/tasks.md`
- `openspec/board/1.backlog/add-operator-review-allowance.md` — существующий операторский +1, используется как один из маршрутов
- `openspec/changes/close-exhausted-native-delivery/` — закрытие попытки как один из вариантов
- `.runtime/changerail/runs/20260912T091333Z-restore-accepted-task-wording` — реальный случай двух NO-GO

## Result
Реализовано 20 из 21 задачи. После каждого NO-GO строится разбор повторяемости и
попадает в контекст ремонта; при исчерпании появляется диагностика с закрытым
набором классов, обоснованием и вариантами, а неопределённая ситуация
уточняется одной ограниченной сессией, если в профиле задан route
`[models.diagnosis]`. Runner отвергает класс, отрицающий наблюдаемое. Оператор
фиксирует выбор и изменение критерия двухфазными неизменяемыми записями, CLI
`chrl rethink` показывает разбор и записывает решение. Записанный выбор даёт
конкретное продолжение: повторное ревью, ремонт с изменённым подходом, закрытие
попытки и новый план либо маршрут технического восстановления.

Исчерпание остатка больше не является ошибкой: run останавливается штатным
состоянием `awaiting-operator-decision` (код 3) с сохранением истории,
accounting и frozen identity, `status` отдаёт `stop_state` и
`awaiting_decision`, а повторный `resume` уже исчерпанного run возвращает ту же
точку решения, читая сохранённый разбор предшественника и не переписывая его.
Инфраструктурный класс автоматически готовит существующее техническое
восстановление под его собственными гейтами; отказ гейта сообщается, а не
продавливается.

Проверено: 38 тестов диагностики (включая форму реального случая
`restore-accepted-task-wording`, кросс-проверку модельного класса и
автоматический маршрут инфраструктуры, охват линии восстановления, привязку к
плану и payload), 16 тестов реального resume-маршрута учёта слотов (включая C3 —
диагностика и записанный выбор не дают слота и не продолжают доставку, и C4 —
решение доходит до продолжения, отдельный маршрут останавливает продолжение, а
изменение payload делает решение неприменимым), 49 тестов execution contract,
полный набор 1278 тестов.

Внешний независимый review коммитов `4fe6645`/`f399917` дал NO-GO и был
исправлен коммитом `5a12c46`; findings 1–14 разобраны, что именно сделано и что
сознательно оставлено иначе — в Log.

Осталось: 5.4 — повторный узкий внешний review коммита `5a12c46` и архивация
change после вердикта. Это операторское действие: worker не выдаёт себе ревью.

## Next
- Реализация change — коммиты `be40f82..5a12c46` (разбор повторяемости, схема
  диагностики, операторские записи, модельная диагностика, состояние решения,
  исправление по внешнему review); карточная часть — `79a7171`.
- Передать коммит `5a12c46` на узкий повторный review: маршрутизация решения в
  продолжение (включая отдельные маршруты), путь артефакта диагностики и гейт
  автоматического маршрута, кросс-проверка класса, эксклюзивность выбора,
  привязка к плану и payload, регрессии C4 по переходам.
- После вердикта применить delta-спеку и архивировать change.

## Log
- 2026-09-12T18:30:00Z карточка создана по поручению оператора; change и план подготовлены, код не менялся.
- 2026-09-12T19:30:00Z реализованы группы 1, 2.1-2.2, 2.5, 3.2-3.4: разбор повторяемости, артефакт диагностики с классами и вариантами, операторские записи выбора и амендмента, CLI `chrl rethink`; разбор выводится в точке исчерпания. Оператор подтвердил: отдельная модель роли в профиле, изменение критерия — отдельным решением.
- 2026-09-12T20:30:00Z добавлены модельная диагностика (route `[models.diagnosis]`, контекст, артефакт, кросс-проверка класса, правило навыка), продолжение по записанному выбору и операторская документация. 17/20 задач.
- 2026-09-12T22:10:00Z закрыты 3.1 и 4.3: исчерпание стало штатным состоянием `awaiting-operator-decision` вместо пути ошибки (`ReviewExhausted`, `AwaitingDecision`, код 3, `stop_state`/`awaiting_decision` в `status`), инфраструктурный класс автоматически готовит техническое восстановление под его гейтами. Коммит `4fe6645`.
- 2026-09-12T23:20:00Z внешний независимый review коммитов `4fe6645`/`f399917`: NO-GO. Подтвердил два блокера (решение оператора не доходит до продолжения; артефакт модельной диагностики пишется туда, где runner его не читает) и добавил ещё двенадцать находок: гейт автоматического маршрута опирается на класс, а не на наблюдаемое; класс без подтверждающих наблюдений принимается; у амендмента нет автора и потребителя; у вариантов нет предусловий; привязка разбора не включает план и payload; разбор видит только текущий run; исчерпание после финальной проверки остаётся путём ошибки; выбор накапливается; документация и покрытие `status` неполны. Отмечено как верное: `remaining = 2 + grants - spent`, диагностика не выдаёт слот, frozen run не перезаписывается, новый `except AwaitingDecision` не меняет смысл прежних отказов.
- 2026-09-12T23:55:00Z исправлено коммитом `5a12c46`: решение читается у непосредственного предшественника и попадает в recovery- и repair-контекст; переходы, требующие отдельного маршрута, останавливают продолжение вместо подмены ремонтом; `re-review` действительно повторяет ревью неизменённого payload (runner восстанавливает scope и pre-review floor детерминированно); артефакт диагностики называется репозиторно-относительным путём; в digest входят принятый план и payload; повторяемость охватывает всю линию восстановления; модель не может приписать ситуацию критерию или плану без сравнимых наблюдений; варианты несут предусловия; выбор эксклюзивен и идемпотентен; амендмент связывает автора и время; исчерпание после финальной проверки — тоже точка решения; `status` покрыт тестом. Два расхождения с первоначальным текстом зафиксированы ниже.
- 2026-09-12T23:55:00Z сознательные отклонения от первоначального плана: (1) автоматический маршрут инфраструктуры остаётся предложением модели, а не только детерминированного разбора, потому что детерминированный разбор по вердиктам не может установить инфраструктуру вообще; авторитетом сделан существующий гейт `technical_recovery.prepare`, который требует сохранённого доказанного отказа ёмкости, а отказ сообщается — это записано в коде, тестах и документации; (2) амендмент критерия фиксирует новую формулировку, но не применяет её сам: применение к карточке и принятому плану идёт обычным маршрутом принятия, и до этого доставка не продолжается — формулировка delta-спеки приведена к этому явно.
- 2026-09-12T22:40:00Z закрыт разрыв в доказательствах C3: объявленный target `test_native_execution_contract.py` не содержал ни одной проверки диагностики. Регрессия перенесена на реальный маршрут resume/учёта слотов (`test_diagnosis_grants_no_slot_and_never_continues_delivery`) и проверяет, что разбор и записанный выбор не расходуют и не выдают слот, не создают writer, не меняют карточку, scope и байты frozen run. Объявленный Scope карточки сверен с реализацией: отдельный файл схемы и отдельный skill заменены на константу в модуле и правило в навыке доставки (по design.md). 5.3 выполнено, 5.4 — внешний review.
