# <Task Title>

## Status
1.backlog

## Lifecycle
openspec-v1

## Owner
unassigned

## Source
- <session, finding, commit, or document>

## Summary
<What must change and why.>

## Acceptance
### Requirement: <stable obligation>
#### Scenario: <observable use>
- [C1] <observable outcome>

## Scope
- <exact affected paths or subsystem>

## Non-Goals
- <explicitly excluded work>

## Affected Capabilities
- `<capability>`

## Depends On
- none

## OpenSpec Changes
1. `<change-slug>`

## Design
<!-- The linked OpenSpec design.md owns implementation design. This section is
limited to evidence seams, risk mechanisms and runtime-safety decisions. -->
- <evidence seam, risk mechanism and runtime-safety decision>

<!-- Delivery Budget fields are estimates, not stop limits while
budgets.enforce_limits=false. Preserve one invariant and authorized scope. -->

## Delivery Budget
- primary_invariant: <one observable independently shippable invariant>
- expected_wall_minutes: 30
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: <nonnegative estimate>
- estimated_production_loc: <nonnegative estimate>

## Canonical Specs
- <openspec/specs/.../spec.md or none>

## Verify
- <focused command; this is a planned check, not completed evidence>

Начните с одного test target. Если нужны несколько различных проверок, добавьте
в method, например, `"additional_targets": ["tests/test_guards.py::test_rejects_invalid_input"]`.
Основной target и все объявленные дополнительные обязательны и не повторяются.
Выбирайте релевантные тесты, включая существующие проверки общих границ. Одно
исполнение может поддерживать несколько условий отдельными proof records без
повторного запуска или общего wrapper. Дополнительные targets требуют
поддерживающего runtime до принятия плана; каждый proof содержит один `{kind, target}`.

```json
{
  "schema": "changerail.card-evidence.v1",
  "conditions": [{
    "condition": "C1", "seam": "<seam>", "precondition": "<before-state>",
    "action": "<action>", "expected": "<observation>",
    "method": {"kind": "test", "target": "tests/test_example.py::test_case"},
    "stage": "implementation"
  }],
  "risks": [
    {"kinds": ["input_safety"], "applies": true, "decision": "<mechanism>", "conditions": ["C1"]},
    {"kinds": ["mutation", "restart"], "applies": false, "decision": "<concrete N/A reason>", "conditions": []},
    {"kinds": ["concurrency", "publication", "external_effects"], "applies": false, "decision": "<concrete N/A reason>", "conditions": []}
  ]
}
```
- `git diff --check`
- `python3 -m pytest -v tests/test_example.py::test_case`
- `uv run python -m compileall -q src tests`
- `./bin/openspec validate --specs --strict --no-interactive`

## Related
- <live path, canonical spec, commit, or historical evidence description>

## Result
not started

## Next
- triage

## Log
- <YYYY-MM-DDTHH:MM:SSZ> card created
