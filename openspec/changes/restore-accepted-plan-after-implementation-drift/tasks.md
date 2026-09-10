## 1. reproduce-recovery-boundaries

- [ ] 1.1 Перенести обезличенное воспроизведение обоих отказов в test_openspec_recovery_boundaries.py: реальные admission, require_plan, import_accepted, recovery_source и payload fingerprints; без подмены проверяемых gates.
- [ ] 1.2 Дополнить stopped fixture настоящими completed groups и focused/observed evidence, failed pre-import child без native-plan и проверкой неизменности всех исходных файлов.
- [ ] 1.3 Создать воспроизводимую installed predecessor fixture прежнего identity shape из generic runtime archive/lock, без qa-mcp данных; зафиксировать границу совместимости C4.

## 2. prepare-exact-restoration

- [ ] 2.1 Реализовать ограниченный модуль/schema proposal и диагностику Next drift с проверкой принятого Git blob, полного card contract, normalized artifacts, exact payload и ancestry origin.
- [ ] 2.2 Добавить CLI prepare/dry-run, snapshots новых admissions, явный target/predecessor и project lock; проверить C1 на разных newline/mode и дубликатах секций.
- [ ] 2.3 Добавить отрицательные тесты подмены источника, Scope/Acceptance/artifacts, product/profile/launcher drift, чужих/cyclic/missing ancestors и неподдерживаемых стадий; доказать отказ до записи.

## 3. apply-append-only-transition

- [ ] 3.1 Реализовать proposal-bound authority, durable intent, атомарное восстановление только Next и отдельные applied/effective-manifest receipts; ни один старый run не дополнять и не перезаписывать.
- [ ] 3.2 Реализовать reconcile для before/after состояний, repeat без двойной мутации и блокирование обычного run при незавершённом intent.
- [ ] 3.3 Проверить C2: competing writer, drift после prepare, подмена proposal, прерывания на каждой границе записи, third-state отказ и полное сравнение history inventory до/после.

## 4. bridge-installed-execution

- [ ] 4.1 Реализовать reviewed compatibility descriptor старых schemas/identity shapes; доказать пропущенные tool bytes frozen distribution lock/archive, а не текущим checkout.
- [ ] 4.2 Добавить отдельный runtime-transition proposal и integration с distribution transaction для точной lineage и target archive; сохранить существующий запрет на read-only runs и immutable project settings.
- [ ] 4.3 Проверить C4 на installed-copy predecessor с completed groups/evidence и failed child, неизвестной/неполной identity, изменённых archive/profile/launcher, несвязанном frozen run и history-retention обходе.
- [ ] 4.4 Проверить прерывания между runtime install и card restore: только доказанные old/target и before/after состояния доходят до applied; до этого successor не запускается.

## 5. continue-with-fresh-evidence

- [ ] 5.1 Интегрировать effective manifest и consumption receipt в doctor/resume с точным predecessor под одной lock; новый run получает план из проверенного origin, сохраняя failed child в ancestry.
- [ ] 5.2 Сохранять complete groups только по semantic identity и events; строить explicit invalidation/refresh context и получать свежие focused/observed proofs до handoff.
- [ ] 5.3 Проверить C3 настоящими gates с контролируемыми сессиями: complete events не повторяются; finalize/sync/review/archive/final/publication проходят только после свежих proofs; fake success handoff отклоняется.
- [ ] 5.4 Проверить review budgets 0/1/2, отменённый оператором floor, interrupted attempts, pending provisional review/archive/publication и unrelated dangling board reference; дополнительных review и обхода блокеров нет.
- [ ] 5.5 Выполнить synthetic end-to-end через публичный CLI от installed predecessor до штатного продолжения и локальной fixture publication; никакой внешней сети, model CLI или реального потребителя.

## 6. document-and-verify-contract

- [ ] 6.1 Обновить native implementing skill: frozen Next, допустимые Result/Log по стадии, успешный exit handoff как условие передачи; проверить сценарий отказа без ложного completion.
- [ ] 6.2 Документировать prepare/apply/reconcile/resume, installed transition, ограничения стадий и отличие от runtime-repair в docs/operations.md и docs/runtime-repair.md; не предлагать пересэмплирование старого manifest.
- [ ] 6.3 Выполнить адресные recovery/native integration/execution/evidence/accounting и installer transaction регрессии, Ruff и git diff --check; связать результаты с C1–C4. Полный suite оставить CI, остановленные оператором наборы не перезапускать.
- [ ] 6.4 Выполнить strict validation change и canonical specs, проверить публичную выборку на отсутствие потребительских profiles/logs/data; delivery review/archive/publication оставить outer runner.
