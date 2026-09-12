## 1. reproduce-and-model

- [ ] 1.1 Добавить синтетическую регрессию остановки после двух NO-GO и отсутствие supported extension в `tools/changerail/tests/test_local_changerail_delivery.py`; сохранить RED evidence в `.runtime/review-extension-development/` без consumer данных.
- [ ] 1.2 Зафиксировать fixtures с exact root/predecessor/accepted plan и двумя verdict; проверить прежний default 2 и неизменность accounting для обычных runs.
- [ ] 1.3 Описать и валидировать schemas proposal/grant/reservation/transition с bindings C1–C4; отвергать неизвестные поля authority, отрицательные counters, duplicate IDs и scope expansion.

## 2. protect-operator-authority

- [ ] 2.1 Реализовать ограниченный Linux broker и operator CLI: защищённый host config, project/root registry, Unix peer credentials, раздельные operator/coordinator endpoints и отсутствие worker approve.
- [ ] 2.2 Реализовать SQLite grant/event ledger с unique project/root grant, атомарными переходами, immutable audit и fail-closed поведением при потере ledger/identity; profile и workspace receipts не должны подменять authoritative state.
- [ ] 2.3 Добавить coordinator client и проверку защищённого execution contour/host launcher; model worker должен иметь другой principal и не наследовать authority credentials. Same-UID bypass сохраняет default 2 и отказывает extension.
- [ ] 2.4 Доказать C1 реальным Linux multi-UID subprocess test: worker и coordinator не вызывают approve, worker не пишет host config/state и не impersonates coordinator; operator одобряет только exact proposal. Настроить отдельный CI job; отсутствие OS-возможностей не считать pass.

## 3. reserve-one-attempt

- [ ] 3.1 Реализовать `review_allowance.py` и подключить его к review/NO-GO/semantic repair/final-floor/recovery/installed входам; сохранить публичное наблюдение `review_budget_usage` и default profile limit 2.
- [ ] 3.2 Реализовать prepare/dry-run/apply с exact proposal и внешним grant: stale/foreign/worker-issued request отклоняется до writer; runtime, план, findings и repair allowlist проверяются повторно под lock.
- [ ] 3.3 До repair writer резервировать один постоянный attempt №3, создавать successor через durable intent/staging/atomic publication и подтверждать broker binding без изменения старых runs.
- [ ] 3.4 Добавить C2 race/crash/replay tests до/после reserve, между broker и local receipt, при публикации successor и разрыве соединения; повтор создаёт только тот же attempt, живой/неизвестный worker блокирует новый launch.
- [ ] 3.5 Проверить registry alias/root binding: rename, child, reinstall и local receipt rollback не создают нового grant; missing history/broker не дают ordinary fallback. Сравнить хеши и состав всех predecessor directories.

## 4. finish-or-stop

- [ ] 4.1 Реализовать finding-bound handoff перед review №3: reproduction/cause/fix/regression/fresh evidence для каждого finding, mechanical scope check и независимый verdict на актуальный payload.
- [ ] 4.2 Подключить GO №3 к прежним archive/final/publication gates без нового authority; NO-GO №3, review №4 и новый substantial final repair переводят lineage в exhausted.
- [ ] 4.3 Реализовать operator pause/unpause/cancel с проверкой перед writer/stage, сохранением фактических effects и IDs; canceled/exhausted терминальны, operator_interrupt не получает новый recovery path.
- [ ] 4.4 Ограничить infrastructure continuation одним восстановлением на весь extension attempt с тем же session/check ID; assertion failure, ambiguous launch, повторный сбой и отсутствие identity не запускают новый review и дают infrastructure-blocked.
- [ ] 4.5 Добавить C3/C4 regression matrix: pause до reserve и во время stage, cancel, stale proof, GO/NO-GO №3, failed final floor, штатный archive refresh, repeated CLI и technical budget shared across phases.

## 5. bridge-installed-runtime

- [ ] 5.1 Добавить exact rc.2/rc.3 compatibility descriptors и новый review-extension installed transition с target archive, frozen lock, неизменными project profile/launcher/adapters и явной target identity защищённого host envelope.
- [ ] 5.2 Связать installation intent с тем же grant/reservation, блокировать другие writers и обычный installer до reconcile; не расширять eligibility plan restoration/runtime-repair и не дописывать старые receipts.
- [ ] 5.3 Доказать C4 synthetic installed end-to-end от двух NO-GO через trusted approval, reserve, один repair и GO №3 до stock archive/final/локального bare push; старые файлы побайтно неизменны, четвёртый review невозможен.
- [ ] 5.4 Добавить negative E2E: unknown payload, bad archive, altered profile/launcher, same-UID contour, read-only history, operator stop, unsupported floor, третье состояние interrupted install и technical retry exhaustion.

## 6. document-and-verify

- [ ] 6.1 Обновить общие `AGENTS.md`, `openspec/config.yaml`, README, `docs/operations.md`, `docs/runtime-repair.md`, DISTRIBUTION и затронутые skills: default 2, единственное +1, hard ceiling 3, trusted setup, CLI, статусы и отдельные publication/runtime полномочия.
- [ ] 6.2 Включить broker/client/schemas и entrypoint в distribution ownership/allowlist; проверить build/verify/install/идемпотентность и отсутствие host settings, ledger, credentials и consumer data в архиве. Installer не создаёт OS identities и не запускает broker.
- [ ] 6.3 Выполнить адресные pytest для C1–C4, включая реальные Linux authority tests и E2E; сохранить команды, exit codes, hash proofs и ограничения в `verify-notes.md`. Выполнить Ruff и `git diff --check`; полный ChangeRail suite принадлежит CI, остановленный оператором набор не перезапускать.
- [ ] 6.4 Проверить change strict validation, доказательства каждого acceptance ID и согласованность delta spec перед handoff. Оставить native runner штатные independent review, sync/archive и final gates; не объявлять delivery выполненной по одним зелёным тестам.

<!-- Планируемые проверки реализации: python3 -m pytest -q по затронутым
tools/changerail/tests/test_local_changerail_delivery.py,
test_native_openspec_integration.py, test_openspec_recovery_boundaries.py,
test_native_execution_contract.py, test_runtime_repair.py, test_distribution.py
и новому Linux authority regression module; python3 -m ruff check scripts
tools/changerail/tests distribution.py; git diff --check.
Этот список не является выполненным evidence и не запускается при планировании. -->
