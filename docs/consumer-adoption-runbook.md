# Runbook подключения существующего проекта к OPSX

Этот runbook нужен для случая, когда OPSX уже опубликован как отдельный
source of truth, а существующий проект нужно подключить к workflow
`explore -> ff -> do -> review -> pub`.

Цель: настроить **один выбранный проект** как OPSX consumer, не копируя OPSX
целиком внутрь проекта и не теряя проектные правила.

## Короткий промпт для агента

Передайте своему агенту этот текст, заменив `PROJECT_PATH` на путь к
выбранному проекту:

```text
Подключи один существующий проект к OPSX.

OPSX repo: https://github.com/vlikhobabin/opsx.git
OPSX root: /opt/opsx
Project: PROJECT_PATH

Если /opt/opsx отсутствует, клонируй repo в /opt/opsx. Если /opt/opsx уже
есть, не перезаписывай его: покажи remote, branch, HEAD и git status.
Настраивай только PROJECT_PATH, другие проекты не трогай.

Сначала прочитай /opt/opsx/docs/consumer-adoption-runbook.md,
/opt/opsx/docs/wiring-discovery.md и /opt/opsx/AGENTS.shared.md.
Не запускай bootstrap-project поверх непустого существующего проекта.
Если в PROJECT_PATH грязное git-дерево или существующие .claude/.codex/bin
файлы конфликтуют с OPSX wiring, остановись и покажи, что требует решения.

Аккуратно подключи OPSX wiring через symlink-и, сохрани проектные правила,
обнови AGENTS.md/CLAUDE.md/.mcp.json/.codex/config.toml/.gitignore и создай
OpenSpec skeleton, если его нет. В конце запусти:
/opt/opsx/bin/verify-project PROJECT_PATH
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

## Установка OPSX source of truth

OPSX устанавливается отдельно от проекта:

```bash
git clone https://github.com/vlikhobabin/opsx.git /opt/opsx
cd /opt/opsx
```

Если `/opt/opsx` уже существует, сначала проверьте, что это ожидаемый checkout:

```bash
git -C /opt/opsx remote -v
git -C /opt/opsx branch --show-current
git -C /opt/opsx rev-parse HEAD
git -C /opt/opsx status --short
```

Не удаляйте и не перезаписывайте существующий `/opt/opsx` автоматически.

## Почему не bootstrap поверх существующего проекта

`bin/bootstrap-project` предназначен для нового или пустого проекта. Для
живого проекта он полезен как source of truth по templates, но migration нужно
делать как аккуратный adoption:

- сохранить существующие `AGENTS.md`, `CLAUDE.md`, `.mcp.json`,
  `.codex/config.toml`, `.gitignore` и локальные правила;
- добавить недостающие OPSX-секции;
- заменить только OPSX-owned surfaces на symlink-и;
- не удалять пользовательские команды, skills или project-specific tooling без
  явного решения владельца проекта.

## Целевой wiring проекта

Потребительский проект должен видеть OPSX через project-local paths:

```text
.claude/skills             -> /opt/opsx/skills
.claude/commands/opsx      -> /opt/opsx/claude/commands/opsx
.codex/skills/opsx-*       -> /opt/opsx/skills/opsx-*
.codex/skills/openspec-*   -> /opt/opsx/skills/openspec-*
bin/openspec               -> /opt/opsx/bin/openspec
bin/opsx-review-verdict    -> /opt/opsx/bin/opsx-review-verdict
```

Практический shell-фрагмент для агента:

```bash
OPSX=/opt/opsx
PROJECT=/opt/example-project

mkdir -p "$PROJECT/.claude/commands" "$PROJECT/.codex/skills" "$PROJECT/bin"

ln -sfnT "$OPSX/skills" "$PROJECT/.claude/skills"
ln -sfnT "$OPSX/claude/commands/opsx" "$PROJECT/.claude/commands/opsx"
ln -sfnT "$OPSX/bin/openspec" "$PROJECT/bin/openspec"
ln -sfnT "$OPSX/bin/opsx-review-verdict" "$PROJECT/bin/opsx-review-verdict"

for skill_path in "$OPSX"/skills/*; do
  [ -f "$skill_path/SKILL.md" ] || continue
  skill_name="$(basename "$skill_path")"
  ln -sfnT "$skill_path" "$PROJECT/.codex/skills/$skill_name"
done
```

Если команда не может заменить существующий реальный каталог или файл, агент
должен остановиться и показать конфликт. Типовые конфликты:

- `.claude/skills` уже является реальным каталогом с project-specific skills;
- `.claude/commands/opsx` содержит ручную копию старых команд;
- `.codex/skills/<skill>` является локальной копией, а не symlink-ом;
- `bin/openspec` уже используется проектом для другого wrapper-а.

## Project-local файлы

Проектные файлы остаются в проекте и коммитятся там:

- `AGENTS.md` - локальные правила проекта + OPSX generated section;
- `CLAUDE.md` - короткая подсказка Claude, что команды доступны как
  `/opsx:*`;
- `.mcp.json` - filesystem MCP scope должен покрывать корень проекта;
- `.codex/config.toml` - trusted project entry и filesystem MCP scope для
  корня проекта;
- `.gitignore` - runtime/auth state должен быть ignored;
- `openspec/config.yaml` и `openspec/board/` - OpenSpec skeleton проекта.

Для новых файлов используйте templates из `/opt/opsx/templates/project/`. Для
существующих файлов делайте merge, а не blind overwrite.

В `AGENTS.md` default-форма для надежного agent context - generated section из
`/opt/opsx/AGENTS.shared.md`:

```md
<!-- OPSX_SHARED_AGENTS_BEGIN source="/opt/opsx/AGENTS.shared.md" -->
... содержимое /opt/opsx/AGENTS.shared.md ...
<!-- OPSX_SHARED_AGENTS_END -->
```

Перед этим блоком должны остаться project-specific правила: назначение
проекта, verification baseline, public/private policy, локальные команды и
ограничения.

## Проверка

Минимальный gate после migration:

```bash
/opt/opsx/bin/verify-project /opt/example-project
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
OPSX команды:

```text
/opsx:explore
/opsx:ff
/opsx:do
/opsx:review
/opsx:pub
/opsx:deliver
```

Для Codex доступны соответствующие skills `$opsx-*` и `openspec-*`.

Изменения коммитятся в репозитории проекта. В `/opt/opsx` ничего коммитить не
нужно, если сам OPSX не менялся.
