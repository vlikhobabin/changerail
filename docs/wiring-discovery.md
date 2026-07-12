# ChangeRail wiring discovery

Статус: рабочий контракт для ChangeRail skills, OpenSpec lifecycle skills и Claude
command wrappers.

Этот документ фиксирует, как проекты видят ChangeRail skills и Claude command
wrappers, и какой smoke подтверждает discovery. ChangeRail остается source of truth в
`/opt/changerail`; проекты-потребители не копируют весь репозиторий.

## Область

Проверяемая поверхность:

- Codex skills: `changerail-*` и `openspec-*`;
- Claude skills: те же каталоги через `.claude/skills`;
- Claude commands: `/changerail:explore`, `/changerail:ff`, `/changerail:do`,
  `/changerail:review`, `/changerail:pub`, `/changerail:deliver`;
- helper wrappers: `bin/openspec`, `bin/changerail-review-verdict`.

Smoke проверяет discovery wiring, а не полный runtime-flow этих команд.

## Repo-local wiring

Сам репозиторий ChangeRail использует относительные symlink-и, которые остаются
внутри `/opt/changerail` и не указывают на другой workspace:

```text
.claude/skills             -> ../skills
.claude/commands/changerail      -> ../../claude/commands/changerail
.codex/skills/changerail-explore -> ../../skills/changerail-explore
.codex/skills/changerail-ff      -> ../../skills/changerail-ff
.codex/skills/changerail-do      -> ../../skills/changerail-do
.codex/skills/changerail-review  -> ../../skills/changerail-review
.codex/skills/changerail-pub     -> ../../skills/changerail-pub
.codex/skills/changerail-deliver -> ../../skills/changerail-deliver
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
.codex/skills/changerail-explore -> /opt/changerail/skills/changerail-explore
.codex/skills/changerail-ff      -> /opt/changerail/skills/changerail-ff
.codex/skills/changerail-do      -> /opt/changerail/skills/changerail-do
.codex/skills/changerail-review  -> /opt/changerail/skills/changerail-review
.codex/skills/changerail-pub     -> /opt/changerail/skills/changerail-pub
.codex/skills/changerail-deliver -> /opt/changerail/skills/changerail-deliver
.codex/skills/openspec-*   -> /opt/changerail/skills/openspec-*
bin/openspec               -> /opt/changerail/bin/openspec
bin/changerail-review-verdict    -> /opt/changerail/bin/changerail-review-verdict
```

Для Codex допустимы generated copies под `.codex/skills/changerail-*`, если symlink
discovery у конкретной версии CLI сломан или запрещен политикой проекта. Такие
copies должны генерироваться из `/opt/changerail/skills/changerail-*` и проверяться drift
gate; Codex runtime state под `.codex/` не коммитится.

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
- wrappers `/changerail:explore`, `/changerail:ff`, `/changerail:do`, `/changerail:review`,
  `/changerail:pub` and `/changerail:deliver` mention the expected skill names;
- wrappers do not reference a consumer-root `skills/` path.

Codex checks:

- `.codex/skills/changerail-*` resolves to ChangeRail `skills/changerail-*`;
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
