## 1. allowance-model

- [x] 1.1 Воспроизвести остановку после двух автономных review: общий остаток, наследованный расход, терминальный NO-GO без права на новый review.
- [x] 1.2 Реализовать `review_allowance.py`: единый расчёт `2 + operator_granted_slots - spent_reviews`, чтение неизменяемых записей, отрицательный остаток как ошибка.
- [x] 1.3 Реализовать двухфазный `review-allow`: preview с digest, `--authorize` с атомарной append-only записью, идемпотентный повтор, отказ при устаревшем digest.
- [x] 1.4 Реализовать отказ worker-контекста, не включая shared-use lease `CHRL_ENGINE_USE_FD` обычного launcher'а.
- [x] 1.5 Сохранить focused-регрессии модуля allowance и зафиксировать receipts.

## 2. runner-integration

- [x] 2.1 Подключить `review_slot` к `build_review_context` и `run_review`, сохранив lineage ordinal и общий слот provisional/final.
- [x] 2.2 Подключить `recovery_authorization` к `doctor` и к переходу recovery; связывать слот с единственным successor до writer.
- [x] 2.3 Добавить read-only статус allowance в `native_workflow.status` и защиту retained read-only истории.
- [x] 2.4 Сохранить жёсткие гейты: scope, frozen identity, proofs, handoff, archive, final floor и publication.
- [x] 2.5 Сохранить focused/integration/recovery регрессии и подтвердить отсутствие второго child при частичном claim.

## 3. contract-and-docs

- [ ] 3.1 Синхронизировать каноническую спеку `openspec/specs/native-delivery/spec.md` с фактическим контрактом allowance.
- [ ] 3.2 Обновить `openspec/config.yaml`: автономные два review и операторский +1 при исчерпании вместо «at most two independent reviews».
- [ ] 3.3 Обновить публикуемый `tools/changerail/README.md`, чтобы установленный runtime не получал противоречивый контракт.
- [ ] 3.4 Зафиксировать русскую инструкцию оператора и навыки deliver/review: worker не выдаёт разрешение сам.

## 4. retired-change-and-verification

- [ ] 4.1 Архивировать отменённый change `allow-single-operator-review-extension` как историю.
- [ ] 4.2 Исправить недостоверный раздел `Result` в карточке `5.canceled`: заявленные broker/ledger в дереве отсутствуют; указать, что дизайн заменён этим change'ем.
- [ ] 4.3 Прогнать полный набор `./bin/test-changerail` и Ruff на точном payload.
- [ ] 4.4 Передать свежие proofs внешнему независимому review и пройти обычные финальные гейты.
