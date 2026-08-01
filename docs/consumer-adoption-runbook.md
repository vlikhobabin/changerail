# Runbook подключения существующего проекта к ChangeRail

Этот runbook нужен для случая, когда ChangeRail уже опубликован как отдельный
source of truth, а существующий проект нужно подключить к workflow
`explore -> ff -> do -> review -> pub`.

Цель: настроить **один выбранный проект** как ChangeRail consumer, не копируя ChangeRail
целиком внутрь проекта и не теряя проектные правила.

Для workspace-агрегатора с несколькими дочерними git-репозиториями default -
подключать и проверять каждый дочерний репозиторий как отдельный ChangeRail
consumer. Root workspace может держать roadmap, inventory или integration
карточки, но обычный delivery запускается в child repo через `--workspace`.

## Короткий промпт для агента

Передайте своему агенту этот текст, заменив `PROJECT_PATH` на путь к
выбранному проекту:

```text
Подключи один существующий проект к ChangeRail.

ChangeRail repo: https://github.com/vlikhobabin/changerail.git
ChangeRail root: /opt/changerail
Project: PROJECT_PATH

Если /opt/changerail отсутствует, клонируй repo в /opt/changerail. Если /opt/changerail уже
есть, не перезаписывай его: покажи remote, branch, HEAD и git status.
Настраивай только PROJECT_PATH, другие проекты не трогай.

Сначала прочитай /opt/changerail/docs/consumer-adoption-runbook.md,
/opt/changerail/docs/wiring-discovery.md и /opt/changerail/AGENTS.shared.md.
Не запускай bootstrap-project поверх непустого существующего проекта.
Если в PROJECT_PATH грязное git-дерево или существующие .claude/.codex/bin
файлы конфликтуют с ChangeRail wiring, остановись и покажи, что требует решения.

Аккуратно подключи ChangeRail wiring через symlink-и, сохрани проектные правила,
обнови AGENTS.md/CLAUDE.md/.mcp.json/.codex/config.toml/.gitignore и создай
OpenSpec skeleton, если его нет. В конце запусти:
/opt/changerail/bin/verify-project PROJECT_PATH
git -C PROJECT_PATH diff --check

Не коммить без отдельной команды. В ответе покажи итоговый diff summary,
результаты проверок и список файлов, которые нужно закоммитить в Project.
```

## Что должен сделать человек

1. Выбрать ровно один проект для подключения.
2. Убедиться, что в проекте нет незавершенного чужого WIP, который нельзя
   смешивать с migration diff.
3. Запустить агента из корня выбранного проекта или явно передать ему
   абсолютный `PROJECT_PATH`.
4. После зеленого `verify-project` просмотреть diff и закоммитить изменения в
   репозитории проекта.

## Workspace с дочерними репозиториями

Если путь вроде `/opt/example-workspace` содержит несколько независимых
дочерних git-репозиториев, не настраивайте весь root как один большой проект по
умолчанию. Default protocol:

1. Найти дочерние repos, в которых реально живут code, local rules и
   `openspec/board/`.
2. Подключить ChangeRail wiring отдельно в каждом выбранном child repo.
3. Запустить `/opt/changerail/bin/verify-project <child-repo>` для каждого.
4. Коммитить wiring и delivery payload в соответствующем child repo, не в root.
5. Использовать root только для roadmap/inventory/integration карточек, если он
   сам является отдельным git project с собственной доской.

Параллельный delivery допустим между разными child repos:

```bash
/opt/changerail/bin/changerail-delivery-runner run \
  --workspace /opt/example-workspace/service-a \
  openspec/board/1.backlog/example-card.md

/opt/changerail/bin/changerail-delivery-runner run \
  --workspace /opt/example-workspace/service-b \
  openspec/board/1.backlog/another-card.md
```

Если single-card preflight блокируется на remote publish target, status
классифицирует причину как `ssh_config`, `dns`, `auth`, `missing_branch`,
`timeout` или `unknown_remote_failure`. После исправления transient или
операторской причины используйте explicit resume; он повторит полный fresh
preflight и продолжит только при доказанном publish target:

```bash
/opt/changerail/bin/changerail-delivery-runner resume \
  --status-path /opt/example-workspace/service-a/.runtime/changerail/delivery-runs/<run-id>/status.json
```

Для dependency-ordered очереди через несколько child repos используйте
consumer-owned JSON plan с workspace aliases и relative paths:

```json
{
  "schema": "changerail.delivery-plan.v1",
  "id": "example-plan",
  "max_parallel": 2,
  "per_workspace_parallelism": 1,
  "workspaces": [
    {"alias": "service-a", "path": "service-a"},
    {"alias": "service-b", "path": "service-b"}
  ],
  "cards": [
    {"id": "service-a-card", "workspace": "service-a", "card": "service-a-card.md", "wave": 1},
    {
      "id": "service-b-card",
      "workspace": "service-b",
      "card": "service-b-card.md",
      "depends_on": ["service-a-card"],
      "wave": 2
    }
  ]
}
```

Typical queue lifecycle:

```bash
/opt/changerail/bin/changerail-delivery-runner plan delivery-plan.json \
  --consumer-root /opt/example-workspace --json
/opt/changerail/bin/changerail-delivery-runner preflight-plan delivery-plan.json \
  --consumer-root /opt/example-workspace --json
/opt/changerail/bin/changerail-delivery-runner run-plan delivery-plan.json \
  --consumer-root /opt/example-workspace
/opt/changerail/bin/changerail-delivery-runner status-plan \
  /opt/example-workspace/.runtime/changerail/delivery-plans/<run-id>/status.json --json
```

При safety stop исправьте blocked workspace/card, затем используйте
`resume-plan` с previous aggregate status. Runtime status, raw logs и locks
остаются ignored under `.runtime/changerail/`; plan examples не должны
содержать credentials, secrets или machine-specific absolute paths.

Если root отслеживает child repos как submodules/gitlinks или содержит общий
integration manifest, root-level update выполняйте после child-repo publish как
отдельный serial step.

## Установка ChangeRail source of truth

ChangeRail устанавливается отдельно от проекта:

```bash
git clone https://github.com/vlikhobabin/changerail.git /opt/changerail
cd /opt/changerail
```

Если `/opt/changerail` уже существует, сначала проверьте, что это ожидаемый checkout:

```bash
git -C /opt/changerail remote -v
git -C /opt/changerail branch --show-current
git -C /opt/changerail rev-parse HEAD
git -C /opt/changerail status --short
```

Не удаляйте и не перезаписывайте существующий `/opt/changerail` автоматически.

## Почему не bootstrap поверх существующего проекта

`bin/bootstrap-project` предназначен для нового или пустого проекта. Для
живого проекта он полезен как source of truth по templates, но migration нужно
делать как аккуратный adoption:

- сохранить существующие `AGENTS.md`, `CLAUDE.md`, `.mcp.json`,
  `.codex/config.toml`, `.gitignore` и локальные правила;
- добавить недостающие ChangeRail-секции;
- заменить только ChangeRail-owned surfaces на symlink-и;
- не удалять пользовательские команды, skills или project-specific tooling без
  явного решения владельца проекта.

## Целевой wiring проекта

Потребительский проект должен видеть ChangeRail через project-local paths:

```text
.claude/skills             -> /opt/changerail/skills
.claude/commands/changerail      -> /opt/changerail/claude/commands/changerail
.claude/commands/chrl      -> /opt/changerail/claude/commands/chrl
.codex/skills/changerail-*       -> /opt/changerail/skills/changerail-*
.codex/skills/chrl-*       -> /opt/changerail/skills/chrl-*
.codex/skills/openspec-*   -> /opt/changerail/skills/openspec-*
bin/openspec                    -> /opt/changerail/bin/openspec
bin/changerail-python           -> /opt/changerail/bin/changerail-python
bin/changerail-review-verdict   -> /opt/changerail/bin/changerail-review-verdict
bin/changerail-evidence         -> /opt/changerail/bin/changerail-evidence
```

Практический shell-фрагмент для агента:

```bash
ChangeRail=/opt/changerail
PROJECT=/opt/example-project

mkdir -p "$PROJECT/.claude/commands" "$PROJECT/.codex/skills" "$PROJECT/bin"

ln -sfnT "$ChangeRail/skills" "$PROJECT/.claude/skills"
ln -sfnT "$ChangeRail/claude/commands/changerail" "$PROJECT/.claude/commands/changerail"
ln -sfnT "$ChangeRail/claude/commands/chrl" "$PROJECT/.claude/commands/chrl"
ln -sfnT "$ChangeRail/bin/openspec" "$PROJECT/bin/openspec"
ln -sfnT "$ChangeRail/bin/changerail-python" "$PROJECT/bin/changerail-python"
ln -sfnT "$ChangeRail/bin/changerail-review-verdict" "$PROJECT/bin/changerail-review-verdict"
ln -sfnT "$ChangeRail/bin/changerail-evidence" "$PROJECT/bin/changerail-evidence"

for skill_path in "$ChangeRail"/skills/*; do
  [ -f "$skill_path/SKILL.md" ] || continue
  skill_name="$(basename "$skill_path")"
  ln -sfnT "$skill_path" "$PROJECT/.codex/skills/$skill_name"
done
```

Если команда не может заменить существующий реальный каталог или файл, агент
должен остановиться и показать конфликт. Типовые конфликты:

- `.claude/skills` уже является реальным каталогом с project-specific skills;
- `.claude/commands/changerail` содержит ручную копию старых команд;
- `.claude/commands/chrl` содержит ручную копию старых команд;
- `.codex/skills/<skill>` является локальной копией, а не symlink-ом;
- `bin/openspec` уже используется проектом для другого wrapper-а.

## Project-local файлы

Проектные файлы остаются в проекте и коммитятся там:

- `AGENTS.md` - локальные правила проекта + ChangeRail generated section;
- `CLAUDE.md` - короткая подсказка Claude, что команды доступны как
  `/chrl:*` для ежедневной работы и `/changerail:*` как canonical form;
- `.mcp.json` - filesystem MCP scope должен покрывать корень проекта;
- `.codex/config.toml` - trusted project entry и filesystem MCP scope для
  корня проекта;
- `.gitignore` - runtime/auth state должен быть ignored;
- `openspec/config.yaml` и `openspec/board/` - OpenSpec skeleton проекта.

Для новых файлов используйте templates из `/opt/changerail/templates/project/`. Для
существующих файлов делайте merge, а не blind overwrite.

В `AGENTS.md` default-форма для надежного agent context - generated section из
`/opt/changerail/AGENTS.shared.md`:

```md
<!-- CHANGERAIL_SHARED_AGENTS_BEGIN source="/opt/changerail/AGENTS.shared.md" -->
... содержимое /opt/changerail/AGENTS.shared.md ...
<!-- CHANGERAIL_SHARED_AGENTS_END -->
```

Перед этим блоком должны остаться project-specific правила: назначение
проекта, verification baseline, public/private policy, локальные команды и
ограничения.

## Codex Auth For Delivery Runner

`verify-project` проверяет wiring и ignore policy, но unattended delivery runner
нуждается еще и в effective Codex auth source. Это относится к single-card
команде `changerail-delivery-runner run` и к plan-oriented командам
`preflight-plan`, `run-plan` и `resume-plan`: без auth preflight должен
остановиться fail-closed до запуска delivery child.

Для queue plans plan runner запускает ChangeRail single-card runner, а single-card runner запускает Codex.
Примечание: consumer repository не обязан иметь tracked `bin/codex`. Supported path - запускать
`/opt/changerail/bin/changerail-delivery-runner` из ChangeRail checkout или
передать явный supported launcher через `--launcher`. `CODEX_WORKDIR` и
effective `CODEX_HOME` задаются для каждого child workspace.

Runner выбирает auth location так:

- если оператор явно задал `CODEX_HOME`, используется этот каталог;
- иначе effective `CODEX_HOME` равен `<workspace>/.codex`, где `workspace` -
  consumer repository из `--workspace` или текущий git-root;
- auth считается готовым, если есть supported marker вроде `auth.json` или
  `auth.toml` внутри effective `CODEX_HOME`, либо задана supported auth
  environment variable.

Project-local marker должен оставаться ignored local state. В generated
`.gitignore` для consumer проекта есть `.codex/auth.json` и
`.codex/auth.toml`; не добавляйте эти файлы в tracked payload, не публикуйте их
в docs, status или logs и не копируйте credentials автоматически во время
adoption.

Безопасный локальный вариант - symlink на уже настроенный Codex auth:

```bash
mkdir -p /opt/example-project/.codex
ln -sfn "$HOME/.codex/auth.json" /opt/example-project/.codex/auth.json
/opt/changerail/bin/changerail-delivery-runner preflight \
  openspec/board/3.inprogress/example-card.md \
  --workspace /opt/example-project --json
```

Для нового пустого consumer project можно сделать тот же local symlink во время
bootstrap, но только явным opt-in:

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project \
  --name example-project \
  --kind generic \
  --link-codex-auth "$HOME/.codex/auth.json"
```

Если source auth file отсутствует, bootstrap должен остановиться без создания
dangling auth marker. Default bootstrap не создает `.codex/auth.json` или
`.codex/auth.toml`.

Если auth должен жить вне проекта, запускайте runner с explicit `CODEX_HOME`:

```bash
CODEX_HOME="$HOME/.codex" /opt/changerail/bin/changerail-delivery-runner preflight \
  openspec/board/3.inprogress/example-card.md \
  --workspace /opt/example-project --json
```

Для queue plans сначала проверяйте readiness без live delivery:

```bash
/opt/changerail/bin/changerail-delivery-runner generate-plan --id example-plan \
  --workspace service-a=service-a --workspace service-b=service-b \
  --card service-a-card.md \
  --card service-b-card=service-b:service-b-card.md \
  --depends service-b-card=service-a-card \
  --output delivery-plan.json --consumer-root /opt/example-workspace
/opt/changerail/bin/changerail-delivery-runner preflight-plan delivery-plan.json \
  --consumer-root /opt/example-workspace --json
```

Если output содержит `CODEX auth: fail`, настройте project-local ignored marker,
задайте explicit `CODEX_HOME` или используйте supported auth environment
variable. Если output содержит `CODEX_HOME symlinks: fail`, пересоздайте stale
symlink-и внутри effective `CODEX_HOME` перед `run-plan` или `resume-plan`.

## Проверка

Минимальный gate после migration:

```bash
/opt/changerail/bin/verify-project /opt/example-project
git -C /opt/example-project diff --check
git -C /opt/example-project status --short
```

`verify-project` проверяет:

- symlink-и `.claude`, `.codex/skills` и `bin/`;
- `.mcp.json` и `.codex/config.toml`;
- `openspec/config.yaml` и `bin/openspec validate --all --strict`;
- обязательные `.gitignore` patterns для runtime/auth state;
- что запрещенный runtime/auth state не попал в tracked files.

Итог `summary: pass-with-diagnostics` допустим только для explicitly
non-blocking findings, например intentionally optional surface или tracked
project-wide baseline debt с residual risk. `summary: fail` остается blocking
gate. Targeted card-owned OpenSpec validation нельзя переводить в optional.

## Ожидаемый результат

После подключения пользователь запускает Claude Code из корня проекта и видит
ChangeRail команды:

```text
/chrl:explore
/chrl:ff
/chrl:do
/chrl:review
/chrl:pub
/chrl:deliver
/changerail:explore
/changerail:ff
/changerail:do
/changerail:review
/changerail:pub
/changerail:deliver
```

Для Codex доступны соответствующие skills `$chrl-*`, `$changerail-*` и
`openspec-*`.

Изменения коммитятся в репозитории проекта. В `/opt/changerail` ничего коммитить не
нужно, если сам ChangeRail не менялся.
