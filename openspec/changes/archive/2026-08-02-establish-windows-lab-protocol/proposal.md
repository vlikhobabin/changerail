## Why

Серия `030-native-windows-discovery` должна исследовать native Windows behavior
на operator-managed hosts, не смешивая private connection data с публичным
ChangeRail surface. Перед probe-карточками нужен reusable protocol, который
задает границы SSH, disposable workspaces, cleanup, timeout, evidence retention
и запрет elevation.

## What Changes

- Добавить публичный lab protocol для native Windows research с generic host ids
  `windows-host-a` и `windows-host-b`.
- Зафиксировать ignored inventory contract: raw host mapping, usernames,
  hostnames, credentials and disposable root values остаются outside tracked
  files.
- Добавить локально проверяемый dry-run harness contract для protocol/report
  generation без обращения к реальным Windows hosts.
- Описать no-elevation, timeout, cleanup и evidence retention правила для
  будущих Windows probes.

## Capabilities

### New Capabilities
- `changerail-windows-lab-protocol`: правила безопасного native Windows lab
  research protocol, ignored inventory, disposable workspaces, SSH execution,
  cleanup and evidence retention.

### Modified Capabilities
- none

## Impact

- `docs/compatibility.md` получает reusable Windows lab protocol.
- Новый local research harness/reporting surface остается generic и не меняет
  runtime/bootstrap behavior.
- Board card `030-01` получает apply-ready artifact plan для delivery.
