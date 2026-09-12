# Проверка неуспешного закрытия

Это план проверок, не выполненное evidence. Сценарии используют только временные
generic проекты, локальный Git и синтетические verdict; реальные consumer logs
не копируются. Результаты сохраняются под уникальным run path в
`.runtime/verification/close-exhausted-native-delivery/`: exact command, exit,
payload identity, pytest output и наблюдаемые before/after значения.

## C1: явное закрытие

- Precondition: synthetic native ancestry содержит первый NO-GO у предка,
  второй у выбранного run; живых writers и поздних intents нет.
- Action: prepare, проверить proposed before/after, apply с точным digest.
- Expected: карточка в 5.canceled с неуспешным результатом, frozen sections
  неизменны, расход review=2; review/archive/commit/push subprocess не вызваны.
- Negative: один review, GO, pending review/verification, descendant, worker
  role, чужая lineage, живой lock/orphan writer, recovery/archive/final/publish
  intent; каждый отказ оставляет board и payload неизменными.
- Artifact: closure.json и output focused tests `test_native_closure.py`.

## C2: история и snapshot

- Precondition: после последнего NO-GO добавлен ремонт: binary untracked,
  tracked delta, удаление, executable mode и symlink; исходная история hashed.
- Action: восстановить snapshot в отдельном временном дереве, сравнить path
  set/types/bytes/modes; затем применить закрытие. Повторить со сбоями после
  intent, после переноса карточки и посреди изменения ссылок.
- Expected: snapshot полный, reviewed/current различимы, вся прежняя история
  побайтно сохранена; repeat завершает ровно один intent, расход не меняется.
- Negative: stale HEAD/payload, непустой index и конфликт чужой правки;
  refusal до мутации либо fail-closed reconcile без перезаписи чужих данных.
- Artifact: snapshot.json, before/after inventories и pytest output.

## C3: терминальность и новый план

- Precondition: completed closure и отдельно interrupted closure intent.
- Action: вызвать resume, run recovery, handoff/review/publish и restoration
  для выбранного run/предков; проверить status, board guard и разрешение ссылок.
  Создать связанную backlog-карточку без native acceptance.
- Expected: ни один writer не стартует; status показывает неуспешное закрытие;
  завершённый transition освобождает active column, незавершённый блокирует run.
  Преемник остаётся backlog, dirty payload явно указан, старый allowance=2.
- Artifact: terminal.json и CLI/pytest output.

## C4: installed rc.3

- Precondition: generic copy-install проект с публичной rc.3 provenance и
  synthetic exhausted native history; проверяемый новый комплект отдельно.
- Action: выполнить реальный CLI нового комплекта с --project, prepare/apply,
  затем отрицательные resume/restoration. Проверить вариант retained read-only
  history, неизвестный формат и подменённый lock/provenance.
- Expected: только доказанный rc.3 predecessor закрыт; installed runtime,
  lock/launcher/profile и старые runs неизменны; права исполнения не расширены.
  Тесты не требуют сети, реального оператора/provider config или live rollout.
- Artifact: installed.json, before/after inventory и subprocess output.

## Команды после реализации

- `python3 -m pytest -q tools/changerail/tests/test_native_closure.py`
- `python3 -m pytest -q tools/changerail/tests/test_native_closure_installed.py tools/changerail/tests/test_native_execution_contract.py`
- `python3 -m ruff check scripts/changerail/native_closure.py tools/changerail/tests/test_native_closure.py tools/changerail/tests/test_native_closure_installed.py` и затронутые существующие Python files.
- `./bin/openspec validate close-exhausted-native-delivery --strict --no-interactive`
- `./bin/openspec validate --specs --strict --no-interactive`
- `git diff --check`

Полный suite принадлежит CI/штатному финальному gate; остановленный оператором
набор автоматически не перезапускается. Final stage C4 требует свежего evidence
от финального payload, ранние успехи не заменяют эту проверку.
