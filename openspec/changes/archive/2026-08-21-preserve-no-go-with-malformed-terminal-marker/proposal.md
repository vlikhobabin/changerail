## Why

После исчерпания review budget child может правдиво записать canonical
`no-go`, но ошибиться в spelling `terminal_reason`. Сейчас распознанный
`BLOCKED/malformed_terminal_reason` безусловно перекрывает более сильное
negative review evidence, поэтому aggregate supervisor сообщает технический
blocker вместо требуемого `NO-GO` handoff.

## What Changes

- Разрешить schema-valid canonical `no-go` заменить только malformed child
  terminal marker.
- Сохранить существующую fail-closed классификацию для malformed marker без
  valid negative verdict и для всех positive verdict paths.
- Добавить regression smoke для сочетания final no-go и malformed marker.

## Capabilities

### Modified Capabilities
- `changerail-delivery-runner`: уточнить приоритет conservative negative
  review evidence при malformed child diagnostics.

## Impact

Затронуты generic delivery runner, его smoke fixture, normative spec и public
contracts guide. Schema, authority и wire protocol не меняются.
