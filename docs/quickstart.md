# Первый запуск ChangeRail

Этот сценарий устанавливает runtime `v2.0.0-rc.5` в новый Git-проект на Linux
после публикации тега и assets и проверки CI точного release commit.
Для существующего проекта с прежним ChangeRail используйте
[принятие и обновление](../DISTRIBUTION.md); для разработки общего исходника —
[подключение checkout](shared-source.md).

Нужны Python 3.11+ с `venv` и pip, Git, GitHub CLI (`gh`), Node.js >=20.19.0,
npm и заранее установленный и авторизованный Codex CLI. Модели из профиля должны
быть доступны вашему аккаунту. Подготовьте существующий remote проекта, права на
push в его `main`, Git identity (`user.name`, `user.email`) и зависимости проверок
продукта. Установка runtime не устанавливает Codex и не настраивает авторизацию.

`run` запускает модель с полномочиями текущего пользователя, реализует принятую
карточку и после проверок **сам создаёт commit и выполняет push** в upstream
текущей ветки. Поддерживается ветка `main`; её правила должны допускать такую
публикацию. `require_push = false` не отключает push: сейчас это поле влияет
только на сетевую проверку `doctor`. Перед первым запуском прочитайте
[полномочия и локальные настройки](../SECURITY.md).

## 1. Получить и проверить выпуск

Выберите свободные каталоги. В примерах checkout инструмента и проект независимы;
переменные действуют в одной Bash-сессии.

```sh
release_tag=v2.0.0-rc.5
release_version=2.0.0-rc.5
tool_root="$HOME/tools/changerail-$release_version"
release_dir="$HOME/downloads/changerail-$release_version"
project_root="$HOME/projects/example-project"
mkdir -p "$(dirname "$tool_root")" "$release_dir" "$(dirname "$project_root")"
gh release view "$release_tag" --repo vlikhobabin/changerail
gh release download "$release_tag" --repo vlikhobabin/changerail \
  --dir "$release_dir" \
  --pattern "changerail-$release_version-runtime.tar.gz" \
  --pattern SHA256SUMS --pattern release-provenance.json
git clone --branch "$release_tag" --depth 1 \
  https://github.com/vlikhobabin/changerail.git "$tool_root"
(cd "$release_dir" && sha256sum --check SHA256SUMS)
```

Сверьте происхождение с checkout **того же тега**, а затем проверьте структуру
и внутренние хеши архива установщиком из этого checkout:

```sh
python3 - "$tool_root" "$release_dir" "$release_tag" "$release_version" <<'PY'
import hashlib
import json
from pathlib import Path
import subprocess
import sys

source, assets = map(Path, sys.argv[1:3])
tag, version = sys.argv[3:5]
record = json.loads((assets / "release-provenance.json").read_text())
archive_name = f"changerail-{version}-runtime.tar.gz"
def git_revision(ref):
    return subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", ref], text=True
    ).strip()
assert record["schema"] == "changerail.release-provenance.v1"
assert record["version"] == version and record["planned_tag"] == tag
assert record["source_commit"] == git_revision("HEAD") == git_revision(f"{tag}^{{commit}}")
assert record["source_tree"] == git_revision("HEAD^{tree}")
assert record["archive"] == archive_name
assert record["archive_sha256"] == hashlib.sha256((assets / archive_name).read_bytes()).hexdigest()
print("Происхождение и SHA256 архива совпадают с выбранным тегом")
PY
python3 "$tool_root/distribution.py" verify \
  "$release_dir/changerail-$release_version-runtime.tar.gz"
```

При любой ошибке остановитесь. SHA256 доказывает совпадение байтов, а provenance
связывает их с Git; доверие к владельцу репозитория и выбранному выпуску остаётся
исходным условием. Поле `historical_upstream_commit` описывает происхождение
рефакторинга, а точный выпуск задают `source_commit` и `source_tree`.

## 2. Подготовить потребителя и установить runtime

Клонируйте **свой** remote, заменив пример URL. В нём должна существовать ветка
`main` хотя бы с одним commit; для пустого remote сначала создайте и опубликуйте
начальную `main` штатными средствами Git. Команды ниже не меняют ветку
существующего рабочего проекта.

```sh
git clone --branch main git@github.com:YOUR-ORG/example-project.git "$project_root"
cd "$project_root"
git status --short
git rev-parse --abbrev-ref --symbolic-full-name '@{u}'
cat >> .gitignore <<'IGNORE'

# Local ChangeRail configuration, evidence and dependencies
.runtime/
.changerail/profile.toml
.codex/
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
node_modules/
npm-logs/
IGNORE
git check-ignore .runtime/probe
python3 "$tool_root/distribution.py" install \
  "$release_dir/changerail-$release_version-runtime.tar.gz" "$project_root" --dry-run
python3 "$tool_root/distribution.py" install \
  "$release_dir/changerail-$release_version-runtime.tar.gz" "$project_root"
python3 -m venv .venv
.venv/bin/python -m pip install 'jsonschema>=4.23,<5'
mkdir -p .changerail
cp tools/changerail/templates/profile.toml .changerail/profile.toml
```

Используйте принятый в проекте способ установки Python-зависимостей, если в нём
уже есть окружение. `bin/chrl` выбирает проектный `.venv/bin/python` первым.
Тестовые зависимости ChangeRail и его полный набор тестов потребителю не нужны.

## 3. Настроить launcher, профиль и OpenSpec

Профиль `.changerail/profile.toml` принадлежит проекту. До запуска настройте
`models.implementation`, `models.review` и обе группы команд `verification`.
Если проект хочет разрешить строго ограниченное продолжение после доказанного
отказа capacity модели между группами, добавьте отдельный
`models.technical_recovery`: это должна быть отличающаяся fallback-модель.
Без этого явного маршрута такое recovery fail-closed. Этот маршрут не добавляет
третье ревью и не используется для ошибок продукта, проверки или оператора.
Замените шаблонные pytest-команды реальными проверками продукта и установите их
зависимости. Сохраните максимум два независимых ревью: repair и продолжение
используют общий остаток. Credentials храните в локальном хранилище провайдера,
не в профиле или карточке.

`adapters.codex.launcher` — путь относительно корня проекта; по умолчанию
`bin/codex`. Если проект ещё не имеет launcher, следующий пример сохраняет
абсолютный путь к уже установленному CLI и передаёт все аргументы адаптера:

```sh
python3 - <<'PY'
from pathlib import Path
import shlex
import shutil

cli = shutil.which("codex")
if cli is None:
    raise SystemExit("Сначала установите и авторизуйте Codex CLI")
launcher = Path("bin/codex")
with launcher.open("x") as stream:
    stream.write("#!/bin/sh\nexec " + shlex.quote(str(Path(cli).resolve())) + ' "$@"\n')
launcher.chmod(0o755)
PY
./bin/codex --version
mkdir -p openspec/specs openspec/changes \
  openspec/board/1.backlog openspec/board/2.todo \
  openspec/board/3.inprogress openspec/board/4.done
cat > openspec/config.yaml <<'CONFIG'
schema: spec-driven
context: |
  Проект использует ChangeRail openspec-v1: одна карточка и один change.
  Дополните этот контекст архитектурой и правилами своего проекта.
CONFIG
```

Для существующего `openspec/config.yaml` сохраните его настройки и дополните
контекст; не перезаписывайте файл примером. Используется стандартная схема
`spec-driven` OpenSpec 1.3.1; локальные `openspec/schemas` не поддерживаются.
Генерация глобальных инструкций и `openspec init` для этого сценария не нужны.

Зависимости OpenSpec устанавливаются **в потребителе**. При заполненном npm cache:

```sh
./tools/openspec/bootstrap.sh --offline
```

Если нужных tarballs в cache нет, отдельно выполните разрешённую сетевую
установку закреплённого дерева зависимостей:

```sh
npm --prefix "$project_root/tools/openspec" ci \
  --ignore-scripts --no-audit --no-fund \
  --logs-dir "$project_root/tools/openspec/npm-logs"
```

Это явная установка зависимостей, а не fallback runtime. Затем:

```sh
./bin/openspec --project "$project_root" --version
./bin/chrl --project "$project_root" wiring
```

Ожидаются версия `1.3.1` и `"ok": true`. Проверка wiring не подтверждает доступ
к модели и не выполняет продуктовую доставку. Детали выбора проекта и установки —
в [OpenSpec README](../tools/openspec/README.md).

## 4. Подготовить одну карточку и один change

Выберите небольшой реальный инвариант продукта. Следующие команды создают
заготовки; содержимое требований и план evidence оператор готовит по своей задаче.
Пример slug `first-change` замените осмысленным именем.

```sh
chrl_board=openspec/board
chrl_slug=first-change
cp tools/changerail/templates/card-template.md \
  "$chrl_board/1.backlog/$chrl_slug.md"
./bin/openspec --project "$project_root" new change first-change --schema spec-driven
./bin/openspec --project "$project_root" instructions proposal --change first-change
```

Заполните `proposal.md`, затем получите инструкции `specs`, `design`, `tasks`
той же командой `instructions <artifact> --change first-change` и создайте
соответствующие файлы в `openspec/changes/first-change/`. Нужны proposal, хотя бы
один `specs/<capability>/spec.md`, design и непустой tasks. ChangeRail принимает
заголовки групп задач строго вида `## 1. group-slug`, `## 2. next-group`;
нумерация непрерывна, slug уникальны. Задачи содержат номера группы и пункта:

```markdown
## 1. implement-invariant
- [ ] 1.1 Реализовать согласованное поведение и проверить критерий C1
```

В карточке сохраните `1.backlog` в разделе `Status` и `openspec-v1` в
`Lifecycle`; в `OpenSpec Changes` укажите только `first-change`.
Замените все placeholders: scope, non-goals, зависимости, бюджет-наблюдение,
критерии с ID (`C1` и т. д.) и JSON `changerail.card-evidence.v1` в `Verify`.
Каждому критерию нужны конкретные предусловие, действие, ожидаемый результат,
метод и этап доказательства. Обоснуйте применимость рисков и неприменимые риски.
Команды и test targets должны соответствовать проекту; шаблонный `uv` не является
обязательной зависимостью. Не отмечайте запланированные проверки выполненными.

Планируйте независимые релевантные тесты, включая существующие проверки общих
границ. Расширенный test method сохраняет основной `target` и допускает уникальные
`additional_targets`: каждый из них обязателен, а proof record содержит один
`{kind, target}`. Совокупность records подтверждает условие; один выполненный
тест может поддерживать несколько условий отдельными records без повторного
запуска ради их номеров. Это не отменяет risk coverage, конкретных причин отказа
и проверки отсутствия неразрешённых записей. Assertions вызываемого helper
можно оставить на месте с проверяемой ссылкой на вызов; общий wrapper не нужен.

Эти расширения входят в `v2.0.0-rc.5` и требуют совместимого engine
**до принятия плана**. Старый `v2.0.0-rc.4` не получает их от изменения
документации: для него сохраняйте прежний singleton method без новых полей.
Не редактируйте принятый Verify и старую историю для смены формата; корректные
прежние singleton proofs поддерживаются новым reader.

```sh
./bin/openspec --project "$project_root" status --change first-change --schema spec-driven
./bin/openspec --project "$project_root" validate first-change --strict --no-interactive
./bin/chrl --project "$project_root" admission "$chrl_board/1.backlog/$chrl_slug.md"
./bin/chrl --project "$project_root" native-accept \
  "$chrl_board/1.backlog/$chrl_slug.md" --dry-run
./bin/chrl --project "$project_root" native-accept \
  "$chrl_board/1.backlog/$chrl_slug.md"
```

`native-accept` требует complete stock plan и `READY`, сохраняет его identity
в `.runtime/changerail/native-plans/first-change/native-plan.json` и перемещает
карточку в `2.todo`. Это структурное принятие плана, а не доказательство
правильности продукта. После принятия план фиксирован; в ходе реализации разрешён
прогресс checkbox задач. Сохраните локальный receipt для предстоящего запуска.

## 5. Зафиксировать подготовку и запустить доставку

Просмотрите `git status` и diff. В новом проекте подготовьте commit из
установленного runtime, Git ignore, launcher, OpenSpec config, change и карточки
в `2.todo`. Профиль, credentials, зависимости и `.runtime` остаются локальными.
Явно выберите только относящиеся к подготовке пути; не включайте постороннюю работу.

```sh
git add -- .gitignore .changerail/distribution-lock.json \
  DISTRIBUTION.md distribution.py distribution.json bin scripts tools openspec
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "Configure ChangeRail and accept first change"
git push
git status --short
./bin/chrl --project "$project_root" doctor "$chrl_board/2.todo/$chrl_slug.md"
```

Ожидаются чистое рабочее дерево и `doctor` с `"ok": true`. Не используйте
`--no-remote` для подтверждения готовности публикации: эта опция пропускает
проверку доступности upstream. `doctor` не проверяет все будущие права модели
и не гарантирует успешный push через правила сервера.

Когда проектные команды, модель и полномочия настроены, запустите:

```sh
./bin/chrl --project "$project_root" run "$chrl_board/2.todo/$chrl_slug.md"
```

Runner ведёт реализацию, evidence, независимое ревью, sync/archive и финальные
проверки; при успешной публикации карточка окажется в `4.done`, а commit —
в настроенном upstream. Наблюдения сохраняются в `.runtime/changerail/runs/`.
При остановке сохраните run и используйте [руководство оператора](operations.md);
не удаляйте receipts и не запускайте новую доставку для обнуления review allowance.
