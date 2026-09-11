# Выпуск ChangeRail

Команды выполняются из корня основного checkout ChangeRail. Публикация тега
и GitHub Release — отдельные действия после проверки результата; они требуют
решения владельца выпуска. Уже опубликованные теги и assets не заменяют:
исправление получает новую версию. Нужны Git, Python, GitHub CLI (`gh`) с
доступом к репозиторию и зависимости разработки из CONTRIBUTING.

## 1. Состав и версия

Обновите согласованно `pyproject.toml`, `uv.lock`, `distribution.json`, README,
runtime README/ORIGIN, CHANGELOG и `docs/releases/<version>.md`. Для примера
`2.0.0-rc.4` Python metadata имеет форму `2.0.0rc4`. Исторический
`distribution.json.provenance.upstream_commit` не заменяют самоссылкой на
будущий commit; точное происхождение записывают отдельным release asset.

Проверьте совместимость frozen runs. Даже правка agent skill меняет execution
identity; изменения схем, skills, profile и launcher не покрывает Python repair.
Описание выпуска должно отражать это ограничение.

Сохраните пользовательские изменения и локальные настройки. В Git и runtime
архив не входят `.runtime/`, `internal/`, credentials, consumer profiles,
provider/auth config, журналы и зависимости. Просмотрите будущую выборку
`git diff --cached --name-status` и `git diff --cached`, затем экспортируйте
индекс в отдельный временный каталог через `git checkout-index --all --prefix`.
Сканируйте именно этот каталог с `--root <snapshot> --json .`; скан checkout
по умолчанию не заменяет проверку всей публикуемой выборки.

## 2. Проверки и commit

Локально выполните затронутые регрессии, Ruff и `git diff --check`. Для документов
проверьте ссылки и CLI-примеры; полный набор принадлежит CI ChangeRail.
Перед push получите актуальные refs и проверьте достижимую историю:

```sh
git fetch origin --tags
python3 scripts/public-surface-scan.py --history --json
.venv/bin/python -m ruff check scripts tools/changerail/tests distribution.py
git diff --check
```

Сканер ищет известные утечки; дополнительно просмотрите новые пути, diff и
содержимое архива. Замечание сканера разбирают до публикации, не скрывают
исключением для конкретного потребителя.

Создайте осмысленный commit только из проверенных файлов и отправьте `main`
обычным push. При расхождении с remote сначала согласуйте изменения. CI должен
пройти на **точном release commit** для Python 3.11 и 3.12, включая Node wrapper,
Ruff, public-surface scan и diff. Остановленный оператором набор автоматически
не перезапускают. При ошибке исправьте причину новым коммитом и проверяйте его CI.

```sh
git rev-parse HEAD
gh run list --branch main --limit 5
gh run view REPLACE_WITH_RUN_ID --json headSha,status,conclusion,jobs,url
```

## 3. Сборка точного коммита

Используйте точный commit, совпадающий с `origin/main`, после успешного CI.
В основном checkout не должно быть незакоммиченных изменений tracked-файлов
или staged payload. Посторонние untracked-файлы разрешено сохранить на месте:
заранее зафиксируйте их inventory и убедитесь, что их нет в индексе. Не удаляйте
их ради сборки; источником архива служит только экспорт выбранного commit.
В Bash задайте версию; все результаты ниже остаются локально. Свежий временный
source snapshot исключает незакоммиченные файлы из архива.

```bash
export CHRL_RELEASE_VERSION=2.0.0-rc.4
export CHRL_RELEASE_COMMIT=$(git rev-parse HEAD)
export CHRL_RELEASE_TREE=$(git rev-parse 'HEAD^{tree}')
git diff --quiet
git diff --cached --quiet
git ls-files --others --exclude-standard
test "$CHRL_RELEASE_COMMIT" = "$(git rev-parse origin/main)"
git check-ignore -q .runtime/release-probe/audit.json
mkdir -p .runtime
export CHRL_RELEASE_DIR=$(mktemp -d "$PWD/.runtime/release-XXXXXXXX")
export CHRL_RELEASE_SOURCE=$(mktemp -d)
git archive "$CHRL_RELEASE_COMMIT" | tar -x -C "$CHRL_RELEASE_SOURCE"
python3 scripts/public-surface-scan.py --root "$CHRL_RELEASE_SOURCE" --json .
python3 distribution.py build --source "$CHRL_RELEASE_SOURCE" \
  "$CHRL_RELEASE_DIR/changerail-$CHRL_RELEASE_VERSION-runtime.tar.gz"
python3 distribution.py build --source "$CHRL_RELEASE_SOURCE" \
  "$CHRL_RELEASE_DIR/reproducibility.tar.gz"
cmp "$CHRL_RELEASE_DIR/changerail-$CHRL_RELEASE_VERSION-runtime.tar.gz" \
  "$CHRL_RELEASE_DIR/reproducibility.tar.gz"
```

Проверьте список файлов `tar -tzf <archive>`: runtime-архив исключает тесты,
профили, зависимости и журналы. Создайте provenance и сверьте каждый файл с Git:

```python
# Выполнить через python3 из корня того же checkout с переменными выше.
import hashlib
import json
import os
import subprocess
from pathlib import Path
import distribution

version = os.environ['CHRL_RELEASE_VERSION']
commit = os.environ['CHRL_RELEASE_COMMIT']
tree = os.environ['CHRL_RELEASE_TREE']
release_dir = Path(os.environ['CHRL_RELEASE_DIR'])
archive = release_dir / f'changerail-{version}-runtime.tar.gz'
manifest, payload = distribution.inspect_archive(archive)
assert manifest['version'] == version
for name, (data, mode) in payload.items():
    assert subprocess.check_output(['git', 'show', f'{commit}:{name}']) == data
    git_mode = subprocess.check_output(
        ['git', 'ls-tree', commit, '--', name], text=True
    ).split()[0]
    assert mode == (0o755 if git_mode == '100755' else 0o644)
provenance = {
    'schema': 'changerail.release-provenance.v1',
    'version': version, 'planned_tag': f'v{version}',
    'source_commit': commit, 'source_tree': tree,
    'historical_upstream_commit': manifest['provenance']['upstream_commit'],
    'archive': archive.name,
    'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
    'payload_sha256': manifest['payload_sha256'],
    'source_url': f'https://github.com/vlikhobabin/changerail/tree/{commit}',
}
provenance_file = release_dir / 'release-provenance.json'
provenance_file.write_text(json.dumps(provenance, indent=2) + '\n')
(release_dir / 'SHA256SUMS').write_text(''.join(
    f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n'
    for path in (archive, provenance_file)
))
```

Сохраните результат CI и отчёты сканирования рядом с assets локально. Из
`docs/releases/<version>.md` подготовьте `release-notes.md`: ссылки на документы
преобразуйте в GitHub blob URL точного commit, добавьте завершённый CI и его
результаты. Не публикуйте подготовительные logs или локальные пути.

## 4. Тег и GitHub Release

Сверьте `headSha` CI с `CHRL_RELEASE_COMMIT`, remote `main`, контрольные суммы,
текст release notes и отсутствие такого тега/релиза. После решения о публикации:

```bash
git tag -a "v$CHRL_RELEASE_VERSION" "$CHRL_RELEASE_COMMIT" \
  -m "ChangeRail $CHRL_RELEASE_VERSION"
git push origin "refs/tags/v$CHRL_RELEASE_VERSION"
gh release create "v$CHRL_RELEASE_VERSION" --repo vlikhobabin/changerail \
  --verify-tag --prerelease --title "ChangeRail $CHRL_RELEASE_VERSION" \
  --notes-file "$CHRL_RELEASE_DIR/release-notes.md" \
  "$CHRL_RELEASE_DIR/changerail-$CHRL_RELEASE_VERSION-runtime.tar.gz" \
  "$CHRL_RELEASE_DIR/SHA256SUMS" "$CHRL_RELEASE_DIR/release-provenance.json"
```

`--prerelease` обязателен для RC. Stable release требует отдельного решения о
готовности. `--verify-tag` исключает неявное создание тега GitHub CLI. Если upload
прервался, сначала прочитайте состояние существующего релиза; не перемещайте тег
и не создавайте новый вслепую.

## 5. Проверка опубликованного результата

```bash
git ls-remote origin "refs/tags/v$CHRL_RELEASE_VERSION*"
gh release view "v$CHRL_RELEASE_VERSION" --repo vlikhobabin/changerail \
  --json url,tagName,isDraft,isPrerelease,publishedAt,assets
gh release download "v$CHRL_RELEASE_VERSION" --repo vlikhobabin/changerail \
  --dir "$CHRL_RELEASE_DIR/downloaded" \
  --pattern "changerail-$CHRL_RELEASE_VERSION-runtime.tar.gz" \
  --pattern SHA256SUMS --pattern release-provenance.json
(cd "$CHRL_RELEASE_DIR/downloaded" && sha256sum -c SHA256SUMS)
cmp "$CHRL_RELEASE_DIR/SHA256SUMS" "$CHRL_RELEASE_DIR/downloaded/SHA256SUMS"
```

Убедитесь, что peeled tag указывает на проверенный commit, релиз опубликован
с нужным типом, набор assets точен, а скачанные байты совпадают с исходными.
Сохраните URL и подтверждение публикации в локальной записи выпуска. `git status`
должен показывать только осознанные новые изменения; пользовательские настройки
остаются нетронутыми.

## 6. Обновление рабочего checkout

После проверки скачанных assets следуйте [runbook рабочего checkout](working-checkout.md).
Обновление consumers и engine binding — отдельные операции. Сохранённые результаты
полного набора применимы к проверенным байтам; документационный релиз не требует
нового локального полного запуска, но CI точного release commit остаётся gate.
