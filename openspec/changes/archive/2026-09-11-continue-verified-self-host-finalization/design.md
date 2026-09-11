## Context
Первый self-host successor имеет завершённые группы и нулевой расход review, но пустой manifest после committed corrective payload. Его failed focused proof требует исправления test fixtures. Frozen engine нельзя править на месте.

## Goals / Non-Goals
Поддержать explicit rebind и новое receipt-based продолжение bound predecessor, а затем ordinary resume пустого точного payload. Не обходить reviews, не менять старые runs, не допускать неизвестную identity и не повторять groups.

## Decisions
- Operator запускает rebind из нового проверенного snapshot. Before identity обязательна; оба snapshot проверяются. Delivery lock и live-process check обязательны. Intent предшествует atomic replace binding; retry согласует тот же intent, не выдавая execution authority старому run.
- Bound predecessor допускается в том же project root только с совпадающими project execution inputs, кроме отдельно заменённого engine binding. Binding остаётся явной частью нового self-host proposal.
- Empty payload допускается при точном выборе retained self-host run и совпадении manifest/head/paths/fingerprints; обычные frozen execution и admission gates остаются обязательными.
- Test fixtures получают свой project root; interruption test синхронизируется с фактическим запуском команды, schema rejection проверяется по структурированному validator.
- Коррекция инфраструктуры выполняется управляющей сессией без второй активной delivery. История первого successor сохранена; следующий переход не повторяет apply исходного run.

## Risks / Trade-offs
Crash между binding replace и applied receipt требует retry по тому же request. Ни rebind, ни пустой payload не разрешают продолжение изменённого проекта без self-host receipt.
