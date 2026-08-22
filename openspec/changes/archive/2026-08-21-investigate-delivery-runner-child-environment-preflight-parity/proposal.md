## Why

Агрегатный delivery plan может проходить publish-target preflight в процессе
supervisor, а затем немедленно останавливать первый child delivery worker на
эквивалентной проверке Git remote внутри Codex execution surface. Это
предсказуемый environment blocker, который должен выявляться до запуска
очереди, workspace lock и child process.

## What Changes

- Зафиксировать decision-only investigation для child-equivalent
  publish-target preflight.
- Описать public-safe deterministic reproducer, который различает
  supervisor-only pass и child-equivalent fail без настоящих credentials,
  private remotes или локальных runtime logs.
- Выбрать canonical preflight design с receipt binding к workspace, branch,
  remote class, execution profile и bounded freshness interval.
- Определить dispatch-time revalidation, чтобы drift во время serial queue
  ловился до запуска следующего child.
- Зафиксировать structured terminal contract для точных причин вроде
  `publish_target_preflight_failed`, `ssh_config` и retryability.
- Разделить bounded retry для DNS/timeout/transient transport и fail-closed
  поведение для auth, SSH policy/configuration и missing branch.
- Привязать точный implementation successor и verification floor без изменения
  production runner behavior в этом change.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-delivery-runner`: runner plan preflight and queue dispatch MUST
  prove publish-target readiness through a child-equivalent execution profile
  before aggregate admission and before each child dispatch.

## Impact

- Affected specs: `openspec/specs/changerail-delivery-runner/spec.md`.
- Affected future implementation surfaces: `bin/changerail-delivery-runner`,
  `bin/codex`, `schemas/changerail-delivery-run.schema.json`,
  `schemas/changerail-delivery-plan-status.schema.json`,
  `scripts/smoke-delivery-runner.py` and
  `docs/consumer-adoption-runbook.md`.
- This card does not change production runner, launcher, schema, skill or test
  behavior; it publishes the investigation decision and successor contract.
