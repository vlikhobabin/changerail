## Why

После двух NO-GO ChangeRail останавливает доставку, даже если оператор отдельно
разрешает последнее ограниченное исправление. Ручной обход лимита разрушает учёт;
нужен проверяемый одноразовый переход, сохраняющий историю и независимое ревью.

## What Changes

- Обычный лимит остаётся 2. Единственное доверенное операторское разрешение
  предоставляет один дополнительный repair и review №3 на корневую delivery
  lineage. Профиль `max_review_cycles` по-прежнему принимает только 2.
- Вводятся конкретный proposal, внешняя по отношению к worker граница одобрения,
  неизменяемые receipts и атомарное резервирование единственного attempt.
  JSON в workspace, SHA-256 и переменная окружения сами по себе не дают authority.
- Единая политика allowance используется review, repair, recovery, final floor
  и installed transition. Повтор и crash продолжают то же резервирование.
- Определяются `paused`, `canceled`, `exhausted`, `infrastructure-blocked` и
  конечная политика технического continuation. Третий NO-GO или новый
  существенный repair после review №3 завершают попытку.
- Поддерживается явный переход известных installed predecessors с двумя NO-GO;
  обычный install, plan restoration и runtime-repair не выдают исключение.
- Обновляются контракты, role skills и runbooks; синтетические проверки покрывают
  полномочия, учёт, гонки, прерывания, обновление и обычные final/publication gates.

## Capabilities

### New Capabilities

Нет: это ограниченное расширение существующей native delivery.

### Modified Capabilities

- `native-delivery`: default 2, однократное operator +1, внешняя граница доверия,
  учёт reservation и конечные переходы всей lineage.

## Impact

Владелец — только ChangeRail. Затрагиваются `scripts/changerail/`, schemas и
skills в `tools/changerail/`, адресные тесты, distribution selection и общая
документация. Нужен небольшой Linux authority broker с защищённым состоянием
вне worker workspace и клиентом runner; он не является планировщиком задач.
Используются Unix sockets, peer credentials и SQLite из стандартной библиотеки,
без облачного сервиса и новых Python crypto dependencies.

Для использования исключения потребуется отдельно настроенная доверенная
операторская среда: worker не должен владеть broker, его конфигурацией или ledger.
По умолчанию отсутствие такой среды сохраняет лимит 2. Установка релиза не
создаёт пользователей ОС, не запускает сервис и не даёт дополнительных прав.

Новый runtime меняет frozen identity; совместимость требует отдельного receipt.
Продукт qa-mcp, его runs, credentials и release остаются вне scope. Этот change
планирует механизм, но не разрешает реальное исключение конкретному потребителю.
