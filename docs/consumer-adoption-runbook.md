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
Не запускай обычную генерацию bootstrap-project поверх непустого существующего
проекта. Для уже подключенного consumer допустим только explicit
`--configure-existing` с allowlisted auth/wiring actions.
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

Непосредственно перед запуском независимого payload reviewer выполните
детерминированный review preflight через уже wired helper:

```bash
bin/changerail-review-verdict preflight \
  openspec/board/3.inprogress/example-card.md --workspace . --normalize \
  --output .runtime/changerail/review-preflights/example-card.json --json
```

`blocked` означает process correction без model launch и без расхода semantic
review budget; `investigation-required` требует simplification/design вместо
очередного patch. `machine-reviewed` завершает deterministic/process review,
ordinary `ready-for-llm-review` использует `high`, а critical
credential/mutation/live/final boundary - `xhigh`. Перед live admission или
final publish полный project verification suite выполняется заново; hash-bound
evidence можно переиспользовать только внутри focused re-review неизменного
payload.

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

Обычный `bin/bootstrap-project` предназначен для нового или пустого проекта.
Для живого проекта он полезен как source of truth по templates, но migration
нужно делать как аккуратный adoption. Отдельный `--configure-existing` не
рендерит templates и допускает только explicit auth link, lock-owned
`--refresh-wiring` и `--adopt-lockless-wiring`:

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
bin/changerail-delivery-manifest -> /opt/changerail/bin/changerail-delivery-manifest
bin/bootstrap-project           -> /opt/changerail/bin/bootstrap-project
bin/verify-project              -> /opt/changerail/bin/verify-project
bin/changerail-review-verdict   -> /opt/changerail/bin/changerail-review-verdict
bin/changerail-evidence         -> /opt/changerail/bin/changerail-evidence
bin/changerail-delivery-runner  -> /opt/changerail/bin/changerail-delivery-runner
bin/changerail-delivery-metrics -> /opt/changerail/bin/changerail-delivery-metrics
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
ln -sfnT "$ChangeRail/bin/changerail-delivery-manifest" "$PROJECT/bin/changerail-delivery-manifest"
ln -sfnT "$ChangeRail/bin/bootstrap-project" "$PROJECT/bin/bootstrap-project"
ln -sfnT "$ChangeRail/bin/verify-project" "$PROJECT/bin/verify-project"
ln -sfnT "$ChangeRail/bin/changerail-review-verdict" "$PROJECT/bin/changerail-review-verdict"
ln -sfnT "$ChangeRail/bin/changerail-evidence" "$PROJECT/bin/changerail-evidence"
ln -sfnT "$ChangeRail/bin/changerail-delivery-runner" "$PROJECT/bin/changerail-delivery-runner"
ln -sfnT "$ChangeRail/bin/changerail-delivery-metrics" "$PROJECT/bin/changerail-delivery-metrics"

for skill_path in "$ChangeRail"/skills/*; do
  [ -f "$skill_path/SKILL.md" ] || continue
  skill_name="$(basename "$skill_path")"
  ln -sfnT "$skill_path" "$PROJECT/.codex/skills/$skill_name"
done
```

Maintenance helper wiring is not part of the default adoption surface. If the
project explicitly opts in to maintenance by adding tracked
`.changerail/knowledge.yaml` and `.changerail/maintenance.yaml`, also wire:

```bash
ln -sfnT "$ChangeRail/bin/changerail-maintenance" "$PROJECT/bin/changerail-maintenance"
ln -sfnT "$ChangeRail/bin/changerail-maintenance-runner" "$PROJECT/bin/changerail-maintenance-runner"
```

После opt-in выполните полный maintenance adoption flow из
[runbook maintenance-операций](maintenance-operations-runbook.md): catalog
validation, `render-index --check`, первый `scan --json`, lifecycle report,
baseline/waiver policy, scheduler setup, feedback/quality rollup и card
handoff. Scheduler examples находятся в `examples/maintenance/`:

- `examples/maintenance/github-actions-readonly.yml` - read-only GitHub
  scheduled audit с `contents: read`;
- `examples/maintenance/ci-readonly-vs-write.yml` - разделение read-only
  analysis и отдельного write-capable workflow;
- `examples/maintenance/codex-scheduled-task.md` - scheduled task для
  isolated checkout;
- `examples/maintenance/systemd/changerail-maintenance.service` и
  `examples/maintenance/systemd/changerail-maintenance.timer` - local POSIX
  scheduler.

Default scheduler authority остается read-only. Любой write follow-up требует
отдельной явной authority и не наследуется от audit job.

Если команда не может заменить существующий реальный каталог или файл, агент
должен остановиться и показать конфликт. Типовые конфликты:

- `.claude/skills` уже является реальным каталогом с project-specific skills;
- `.claude/commands/changerail` содержит ручную копию старых команд;
- `.claude/commands/chrl` содержит ручную копию старых команд;
- `.codex/skills/<skill>` является локальной копией, а не symlink-ом;
- `bin/openspec` уже используется проектом для другого wrapper-а.

### Consumer lock и POSIX repair

Для нового POSIX consumer default bootstrap создает absolute symlink wiring и
`openspec/changerail-consumer-lock.json` с `advisory` enforcement. Strict CI
consumer должен выбрать `--lock-enforcement strict`. Lock генерируется только
из clean tracked ChangeRail checkout с semantic `VERSION`, exact Git revision и
public remote без credentials; machine-local source root не записывается.

Existing lockless consumers продолжают проходить legacy verification, но
обычный `--refresh-wiring` без `openspec/changerail-consumer-lock.json`
остается fail-closed. Плановая migration использует отдельный explicit
adoption flow: сначала dry-run показывает inventory только allowlisted
ChangeRail-owned wiring, затем apply создает consumer lock и добавляет только
missing owned helpers через доказанный backend/path mode.

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project \
  --changerail-root /opt/changerail \
  --configure-existing --adopt-lockless-wiring --dry-run --skip-verify
/opt/changerail/bin/bootstrap-project /opt/example-project \
  --changerail-root /opt/changerail \
  --configure-existing --adopt-lockless-wiring
/opt/changerail/bin/verify-project /opt/example-project
```

POSIX adoption принимает только symlink-и, которые resolve under одного
выбранного ChangeRail checkout и используют один path mode. Dangling links,
mixed roots, mixed absolute/relative targets, regular files, undeclared
destinations, scope escapes и unrelated Git dirty state блокируют migration до
первой мутации. Native Windows generated-copy adoption требует existing
`openspec/changerail-wiring.json` ownership metadata; Windows symlink fallback
требует explicit proof, а junction inference без достаточного proof не
принимается.

Rollback boundary после successful adoption ограничен созданными tracked
ChangeRail-owned файлами: `openspec/changerail-consumer-lock.json`, при
generated-copy/fallback wiring также `openspec/changerail-wiring.json`, и
missing helper/surface artifacts, перечисленными в dry-run как `add`.
Project-owned `AGENTS.md`, `.codex/config.toml`, `.mcp.json`, auth files,
application source, board cards и unrelated Git state не входят в migration
scope и не должны меняться adoption flow.

После adoption повторный запуск explicit adoption идемпотентен и переходит к
lock-owned repair. Для обычного обновления уже adopted consumer используйте:

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project \
  --changerail-root /opt/changerail \
  --refresh-wiring --skip-verify
/opt/changerail/bin/verify-project /opt/example-project
```

Advisory source drift дает visible diagnostic; strict drift и любое broken
wiring блокируют verifier.
`--refresh-wiring` не обновляет `openspec/changerail-consumer-lock.json` на
новую ChangeRail revision: он требует, чтобы lock уже совпадал с активным
checkout. Если consumer lock указывает на старую revision, используйте
checkout этой revision для lock-owned repair или заводите отдельную explicit
migration, которая принимает новую ChangeRail revision в lock.

### Pinned consumer CI

Для нового consumer GitHub Actions workflow создается только explicit opt-in:

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project \
  --profile generic \
  --lock-enforcement strict \
  --with-ci
```

Workflow получает только `contents: read`, читает exact revision из strict
lock, устанавливает ChangeRail в runner temporary directory, repair-ит только
lock-owned wiring и запускает static verifier/OpenSpec baseline. Он не запускает
delivery, не требует Codex auth и не публикует изменения.

Для другого CI provider сохраните тот же нейтральный sequence: schema/strict
lock preflight, получение exact public revision, detached checkout в disposable
path, `bootstrap-project --refresh-wiring --skip-verify`, `verify-project`,
`bin/openspec validate --all --strict` и `git diff --check`. Недоступный revision,
malformed/advisory lock или project-owned wiring conflict должны завершать job
до verification.

## Native Windows Consumer

Для native Windows default не используйте symlink или junction wiring как
обычный путь. Для нового пустого consumer project запускайте
`bootstrap-project.cmd`; он выбирает generated-copy wiring, копирует
project-local `.cmd` helpers и записывает ownership manifest в
`openspec/changerail-wiring.json`:

```bat
set CHANGERAIL_ROOT=C:\opt\changerail
set PROJECT=C:\opt\example-project
"%CHANGERAIL_ROOT%\bin\bootstrap-project.cmd" "%PROJECT%" --name example-project --kind generic
"%CHANGERAIL_ROOT%\bin\verify-project.cmd" "%PROJECT%"
```

После обновления ChangeRail refresh должен менять только lock-owned
generated-owned artifacts и не трогать project-owned files:

```bat
"%CHANGERAIL_ROOT%\bin\bootstrap-project.cmd" "%PROJECT%" --refresh-wiring --skip-verify
"%CHANGERAIL_ROOT%\bin\verify-project.cmd" "%PROJECT%"
```

Минимальные prerequisites для native Windows verification: Git for Windows,
Python `3.11+` with `requirements-runtime.txt`, `cmd.exe`, and Node/npm/npx for
OpenSpec launch and MCP npm integrity verification. Если `verify-project.cmd`
сообщает missing `jsonschema` или `markdown_it`, выполните install в выбранный
Python runtime;
если он сообщает missing `npm`, сначала установите supported Node/npm toolchain
и rerun verification. Full Windows support claim требует passing live matrix или
tracked explicit blocker в ChangeRail compatibility notes.

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
нуждается еще и в effective Codex auth source и trusted automation authority.
При default запуске tracked `<workspace>/.codex/config.toml` должен содержать
`approval_policy = "never"` и `sandbox_mode = "danger-full-access"`; при
explicit `CODEX_HOME` эти значения проверяются в его `config.toml`. Иначе
runner preflight останавливается до запуска child. Это относится к single-card
команде `changerail-delivery-runner run` и к plan-oriented командам
`preflight-plan`, `run-plan` и `resume-plan`: без auth preflight должен
остановиться fail-closed до запуска delivery child.

Для queue plans plan runner запускает ChangeRail single-card runner, а single-card runner запускает Codex.
Примечание: consumer repository не обязан иметь tracked `bin/codex`. Supported path - запускать
`/opt/changerail/bin/changerail-delivery-runner` из ChangeRail checkout или
передать явный supported launcher через `--launcher`. `CODEX_WORKDIR` и
effective `CODEX_HOME` задаются для каждого child workspace.

Runner выбирает auth location так:

- если оператор явно задал `CODEX_HOME`, используется этот operator-owned
  каталог без generated reconciliation;
- иначе effective mutable `CODEX_HOME` равен ignored
  `<workspace>/.runtime/changerail/codex-home`, где `workspace` - consumer
  repository из `--workspace` или текущий git-root;
- default runtime config содержит exact absolute workspace trust, а project
  policy и MCP settings остаются в tracked `<workspace>/.codex/config.toml`;
- auth считается готовым, если есть supported marker вроде `auth.json` или
  `auth.toml` внутри project `.codex/`, который runner подключает symlink-ом в
  default runtime home, либо задана supported auth environment variable.

Project-local marker должен оставаться ignored local state. В generated
`.gitignore` для consumer проекта есть `.codex/auth.json` и
`.codex/auth.toml`; не добавляйте эти файлы в tracked payload, не публикуйте их
в docs, status или logs и не копируйте credentials автоматически во время
adoption. Runner также не копирует marker contents: он создаёт только ignored
symlink в своём runtime home. После preflight `git status --short` должен
оставаться clean; появление `.runtime/` в payload означает неверную ignore
policy и блокирует запуск.

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
  --profile generic \
  --link-codex-auth "$HOME/.codex/auth.json"
```

Если source auth file отсутствует, bootstrap должен остановиться без создания
dangling auth marker. Default bootstrap не создает `.codex/auth.json` или
`.codex/auth.toml`.

Для уже созданного consumer используйте idempotent configure path. Placeholder
`AUTH_JSON` в verifier output оператор заменяет локальным путем; helper не
читает credential contents и не печатает source path:

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project \
  --configure-existing \
  --link-codex-auth "$HOME/.codex/auth.json"
```

Real file, undeclared/dangling link, symlink parent или unrelated Git dirty
state считаются owner conflict: helper останавливается и ничего не заменяет.

### README и локальный Git для greenfield

Минимальный public-safe `README.md` создается только через `--with-readme` и
никогда не заменяет существующий README. `--init-git` инициализирует только
локальный repository; `--default-branch` и `--remote` требуют этот opt-in.
Helper не выполняет `git add`, commit, push и не создает remote repository:

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project \
  --profile service \
  --with-readme \
  --init-git --default-branch main \
  --remote https://github.com/example/consumer.git
```

Remote URL проходит preflight до создания target; credentials, query и
fragment запрещены, а URL не выводится в plan или completion output.

Новые проекты получают `--profile generic`, `--surfaces all-surfaces` и
`--codex-policy safe-interactive` по умолчанию. Это означает
`approval_policy = "on-request"` и `sandbox_mode = "workspace-write"`.
Automation, которой действительно нужен unattended full access, должна явно
передать `--codex-policy trusted-automation`; bootstrap зафиксирует этот выбор
в tracked config. `--kind` остается только compatibility alias для
`--profile`, а конфликт двух флагов останавливает bootstrap до записи target.

Если auth должен жить вне проекта, запускайте runner с explicit `CODEX_HOME`:

```bash
CODEX_HOME="$HOME/.codex" /opt/changerail/bin/changerail-delivery-runner preflight \
  openspec/board/3.inprogress/example-card.md \
  --workspace /opt/example-project --json
```

## Static verification и runtime evidence

Default `verify-project` проверяет tracked config, trust declaration, MCP
scope, wiring и instruction budget статически; этот PASS не является proof
effective Codex process state. Generated `.codex/config.toml` задает
`project_doc_max_bytes = 32768`. Размер `AGENTS.md` считается в UTF-8 bytes:
ниже 85% - PASS, от 85% до limit - non-blocking warning, выше limit - blocking
failure. Для legacy consumer без key временно действует тот же compatibility
default.

Greenfield bootstrap использует более строгий generation target: новый
`AGENTS.md` должен занимать менее 70% limit. Оставшиеся 30% резервируются для
project-specific правил и будущих shared upgrades; повышать limit вместо
сокращения дублирующих инструкций не является default remediation.

### Audit `AGENTS.md` после ChangeRail upgrade

Если новая версия ChangeRail меняет `AGENTS.shared.md`, maintainer обязан
провести review `AGENTS.md` во всех consumer-проектах, а не только проверить
source checkout. Для каждого consumer:

1. Найдите marker-блок `CHANGERAIL_SHARED_AGENTS_BEGIN/END` и замените только
   его body текущим `/opt/changerail/AGENTS.shared.md`, сохранив project-specific
   prefix без blind overwrite.
2. Проверьте локальную часть на duplicated shared workflow, stale authority,
   устаревшие verification commands, private paths и domain rules, ошибочно
   попавшие в generic section.
3. Выполните `wc -c AGENTS.md` и стремитесь держать итог ниже 70% от
   `project_doc_max_bytes`; диапазон 70–85% требует явного owner review, а 85%+
   уже дает verifier diagnostic.
4. Запустите `/opt/changerail/bin/verify-project <project>` и локальный
   verification baseline проекта, затем review diff перед commit.

Workspace inventory с private consumer paths должен оставаться ignored. В
публичных docs и reports фиксируйте только aggregate counts и generic examples.

Runtime evidence запускается только opt-in и только с project-local
`CODEX_HOME`:

```bash
CODEX_HOME=/opt/example-project/.codex \
  /opt/changerail/bin/verify-project /opt/example-project \
  --runtime-diagnostics
```

Адаптер поддерживает `codex-cli 0.147.x`, `doctor --json` schema version 1 и
structured `debug prompt-input`. Другие version/schema получают
unsupported/invalid, не runtime PASS. Raw doctor/prompt output остается только
в ignored `.runtime/changerail/diagnostics/`; в card, report или docs допустим
лишь allowlisted redacted summary без credential values и absolute local paths.

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
symlink-и в указанном runtime или project `.codex/` layer перед `run-plan` или
`resume-plan`. Не добавляйте absolute `[projects."..."]` вручную в tracked
project config: default runner создаёт exact trust только в ignored runtime
home.

## Проверка

Минимальный gate после migration:

```bash
/opt/changerail/bin/verify-project /opt/example-project
git -C /opt/example-project diff --check
git -C /opt/example-project status --short
```

`verify-project` проверяет:

- symlink-и `.claude`, `.codex/skills` и `bin/`;
- generated-owned native Windows wiring and `.cmd` helper copies when the
  project uses generated-copy backend;
- `.mcp.json` и `.codex/config.toml`;
- `openspec/config.yaml` и `bin/openspec validate --all --strict`;
- MCP npm pins through a real `npm view` integrity lookup unless a deterministic
  smoke fixture is being used;
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
