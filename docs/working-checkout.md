# Обновление рабочего checkout

Этот runbook относится к Git checkout самого ChangeRail. Для runtime-копии
используйте [distribution install/history/adoption](../DISTRIBUTION.md), для
ссылочного consumer — [attach/detach](shared-source.md). Не запускайте installer
поверх исходного Git checkout с локальными правками ради обхода Git-конфликтов.
Обновление checkout не переключает consumer bindings и immutable engine.

## Executor из релиза: два каталога

Этот режим использует dev-проект и отдельный полный Git checkout опубликованного
релиза. Тесты и документация, не вошедшие в runtime-архив, допустимы в release
checkout; незаявленные исполняемые файлы в import/runtime roots отклоняются.
Receipt рядом с checkout фиксирует tag object, commit, tree, runtime inventory,
Python/Node и закрытый dependency inventory. Проверка не устанавливает пакеты.

Выпуск с новым coordinator/launcher готовят по [release runbook](releasing.md),
проверяя CI точного публикуемого commit; native или snapshot delivery для этого
не требуется. После публикации оператор скачивает runtime-архив, SHA256SUMS
и provenance, проверяет точный tag/commit/tree и CI по quickstart.
Существующий старый checkout сначала обновляют по оставшейся части этого runbook
до этого implementation release, сохраняя локальный backup и историю. Старый
релиз без нового кода нельзя объявить готовым executor одним acceptance receipt.
Ни публикация, ни конкретная локальная миграция этими инструкциями не выполнены.

Далее из отдельной операторской оболочки выберите свои пути:

```sh
chrl_coordinator=/srv/tools/changerail-dev
chrl_dev=/srv/projects/example-dev
chrl_release=/srv/tools/changerail-release
chrl_assets=/srv/downloads/changerail-release
chrl_tag=v2.0.0-rc.5
chrl_update=/srv/private-receipts/changerail-first-acceptance
chrl_archive="$chrl_assets/changerail-2.0.0-rc.5-runtime.tar.gz"
chrl_provenance="$chrl_assets/release-provenance.json"
chrl_node=$(command -v node)

"$chrl_coordinator/bin/chrl-dist" release-update prepare \
  --root "$chrl_release" --archive "$chrl_archive" --provenance "$chrl_provenance" \
  --tag "$chrl_tag" --proposal "$chrl_update" --node "$chrl_node" --bootstrap --dry-run
"$chrl_coordinator/bin/chrl-dist" release-update prepare \
  --root "$chrl_release" --archive "$chrl_archive" --provenance "$chrl_provenance" \
  --tag "$chrl_tag" --proposal "$chrl_update" --node "$chrl_node" --bootstrap
"$chrl_coordinator/bin/chrl-dist" release-update apply "$chrl_update"
```

Имя runtime-архива сверяют со скачанным provenance выбранного выпуска. Родитель proposal-каталога
должен существовать вне checkout на той же файловой системе, что и release,
для атомарной публикации staging. Preview создаёт временный закрытый каталог
в этом же parent; assets могут храниться на другой файловой системе.
Coordinator должен содержать новую реализацию и находиться вне обновляемого
target: apply/reconcile/provision-lease из самого target отклоняются.
Help и prepare допускаются из accepted executor без записи source bytecode.

Если apply сообщает необходимость provisioning, он оставляет maintenance marker.
Откройте `release-update provision-lease "$chrl_update"`: команда держит exclusive
lease, пока оператор в отдельной оболочке готовит `.venv` и pinned OpenSpec
`node_modules` выбранного release по объявленным версиям. Команда не запускает
installer автоматически. По завершении в оболочке lease введите `done`, затем
выполните `release-update reconcile "$chrl_update"`. После сбоя повторяют эту же
provision/reconcile последовательность с тем же proposal; marker вручную не удаляют.
Зависимости dev-проекта подготавливают отдельно. Полный test suite, модель и delivery
не являются скрытыми шагами обновления.

Updater использует пооперационный журнал source/index/HEAD: release-изменения
в protected `.changerail`, `.codex`, `.runtime`, `bin/codex` и `openspec` не
перезаписывают локальные entries, их отсутствие и соответствующие строки index.
Остальные source paths и detached HEAD обновляются по журналу; reconcile продолжает
точный незавершённый шаг. Это не `git switch` с последующим восстановлением history.
Ручной маршрут ниже относится к первому pre-feature обновлению и обычным checkout,
не заменяет maintenance protocol уже принятого executor.

Для binding нужны ignored/untracked `.changerail/engine-binding.json`,
`.changerail/chrl`, `.changerail/openspec` и `.runtime/changerail/`. Существующий
source-link предварительно отключают документированным detach; dev/bin не заменяют.
Generic consumer должен добавить в свой Git ignore как минимум:

```gitignore
.changerail/engine-binding.json
.changerail/.engine-binding.lock
.changerail/chrl
.changerail/openspec
.runtime/
```

Публичный ChangeRail `.gitignore` уже содержит эти локальные generated пути.
Сами launchers, абсолютные binding paths и пользовательские auth/config не коммитят.

Для начального проекта без binding пропустите `--previous-identity`; для snapshot
или прежнего release укажите точную текущую identity из проверенного binding/receipt.

```sh
chrl_previous_identity=REPLACE_WITH_VERIFIED_CURRENT_IDENTITY
"$chrl_coordinator/bin/chrl-dist" executor-bind prepare \
  --project "$chrl_dev" --executor "$chrl_release" \
  --previous-identity "$chrl_previous_identity" --dry-run
"$chrl_coordinator/bin/chrl-dist" executor-bind prepare \
  --project "$chrl_dev" --executor "$chrl_release" \
  --previous-identity "$chrl_previous_identity"
# Подставьте точный путь proposal.json из результата prepare.
chrl_binding_proposal=REPLACE_WITH_RETURNED_PROPOSAL_JSON
"$chrl_coordinator/bin/chrl-dist" executor-bind apply "$chrl_binding_proposal" --dry-run
"$chrl_coordinator/bin/chrl-dist" executor-bind apply "$chrl_binding_proposal"
"$chrl_dev/.changerail/chrl" --engine-root
"$chrl_dev/.changerail/openspec" --version
```

Миграция получает project delivery lock, затем binding lock, проверяет живые
процессы и незавершённую verification. Receipt хранит точные before/after bytes
binding/launchers и inventory всей сохранённой runtime-истории. Старые run.json,
review/evidence accounting, counters и профили не переписываются; successor не
создаётся. Завершённая история допускает выбор executor для будущих запусков.
Незавершённые, но остановленные runs сохраняются без новых прав исполнения:
при другой release identity обычный resume/frozen check отклоняет их.
Повторный apply завершённого proposal только проверяет уже применённое состояние:
новые history entries допустимы, но все исходные entries должны остаться точными.
Для прерванного перехода reconcile требует точного исходного inventory без добавлений.

После сбоя binding используйте `executor-bind reconcile "$chrl_binding_proposal"`;
он принимает только сохранённые before/after состояния. Возврат к snapshot — новый
`executor-bind prepare --kind snapshot --executor SAVED_SNAPSHOT` с identity текущего
release, затем apply. Слепое восстановление старого binding не является переходом. Такой возврат выбирает
snapshot для будущих запусков, не отменяет delivery, публикацию или сохранённую
history и не возвращает старому run право исполнения.

Guard новых generated launchers и новых внешних `bin/chrl`/`bin/openspec` проверяется
до перенаправления в v1 snapshot. После прерывания используйте только эти supported
пути и reconcile. Произвольный сохранённый старый бинарник, выпущенный до появления
этого protocol, не получает guard задним числом.

Для следующих выпусков повторяют проверку downloaded assets и `release-update
prepare/apply` с новым proposal, без `--bootstrap`. Git tag уже должен быть доступен
локально; updater не выполняет fetch. Accepted receipt публикуется только после
завершения source/dependency transition. `.changerail/chrl` сохраняет стабильный
путь executor и новые runs автоматически выбирают новый accepted release.
Профиль, defaults/auth, board и retained history остаются локальными; обновление
не расширяет review allowance и не восстанавливает право исполнения старых runs.

## Инвентаризация и backup

Выберите опубликованный tag и скачайте assets по [quickstart](quickstart.md).
Проверьте SHA256SUMS, provenance, peeled tag и успешный CI точного release commit.
Примеры используют произвольные каталоги:

```sh
chrl_work=/srv/tools/changerail
chrl_backup=/srv/private-backups/changerail-before-update
chrl_tag=v2.0.0-rc.5
umask 077
mkdir -p "$chrl_backup"
git -C "$chrl_work" status --short
git -C "$chrl_work" worktree list --porcelain
git -C "$chrl_work" rev-parse HEAD > "$chrl_backup/previous-head.txt"
git -C "$chrl_work" diff --binary > "$chrl_backup/unstaged.patch"
git -C "$chrl_work" diff --cached --binary > "$chrl_backup/staged.patch"
```

До первой замены исходников проверьте отсутствие runner и его дочерних процессов,
а также доступность delivery lock; не удаляйте lock. Сохраните полную копию
checkout, включая `.git`, ignored/untracked файлы, ACL/modes и сами ссылки без
разыменования, в закрытом каталоге вне checkout. Например, GNU tar:

```sh
tar --acls --xattrs -cpf "$chrl_backup/checkout.tar" -C "$chrl_work" .
sha256sum "$chrl_backup/checkout.tar" > "$chrl_backup/checkout.tar.sha256"
tar -df "$chrl_backup/checkout.tar" -C "$chrl_work"
```

Сверьте backup и составьте inventory типов, режимов, SHA-256 обычных файлов и
literal targets ссылок. Особо выделите `.changerail/`, настройки и credentials,
проектный launcher, `openspec/`, старые `run.json`, manifests, checkpoints,
evidence и review accounting. Не выводите credentials в отчёт. Проверьте,
что восстановление архива в отдельный закрытый каталог воспроизводит inventory.
Для связанного Git worktree сохраните также фактический common git dir;
копии одного файла `.git` недостаточно. Основной checkout может владеть другими
worktrees: изменение пути его `.git` требует `git worktree repair`.

Если board или другие заменяемые каталоги read-only, сохраните `getfacl -Rp`
и исходные special bits. Временно откройте запись только владельцу нужных
каталогов; после возврата overlay восстановите ACL и режимы из inventory.

## Переключение исходника

Предпочтительно обновить checkout на месте, сохранив его абсолютный путь.
Локальные изменения исходников сохраните в backup и именованном stash с untracked
файлами; ignored данные остаются на месте. Сохраните SHA stash, не используйте
`stash pop` после обновления: старые правки ядра могут нарушить точность выпуска.

```sh
git -C "$chrl_work" stash push --include-untracked -m "before release update"
# Если stash был создан, запишите его точный SHA отдельно.
git -C "$chrl_work" rev-parse refs/stash > "$chrl_backup/stash.txt"
git -C "$chrl_work" fetch origin --tags
git -C "$chrl_work" switch --detach "$chrl_tag"
```

Перед stash просмотрите untracked-выборку: там не должно оказаться секретов;
приватные файлы сохраняются только в закрытом backup и ignore. Если локальных
правок нет, пропустите stash и запись его SHA. До переключения отдельно проверьте пересечения ignored-файлов с release-путями:
Git может перезаписать ignored-файл. Сохраните конфликтующие entries и разрешите
каждый конфликт явно; не используйте force, reset или clean.

Из проверенного backup восстановите только отдельно перечисленные проектные
данные: профиль, настройки, launcher, board, историю OpenSpec. Runtime и его
receipts сохраняйте без изменения байтов и путей. Если новая версия содержит
другой board, сохраните его отдельно как исходник выпуска и верните точное старое
проектное дерево, включая отсутствие ранее удалённых файлов. Это осознанный
локальный overlay: Git HEAD равен release commit, но checkout не обязан быть чистым.
Локальные правки ядра и старые docs остаются в backup/stash для отдельного разбора.
Не записывайте private overlay в релизный commit.

Историческая board не становится исполняемой после обновления. Сохраните уже
имеющийся history manifest без правок. Если manifest отсутствует и старый board
должен остаться read-only, создайте отдельный локальный project-history manifest
из проверенного inventory по [миграционному контракту](migration.md#существующая-openspec-история-и-проектные-инструкции).
Добавление его пути в локальный профиль — явное изменение execution inputs;
сохраните предыдущий профиль и покажите этот diff в отчёте. Это не даёт права resume.
Не исправляйте хеши существующего manifest ради прохождения wiring.

## Проверка и повторное применение

Сверьте каждый файл и режим runtime-архива с рабочим checkout и manifest,
а tag/HEAD/tree — с provenance. Проверьте все остальные release-файлы за пределами
явного project overlay. Выполните `"$chrl_work/bin/chrl" --project "$chrl_work" wiring`; явный project
исключает выбор другого checkout по текущему каталогу. Зависимости OpenSpec
проверяются существующим wrapper, их установка — отдельное явное действие.
ChangeRail suite в consumers и при обычном обновлении runtime не запускается.

Сравните защищённые данные с исходным inventory: ни один старый run, receipt,
checkpoint или proof не должен измениться. Сверьте consumer source-link и targets
ссылок, а snapshots проверьте через `engine-snapshot-verify` без записи в них.
Запишите commit, asset hashes, backup/stash, overlay и результаты локально.
Совпадения строки версии недостаточно. Повторное применение того же выпуска
начинается с этой сверки и при полном совпадении ничего не заменяет.

## Восстановление

До новых доставок возврат исходников возможен через `git switch --detach` на
сохранённый previous HEAD после сохранения текущего overlay. Примените точный
stash через `git stash apply --index <saved-sha>` только к совпадающему исходному
состоянию; проверьте конфликты и inventory. Stash и backup не удаляйте.
При сложном конфликте восстановите полный архив в отдельный каталог и проверьте
его до возврата прежнего пути. Git metadata ссылается на абсолютные worktree paths:
не используйте восстановленную копию для записи в связанные worktrees.

После новых runs или изменения binding нельзя накрывать текущую `.runtime` старым
backup: сначала сохраните новые записи и разберите совместимость. Возврат исходника
не откатывает доставку, remote publication, engine binding или review accounting.
У self-host recovery нет универсального rollback; допустимые rebind и повторный
apply/reconcile описаны в [self-host runbook](self-host-recovery.md).
