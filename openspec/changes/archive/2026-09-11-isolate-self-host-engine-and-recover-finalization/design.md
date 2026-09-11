## Context

Остановленный self-host run нельзя продолжать после drift собственных Python-файлов:
исходный runner обязан сохранять frozen identity. Требуется разделить ownership
замороженного engine и изменяемого checkout.

## Decisions

1. Engine snapshot материализуется в отдельном checkout и идентифицируется хэшем
   полного execution inventory; symlink или env path сами по себе authority не дают.
2. Prepare проверяет predecessor manifest, accepted plan, review accounting, отсутствие
   writer/live process и точный corrective diff; receipt append-only.
3. Apply под project lock атомарно создаёт единственный successor, наследует completed
   groups без replay и передаёт управление обычному finalize lifecycle.
4. Reconcile идемпотентно связывает тот же receipt и successor; второй writer, drift,
   crash boundary или повторный apply fail-closed.
5. Переход к сохранённому run и development attach выполняются только после полной
   проверки change и не входят в обычную установку runtime.

## Verification

Регрессии должны покрыть identity drift, symlink/foreign engine, profile/launcher drift,
race/crash, duplicate apply, live processes, unresolved verification, plan/payload drift,
review/final/archive/publication boundaries и synthetic full lifecycle до publish.

## Engine and project execution inputs

Snapshot создаётся из чистого committed distribution payload, исключает Git,
профили, журналы и зависимости. Manifest фиксирует все файлы, режимы и хэши;
read-only permissions защищают от случайной записи, повторная проверка inventory
обнаруживает изменение даже владельцем. Публикация каталога атомарна и не заменяет
существующий snapshot. Binding принадлежит локальному проекту и не публикуется.

Python запускается с `-P` и точным `PYTHONPATH` engine: текущий рабочий каталог
не может затенить пакет `scripts`. Runner читает schemas и skill инструкции из
snapshot. Проектный профиль, model launcher, adapters, Python executable и
локальная установленная OpenSpec dependency замораживаются отдельно. Продуктовые
`bin/chrl`, Python-модули и schemas разрешено менять как payload; вложенные вызовы
получают путь закреплённого engine. Ссылка `.changerail/engine` не authority.

## Relocated predecessor

При переносе разработки между checkout исходный run находится у прежнего
владельца. Prepare/apply удерживают оба delivery lock в стабильном порядке,
проверяют terminal receipts и живые процессы Linux. Receipt фиксирует оба пути,
Git lineage, полный inventory истории, принятый план, accounting и точный
корректирующий diff. Хэшей старого manifest недостаточно для реконструкции:
нужны соответствующие им исходные bytes из сохранённого snapshot или Git.

Резервирование successor также записывается у origin вне старого run, чтобы
другая копия checkout не создала второго writer. Локальная копия predecessor
публикуется атомарно и сохраняет исходные bytes; обычные ancestry readers
продолжают использовать относительные пути. Старое evidence остаётся историей.

## Current delivery ownership

Активная карточка technical recovery сохраняет своё место и accepted plan.
Инфраструктурное исправление self-host выполняется отдельно в checkout разработки;
оно не записывает checkpoints или review receipts от имени остановленного run.
Вторая активная delivery карточка не создаётся. После проверки нового контракта
допускается explicit переход владельца к одному successor, начинающему finalize.
