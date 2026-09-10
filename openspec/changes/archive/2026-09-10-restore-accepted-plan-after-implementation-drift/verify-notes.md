# Проверка восстановления принятого плана

## Способ выполнения

Изменение самого ChangeRail выполнено в основном checkout под управлением
операторской сессии с ограниченным делегированием. Native runner над меняющимся
собственным исходником не запускался. Ниже приведены результаты разработки
инструмента; они не являются fabricated run/evidence receipts продуктовой доставки.
Реальные потребительские runs не продолжались и не изменялись этой работой.

Исходный RED для отсутствовавшего restoration API получен тестами core и installed
bridge. Retained installed RED: `/tmp/changerail-installed-restoration-red.txt`
(ImportError, отсутствовавший модуль); runner RED:
`.runtime/plan-restoration-development/runner-red.log`. Дополнительный regression
подмены installed effective manifest дал `DID NOT RAISE` при воспроизведении старого
пропущенного guard в памяти; новый guard требует точного authorized projection.
Эти локальные logs не входят в Git и не нужны для clean-clone воспроизведения.

## Адресные результаты

Команды запускаются из корня через `.venv/bin/python -m pytest -q`.

| Покрытие | Test targets | Результат / retained output |
| --- | --- | --- |
| Native admission/archive, frozen execution, recovery boundaries, Python repair | `test_native_openspec_integration.py`, `test_native_execution_contract.py`, `test_openspec_recovery_boundaries.py`, `test_runtime_repair.py` в `tools/changerail/tests/` | 74 passed, 4 failed из-за устаревших test doubles без `required_run_id`; `native-regressions.log`. Все 4 исправлены и адресно повторены: 4 passed, `native-regressions-fixed.log`. |
| Exact predecessor, failed child, complete groups, fresh focused evidence, interrupted/late stage отказ, ancestry и dangling board | `tools/changerail/tests/test_plan_restore_runner.py` | 6 passed; `runner-complete.log`. |
| Два противоположных plan/payload отказа, writer lock, восстановление; evidence dependencies и observed handoff/review/final gates | `test_openspec_recovery_boundaries.py::test_plan_drift_and_manual_restore_form_two_distinct_recovery_failures`, `test_evidence_dependencies.py`, `test_local_changerail_observed_proof.py::test_observed_proof_review_and_final_gates`, `test_local_changerail_observed_proof.py::test_observed_proof_handoff_coverage` | 25 passed; `proof-regressions.log`. |
| Installed bridge, archive/lock/profile/launcher/identity, read-only и interrupted install | `test_installed_restoration.py` и distribution regressions | 28 passed; `/tmp/changerail-installed-restoration-green.txt`. |

Относительные имена logs в таблице находятся в
`.runtime/plan-restoration-development/`. Первые тесты runner ограниченно подменяют
admission environment и observed-contract orchestration; их результат сам по себе
не доказывает end-to-end. Реальные proof gates проверяются отдельно и сквозным тестом.

## Связь с acceptance

- C1: `test_plan_restoration.py` проверяет exact Next, полный frozen contract,
  artifacts, source/hash, snapshots, разные newline и mode, hostile drift.
  `test_openspec_recovery_boundaries.py` сохраняет исходное воспроизведение обоих
  отказов с реальными admission/plan/import/payload gates и позитивным переходом.
- C2: те же core tests и `test_installed_restoration.py` проверяют authority,
  writer lock, before/after/third state, repeat/reconcile, immutable history
  inventory и заранее вычисленный installed effective manifest.
- C3: `test_plan_restore_runner.py` проверяет failed ancestry, complete groups,
  single successor, stale/new evidence и независимые от restoration отказы;
  обычные observed-proof регрессии проверяют gates. Core сохраняет расход 0/1/2
  review; исчерпанный бюджет не даёт новой попытки.
- C4: `test_installed_restoration.py` использует настоящий archive/install/lock
  с воспроизведённой прежней identity shape. Это generic fixture прежнего формата,
  а не утверждение исполнения бинарных байтов старого выпуска или доставки
  конкретного потребителя. Полное продолжение покрывает `test_plan_restore_e2e.py`.

## Сквозное продолжение

`.venv/bin/python -m pytest -q tools/changerail/tests/test_plan_restore_e2e.py`:
**1 passed in 147.72s**, `/tmp/changerail-plan-e2e-green.txt`.

Синтетический installed predecessor имеет настоящие completed events и
focused/observed evidence, затем Next drift и failed child без native-plan.
Через публичный dispatch CLI выполняются prepare/apply/resume. Для synthetic source candidate добавлен явный test-only compatibility descriptor;
production descriptor не допускает эти произвольные fixture bytes. Из
исполнительных границ подменён model launcher: контролируемые сессии выполняют настоящий
finalize/sync, evidence, handoff и verdict validation. Runner сам вызывает stock
archive, archive-refresh, продолжение того же review thread, final floor и Git
commit/push в временный bare remote. Проверены `publication.state=pushed`, clean
tree, совпадение remote SHA, карточка в `4.done`, `verification.ok=true`, расход
ровно одного независимого review и неизменность обеих исходных run directories.
Завершённые task groups не запускались повторно. Внешней сети и model CLI нет.

Отказы при подготовке fixture (неполный profile и отсутствие каталога `4.done`)
исправлены в fixture; production gates не подменялись и не ослаблялись.

## Оставшиеся gates

Независимое review цикла 1 выполнено; все три finding исправлены, адресные
регрессии и актуальный E2E прошли. Strict validation change, canonical spec и
workspace: 2 passed, 0 failed (`openspec-validation.log`). Ruff и diff-check
прошли. Public index snapshot: 108 files, 0 findings (`public-index.json`);
reachable history scan: 0 findings (`public-history.json`). Runtime archive и
full exact-commit CI проверяются отдельно перед tag; результат публикуется
в GitHub release notes, не подменяется локальными адресными проверками.

## Независимое ревью и исправления

Цикл 1 — NO-GO: reviewer без участия в реализации воспроизвёл тупик при
прерывании создания successor и допуск самосогласованного неизвестного runtime
fork; обнаружил обход pending guard другими командами записи. Находки сохранены
в `.runtime/plan-restoration-development/review-cycle-1.md`.

Для общего writer guard добавлен `test_plan_restore_writer_guard.py`: RED —
3 failed (`writer-guard-red.log`), GREEN — 3 passed (`writer-guard-green.log`).
После исправления CLI mutation dispatch и project/installer/source lock проходят
40 адресных проверок: `test_distribution.py`, `test_source_binding.py`,
`test_plan_restore_writer_guard.py`; `writer-distribution-regressions.log`.
Apply имеет явное внутреннее исключение для согласования того же pending intent.
Создание successor исправлено через staging, durable intent и atomic directory
publication до consumption. Partial successor больше нельзя consume; повтор
predecessor заканчивает только тот же доказанный незапущенный successor.
`test_plan_restore_creation.py` проверяет прерывания подготовки, intent, rename,
consumption, manifest index, публикации JSON и third-state отказ. Core reviewer-fix
запуски: 10 creation regressions, ещё 2 staging/index и 2 atomic-record checks,
3 проверки partial/consume/native resume и 1 обновлённый single-successor test.
Исходный orphan RED подтверждён. Результаты retained в выводе отдельных pytest tool invocations текущей сессии;
clean-clone команды указаны именем тестового модуля выше.
Installed compatibility теперь закрепляет полный payload/archive hash, critical
runtime hashes, identity shape и явную политику checkpoint/evidence/review.
Generic source fixtures получают разрешение только через test-only descriptor.
Отдельная регрессия проверяет production descriptor по точным исходным manifests
candidate.5/rc.1/rc.2 и строит/устанавливает настоящий rc.2 из публичного Git tag.
CI получает полную историю с тегами для исполнения этой проверки.
Самосогласованный неизвестный fork воспроизведён в RED (`DID NOT RAISE`):
`/tmp/changerail-compatibility-review1-red.txt`. GREEN: 20 passed in 8.35s, `/tmp/changerail-compatibility-review1-green.txt`.
Актуальный E2E после всех трёх исправлений: 1 passed in 145.54s,
`/tmp/changerail-plan-e2e-review1-green.txt`.


## Archive

Canonical delta синхронизирован и прошёл strict validation до archive. Stock
`./bin/openspec archive restore-accepted-plan-after-implementation-drift --skip-specs --yes`
переместил change в `2026-09-10-restore-accepted-plan-after-implementation-drift`.
`--skip-specs` исключает повторное добавление уже синхронизированных требований.
После archive `./bin/openspec validate --all --strict --no-interactive`: 1 passed,
0 failed; `.runtime/plan-restoration-development/archive.log`. Все 22 задачи
завершены. Frozen contract карточки совпал с исходным admission receipt: изменены
только Status/Result/Log и колонка доски.
