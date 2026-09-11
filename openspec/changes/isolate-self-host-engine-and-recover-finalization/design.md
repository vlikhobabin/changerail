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
