## Why

`verify-project` проверяет ChangeRail wiring, но оператор может узнать о
missing delivery runner auth только после queue preflight failure. Verification
должен давать понятный non-fatal readiness advisory, не делая auth обязательным
для public CI, template smoke tests или non-runner consumers.

## What Changes

- Добавить delivery runner auth readiness advisory в consumer verification.
- Репортить effective project-local auth marker и supported env-var path без
  требования real credentials by default.
- Сохранить fail-closed behavior для существующих required wiring и
  ignore-policy checks.
- Указать оператору canonical remediation command или docs section.

## Capabilities

### New Capabilities

### Modified Capabilities
- `changerail-project-verification`: `verify-project` сообщает non-fatal
  delivery runner readiness advisory.

## Impact

- Затрагивает `bin/verify-project`, bootstrap output при post-bootstrap
  verification и verification smoke tests.
- Public CI и generated template smoke продолжают проходить без real auth
  marker.
