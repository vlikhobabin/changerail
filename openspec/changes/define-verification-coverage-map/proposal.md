## Why

Field validation зафиксировала три false-green случая, когда обязательные
команды и retained evidence существовали, но критичная acceptance route не
была связана с наблюдаемым oracle. Минимальная project-owned coverage map нужна,
чтобы сделать пропуск invariant детерминированным до independent review, не
создавая второй источник истины для acceptance и tasks.

## What Changes

- Определить `changerail.verification-coverage.v1` с минимальными полями `id`,
  `applies_to`, `invariant`, `oracle` и `required_evidence`.
- Хранить reusable coverage rules в tracked project config, а выбранный для
  карточки acceptance ledger выводить как derived runtime artifact.
- Зафиксировать extension boundary для domain-owned surface kinds без BSL/1C
  правил в generic core.
- Проверять schema safety, уникальность ids, normalized repository-relative
  selectors и отсутствие автоматического pass по одному file glob.
- Добавить generic Python fixture, показывающую связь changed surface,
  invariant, runtime oracle и evidence kind.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-contracts`: публичная schema и runtime ledger contract описывают
  verification coverage без дублирования acceptance verdict.
- `changerail-project-templates`: consumer config документирует optional
  project-owned coverage map и domain extension boundary.

## Impact

- новые schemas для coverage map и derived ledger
- `templates/project/openspec/config.yaml.tpl` и board guidance
- schema inventory, validation smokes и generic Python fixtures
- public docs для project-owned verification policy
