## Why

Delivery runner уже требует от unattended child политику
`approval_policy = "never"` и `sandbox_mode = "danger-full-access"`, но во
вложенной Codex execution surface эти значения могут не стать effective для
model-generated commands. В результате supervisor preflight проходит, а
реальный child останавливается на sandbox-specific Git/SSH failure до начала
delivery.

## What Changes

- Для tracked ChangeRail Codex launcher и явно заданного operator-owned
  `CODEX_HOME` runner передает Codex invocation-level bypass после успешной
  проверки уже существующей trusted automation policy.
- Preflight проверяет, что установленный Codex CLI поддерживает этот exact
  invocation mode, и fail-closed останавливается до child launch иначе.
- Custom launchers и generated default runtime homes сохраняют прежний argv.
- Добавляются RED/GREEN regression coverage и durable docs без новых required
  status fields.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: effective automation authority реального
  Codex child для explicit operator-owned runtime home.

## Impact

Затронуты `bin/changerail-delivery-runner`, delivery-runner smoke, durable
runner docs и capability spec. Wire schemas, credentials, consumer source и
custom launcher protocol не меняются.
