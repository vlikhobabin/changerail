## Why

Модельная сессия может завершиться техническим отказом до начала следующей группы
после уже сохранённых checkpoints и evidence. Сейчас ChangeRail не может продолжить
такой run без переписывания identity или запуска дубликата.

## What Changes

- Добавляется узкий late-stage recovery только для доказанного технического отказа
  до начала незавершённой группы.
- Старый run, checkpoints, evidence, review accounting и payload остаются exact;
  successor получает `recovery_of` и запускает только следующую группу.
- Разрешается ограниченный fallback model route без нового review allowance.
- Не поддерживаются product failure, operator stop, живой процесс, неоднозначный
  launch, payload drift, verification/review/archive стадии и новый semantic repair.

## Capabilities

### Modified Capabilities

- `native-delivery`: добавляется позднее техническое продолжение с immutable receipt.

## Impact

Затрагиваются runner recovery policy, session receipts, model adapter, tests и
операторская документация. Реальные consumer runs не изменяются в рамках change;
текущий остановленный run используется только как сохранённый диагностический
пример. Recovery не обходит frozen identity и не добавляет review allowance.
