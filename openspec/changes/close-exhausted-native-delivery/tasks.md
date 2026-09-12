## 1. closure-proposal-and-snapshot

- [ ] 1.1 Воспроизвести synthetic lineage с двумя NO-GO, включая наследованный расход review; зафиксировать исходный отказ закрытия как регрессию, а не production evidence.
- [ ] 1.2 Реализовать native-close-prepare: точный terminal predecessor, outer-session authority, lock/no-writer, ancestry и boundary проверки.
- [ ] 1.3 Сохранить proposal и полный snapshot текущего payload с отдельной reviewed identity; проверить round-trip binary/untracked/deleted/mode/symlink и отказ при непустом index.
- [ ] 1.4 Выполнить focused tests модуля closure; сохранить pytest output и observations для C1/C2.

## 2. terminal-transition

- [ ] 2.1 Реализовать native-close-apply по digest: revalidation, immutable intent, перемещение карточки и только допустимых живых ссылок, completion receipt.
- [ ] 2.2 Добавить idempotent repeat и fault injection после intent, перемещения и промежуточной правки ссылок; конфликт не перезаписывает чужие bytes.
- [ ] 2.3 Интегрировать closure checks по lineage во все execution/recovery entrypoints и status; сохранять accounting и frozen sections.
- [ ] 2.4 Проверить пустую активную колонку, остающийся dirty payload и отсутствие автоматического acceptance преемника; выполнить focused C1–C3 и сохранить evidence.

## 3. installed-compatibility-and-verification

- [ ] 3.1 Реализовать отдельный terminal-only rc.3 decoder/provenance gate и external CLI --project путь, не изменяя allowlist исполнения/restoration.
- [ ] 3.2 Добавить synthetic copy-install CLI test и отрицательные provenance/version/read-only/resume случаи; подтвердить неизменность installed runtime, lock, launcher, profile и всей старой истории.
- [ ] 3.3 Обновить русскую operations-инструкцию: prepare/apply/repeat, неуспешный результат, локальный snapshot, dirty paths, отдельное новое планирование; обновить distribution inventory при добавлении поставляемого модуля.
- [ ] 3.4 Выполнить сценарии verification/scenarios.md, strict OpenSpec, focused pytest, Ruff и diff-check; передать свежие proofs внешнему runner для независимого review и обычной финальной проверки.
