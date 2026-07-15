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
bin/openspec               -> /opt/changerail/bin/openspec
bin/changerail-review-verdict    -> /opt/changerail/bin/changerail-review-verdict
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
ln -sfnT "$ChangeRail/bin/changerail-review-verdict" "$PROJECT/bin/changerail-review-verdict"

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
