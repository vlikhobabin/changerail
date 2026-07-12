# ChangeRail wiring discovery

Статус: рабочий контракт для ChangeRail skills, OpenSpec lifecycle skills и Claude
command wrappers.

Этот документ фиксирует, как проекты видят ChangeRail skills и Claude command
wrappers, и какой smoke подтверждает discovery. ChangeRail остается source of truth в
`/opt/changerail`; проекты-потребители не копируют весь репозиторий.

## Область

Проверяемая поверхность:

- Codex skills: `changerail-*`, short aliases `chrl-*` и `openspec-*`;
- Claude skills: те же каталоги через `.claude/skills`;
- Claude commands: `/changerail:explore`, `/changerail:ff`, `/changerail:do`,
  `/changerail:review`, `/changerail:pub`, `/changerail:deliver`;
- Claude short aliases: `/chrl:explore`, `/chrl:ff`, `/chrl:do`,
  `/chrl:review`, `/chrl:pub`, `/chrl:deliver`;
- helper wrappers: `bin/openspec`, `bin/changerail-review-verdict`.

Smoke проверяет discovery wiring, а не полный runtime-flow этих команд.

## Repo-local wiring

Сам репозиторий ChangeRail использует относительные symlink-и, которые остаются
внутри `/opt/changerail` и не указывают на другой workspace:

```text
.claude/skills             -> ../skills
.claude/commands/changerail      -> ../../claude/commands/changerail
.claude/commands/chrl      -> ../../claude/commands/chrl
.codex/skills/changerail-explore -> ../../skills/changerail-explore
.codex/skills/changerail-ff      -> ../../skills/changerail-ff
.codex/skills/changerail-do      -> ../../skills/changerail-do
.codex/skills/changerail-review  -> ../../skills/changerail-review
.codex/skills/changerail-pub     -> ../../skills/changerail-pub
.codex/skills/changerail-deliver -> ../../skills/changerail-deliver
.codex/skills/chrl-explore -> ../../skills/chrl-explore
.codex/skills/chrl-ff      -> ../../skills/chrl-ff
.codex/skills/chrl-do      -> ../../skills/chrl-do
.codex/skills/chrl-review  -> ../../skills/chrl-review
.codex/skills/chrl-pub     -> ../../skills/chrl-pub
.codex/skills/chrl-deliver -> ../../skills/chrl-deliver
.codex/skills/openspec-*   -> ../../skills/openspec-*
```

Такая форма нужна для dogfooding: Codex и Claude должны видеть тот же source
surface, который затем подключают потребители. `.claude/settings.local.json`,
`.codex/tmp/`, sessions, auth state и runtime reports не являются частью
wiring и не коммитятся.

## Consumer wiring

Потребительский проект подключает ChangeRail source of truth из своего репозитория:

```text
.claude/skills             -> /opt/changerail/skills
.claude/commands/changerail      -> /opt/changerail/claude/commands/changerail
.claude/commands/chrl      -> /opt/changerail/claude/commands/chrl
.codex/skills/changerail-explore -> /opt/changerail/skills/changerail-explore
.codex/skills/changerail-ff      -> /opt/changerail/skills/changerail-ff
.codex/skills/changerail-do      -> /opt/changerail/skills/changerail-do
.codex/skills/changerail-review  -> /opt/changerail/skills/changerail-review
.codex/skills/changerail-pub     -> /opt/changerail/skills/changerail-pub
.codex/skills/changerail-deliver -> /opt/changerail/skills/changerail-deliver
.codex/skills/chrl-explore -> /opt/changerail/skills/chrl-explore
.codex/skills/chrl-ff      -> /opt/changerail/skills/chrl-ff
.codex/skills/chrl-do      -> /opt/changerail/skills/chrl-do
.codex/skills/chrl-review  -> /opt/changerail/skills/chrl-review
.codex/skills/chrl-pub     -> /opt/changerail/skills/chrl-pub
.codex/skills/chrl-deliver -> /opt/changerail/skills/chrl-deliver
.codex/skills/openspec-*   -> /opt/changerail/skills/openspec-*
bin/openspec               -> /opt/changerail/bin/openspec
bin/changerail-review-verdict    -> /opt/changerail/bin/changerail-review-verdict
```

Для Codex допустимы generated copies под `.codex/skills/changerail-*` и
`.codex/skills/chrl-*`, если symlink discovery у конкретной версии CLI сломан
или запрещен политикой проекта. Такие copies должны генерироваться из
`/opt/changerail/skills/changerail-*` или `/opt/changerail/skills/chrl-*` и
проверяться drift gate; Codex runtime state под `.codex/` не коммитится.

## Smoke

Запуск из корня ChangeRail:

```bash
python3 scripts/smoke-wiring-discovery.py
```

По умолчанию smoke выполняет все проверки:

- `repo-local` + `claude`;
- `repo-local` + `codex`;
- `consumer-example` + `claude`;
- `consumer-example` + `codex`.

Consumer example создается во временном ignored-каталоге:

```text
.runtime/changerail/wiring-smoke/<run-id>/example-project
```

Report пишется рядом:

```text
.runtime/changerail/wiring-smoke/<run-id>/report.json
```

## Report contract

Schema id:

```text
changerail.wiring-discovery-smoke.v1
```

Report является aggregate-отчетом. Верхний уровень содержит:

- `schema`;
- `run_id`;
- `changerail_root`;
- `report_kind`: `aggregate`;
- `modes`;
- `surfaces`;
- `summary`;
- `runs[]`;
- `checks[]`.

Каждый `runs[]` entry содержит обязательную минимальную единицу smoke:

- `mode`: `repo-local` или `consumer-example`;
- `surface`: `claude` или `codex`;
- `checks[]`;
- `summary`.

Каждый `checks[]` entry содержит:

- `name`;
- `path`;
- `expected_target`;
- `resolved_target`;
- `status`: `pass` или `fail`;
- `message`;
- `mode`;
- `surface`.

## Pass criteria

Smoke считается успешным, когда все checks имеют `status: pass`.

Claude checks:

- `.claude/skills` resolves to ChangeRail `skills/`;
- `.claude/commands/changerail` resolves to ChangeRail `claude/commands/changerail`;
- `.claude/commands/chrl` resolves to ChangeRail `claude/commands/chrl`;
- wrappers `/changerail:explore`, `/changerail:ff`, `/changerail:do`, `/changerail:review`,
  `/changerail:pub` and `/changerail:deliver` mention the expected skill names;
- wrappers `/chrl:explore`, `/chrl:ff`, `/chrl:do`, `/chrl:review`,
  `/chrl:pub` and `/chrl:deliver` mention the expected short alias skill names
  and their canonical `/changerail:*` forms;
- wrappers do not reference a consumer-root `skills/` path.

Codex checks:

- `.codex/skills/changerail-*` resolves to ChangeRail `skills/changerail-*`;
- `.codex/skills/chrl-*` resolves to ChangeRail `skills/chrl-*`;
- `.codex/skills/openspec-*` resolves to ChangeRail `skills/openspec-*`;
- each discovered `SKILL.md` has frontmatter `name` matching the skill
  directory.

Repo-local checks additionally require relative symlink targets. Consumer
checks may use absolute `/opt/changerail` symlink targets because `/opt/changerail` is the
documented contract path.

## Public safety

Committable wiring artifacts are limited to this document, the smoke script and
public-safe relative symlink-и in the ChangeRail repo. Runtime reports under
`.runtime/` remain ignored. Do not commit private project names, customer data,
secrets, local traces, screenshots, databases, auth state or machine-specific
workspace paths.
