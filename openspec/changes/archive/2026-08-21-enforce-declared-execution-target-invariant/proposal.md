## Why

Если обязательная внешняя среда временно недоступна, delivery worker сейчас
может получить доказательства на созданной или выбранной замене, хотя проект
ожидал проверку на одной объявленной цели. ChangeRail нужен generic fail-closed
инвариант identity, не зависящий от конкретной платформы и не дающий authority
на provision, rebind или substitution.

## What Changes

- Добавить optional tracked contract `.changerail/execution-target.json` с
  logical id, non-sensitive fingerprint и фиксированной policy `forbid`.
- Переносить exact target identity через planning manifest, delivery status,
  blocker/resume lineage и review evidence; endpoint, credentials и target
  contents в ChangeRail не попадают.
- Fail closed при missing/multiple/mismatched target evidence, declaration
  drift или попытке substitution; explicit rebind начинает новый clean attempt.
- Централизовать загрузку и сравнение declaration в одном shared validator и
  удержать production-counted delta не выше 500 строк.
- Обновить reusable skills, project templates, verification и synthetic smoke
  fixtures без platform-specific логики.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: optional execution-target declaration, retained
  identity и evidence binding.
- `changerail-agent-methodology`: запрет неявной подмены и clean rebind flow.
- `changerail-delivery-runner`: capture, drift checks и propagation target
  identity через single-card/package lifecycle.
- `changerail-project-templates`: public-safe optional declaration surface.
- `changerail-project-verification`: schema и consistency checks declaration.
- `changerail-skill-surface`: planning, delivery и review obligations для
  declared target.

## Impact

Затрагиваются schemas contracts/manifest/status/evidence, shared manifest
helper, `verify-project`, delivery runner, deterministic review preflight,
canonical skills/templates, contract/runner/review/verification smokes и
operator documentation. Для проектов без declaration поведение совместимо с
текущим workflow.
