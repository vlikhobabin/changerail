# Обновление рабочего checkout

Этот runbook относится к Git checkout самого ChangeRail. Для runtime-копии
используйте [distribution install/history/adoption](../DISTRIBUTION.md), для
ссылочного consumer — [attach/detach](shared-source.md). Не запускайте installer
поверх исходного Git checkout с локальными правками ради обхода Git-конфликтов.
Обновление checkout не переключает consumer bindings и immutable engine.

## Инвентаризация и backup

Выберите опубликованный tag и скачайте assets по [quickstart](quickstart.md).
Проверьте SHA256SUMS, provenance, peeled tag и успешный CI точного release commit.
Примеры используют произвольные каталоги:

```sh
chrl_work=/srv/tools/changerail
chrl_backup=/srv/private-backups/changerail-before-update
chrl_tag=v2.0.0-rc.4
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
явного project overlay. Выполните `"$chrl_work/bin/chrl" wiring`; зависимости OpenSpec
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
