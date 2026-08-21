## Why

Длительный delivery-run остается внешне неотличимым от зависшего процесса:
поддерживаемый status сообщает только общий `delivery/RUNNING`, а чтение raw
JSONL небезопасно и не является публичным контрактом. Нужен bounded progress
channel, который обновляется самим lifecycle и не зависит от разбора prose,
команд или output дочернего агента.

## What Changes

- Расширить single-card status объектом `progress` с версией схемы, bounded
  lifecycle phase/stage, heartbeat и монотонным счетчиком событий.
- Добавить value-free канал structured progress events между lifecycle child и
  runner с проверкой run/card identity и атомарным обновлением status.
- Зеркалировать последнее безопасное progress-состояние активной карточки в
  aggregate plan status.
- Добавить stalled diagnostic по возрасту heartbeat и состоянию процесса без
  автоматического завершения живого child после одного пропуска.
- Сохранить существующие terminal outcomes, raw evidence и совместимость
  single-card/package records.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-delivery-runner`: runner принимает и публикует bounded lifecycle
  progress, heartbeat и stalled diagnostics.
- `changerail-contracts`: delivery-run и plan-status schemas закрепляют
  безопасный progress contract.
- `changerail-delivery-observability`: поддерживаемые status surfaces показывают
  live progress без чтения raw agent logs.

## Impact

- `bin/changerail-delivery-runner`
- lifecycle skills и command wrappers, которые объявляют major transitions
- `schemas/changerail-delivery-run.schema.json`
- `schemas/changerail-delivery-plan-status.schema.json`
- focused runner/status smokes и operator docs
