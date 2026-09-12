# Сузить машинные гварды и чтение allowance

## Status
1.backlog

## Lifecycle
openspec-v1

## Owner
unassigned

## Source
- Разбор семи падений полного набора 2026-09-12: `_no_live_delivery` падает fail-closed на посторонних процессах машины.
- Измерение: на рабочей машине 7 постоянных процессов того же uid с недоступным `/proc/<pid>/environ` (systemd, `(sd-pam)`, ssh-agent ×2, gpg-agent, sshd-session, sftp-server).
- Наблюдение при починке тестов: `review_allowance_status` бросает исключение вместо отчёта для run вне `RUNTIME_ROOT`.

## Summary
Два места читают состояние шире, чем это нужно для их задачи, и из-за этого
зависят от постороннего окружения.

`engine_snapshot._no_live_delivery` при `PermissionError` на `/proc/<pid>/environ`
считает потенциальным раннером любой процесс, чей `cmdline` содержит
`python`/`codex`/`chrl`/`changerail`/`pytest`/`bash`/`/sh`, и отказывает
(«cannot prove delivery runner is inactive»). На обычной рабочей машине это может
случайно блокировать `engine-bind`, rebind и self-host recovery.

`review_allowance_status(..., read_only=True)` для run, лежащего вне
`RUNTIME_ROOT/runs`, уходит в строгий `_run` и бросает исключение — вместо того
чтобы сообщить, что allowance для такого run не выводится. Из-за этого
`build_metrics` падает на нестандартном, но читаемом run.

## Acceptance
### Requirement: Гвард живого владельца остаётся точным, но не ловит посторонних
#### Scenario: Недоступный процесс без отношения к проекту
- [C1] `_no_live_delivery` не отказывает из-за процесса, который не может быть владельцем этого проекта. Атрибуция сужается до признаков, действительно связывающих процесс с проектом (например, доступные `cwd`/`cmdline`/окружение), а не до «похоже на shell или python».

#### Scenario: Реальный живой владелец по-прежнему блокирует
- [C2] Процесс, действительно владеющий доставкой этого проекта, по-прежнему блокирует rebind и self-host apply. Существующий тест гварда остаётся и проходит.

#### Scenario: Недоступность не превращается в тихое разрешение
- [C3] Если атрибуция невозможна и процесс потенциально относится к проекту, поведение остаётся fail-closed; отказ сопровождается диагностикой, позволяющей понять причину.

### Requirement: Чтение allowance сообщает, а не падает
#### Scenario: Run вне поддержанного контура
- [C4] `build_metrics` для читаемого run вне `RUNTIME_ROOT/runs` возвращает статус allowance с явной пометкой о невозможности расчёта, а не бросает исключение; запись метрик при этом не искажает accounting.

## Scope
- `scripts/changerail/engine_snapshot.py` (`_no_live_delivery`), `scripts/changerail/review_allowance.py`, `scripts/changerail/local_delivery.py` (`review_allowance_status`, `build_metrics`).
- `tools/changerail/tests/test_engine_snapshot.py`, `test_self_host_recovery.py`, `test_local_changerail_delivery.py`.
- `docs/self-host-recovery.md` — при изменении формулировки границы.

## Non-Goals
- Не ослаблять блокировку реального живого владельца доставки.
- Не менять модель полномочий review allowance.
- Не заниматься здесь тестовой инфраструктурой и осиротевшими документами.

## Affected Capabilities
- `native-delivery`

## Depends On
- none

## OpenSpec Changes
- none yet; a change is created before admission.

## Design
- Реализация будет описана в связанном design.md: сужение атрибуции процесса и статус allowance без исключения.

## Delivery Budget
- primary_invariant: гвард живого владельца блокирует только процессы, относимые к проекту, и остаётся fail-closed при неопределимости
- expected_wall_minutes: 120
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 3
- estimated_production_loc: 120

## Canonical Specs
- `openspec/specs/native-delivery/spec.md`

## Verify
```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [
    {"condition": "C1", "seam": "unrelated unreadable process", "precondition": "Same-uid processes whose /proc environ is unreadable and unrelated to the project", "action": "Run rebind and self-host prepare while such processes exist", "expected": "No refusal; diagnostic does not claim a live project owner", "method": {"kind": "test", "target": "tools/changerail/tests/test_engine_snapshot.py"}, "stage": "implementation"},
    {"condition": "C2", "seam": "real live owner", "precondition": "A live process whose environment owns this project's runtime", "action": "Attempt rebind and self-host apply", "expected": "Refused with the live-owner diagnostic", "method": {"kind": "test", "target": "tools/changerail/tests/test_engine_snapshot.py::test_rebind_rejects_live_run_owner"}, "stage": "implementation"},
    {"condition": "C3", "seam": "unattributable process", "precondition": "An unreadable process that may belong to the project", "action": "Attempt rebind", "expected": "Fail-closed refusal with actionable diagnostics", "method": {"kind": "test", "target": "tools/changerail/tests/test_self_host_recovery.py"}, "stage": "implementation"},
    {"condition": "C4", "seam": "allowance report for atypical run", "precondition": "A readable run outside RUNTIME_ROOT/runs with the native contract", "action": "Call build_metrics and read the allowance field", "expected": "A status is reported without raising and without altering accounting", "method": {"kind": "test", "target": "tools/changerail/tests/test_local_changerail_delivery.py::test_metrics_separate_agent_and_deterministic_commands"}, "stage": "final"}
  ],
  "risks": [
    {"kinds": ["input_safety"], "applies": true, "decision": "Narrowing must not turn a genuine project owner into an allowed transition; unattributable cases stay fail-closed", "conditions": ["C1", "C2", "C3"]},
    {"kinds": ["concurrency"], "applies": true, "decision": "Process scanning stays read-only and race-tolerant (ProcessLookupError/FileNotFoundError handled)", "conditions": ["C1", "C3"]},
    {"kinds": ["mutation", "restart"], "applies": false, "decision": "No receipt, lease or ancestry semantics change", "conditions": []},
    {"kinds": ["publication", "external_effects"], "applies": false, "decision": "Local process scanning only; no network", "conditions": []}
  ]
}
```
- `./bin/test-changerail`
- `git diff --check`

## Related
- `scripts/changerail/engine_snapshot.py` (`_no_live_delivery`)
- `scripts/changerail/review_allowance.py`
- `.runtime/planning/repo-cleanup/UNPUBLISHED-WORK-ASSESSMENT.md`

## Result
not started

## Next
- triage

## Log
- 2026-09-12T18:00:00Z карточка создана по итогам починки семи падений; тесты отвязаны от машинного скана, сам гвард не менялся.
