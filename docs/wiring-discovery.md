# OPSX wiring discovery

Статус: рабочий контракт для минимальной поверхности `opsx-explore` и
`opsx-ff`.

Этот документ фиксирует, как проекты видят OPSX skills и Claude command
wrappers, и какой smoke подтверждает discovery. OPSX остается source of truth в
`/opt/opsx`; проекты-потребители не копируют весь репозиторий.

## Область

Проверяемая минимальная поверхность:

- Codex skills: `opsx-explore`, `opsx-ff`;
- Claude skills: те же каталоги через `.claude/skills`;
- Claude commands: `/opsx:explore`, `/opsx:ff`.

Smoke проверяет discovery wiring, а не полный runtime-flow этих команд.

## Repo-local wiring

Сам репозиторий OPSX использует относительные symlink-и, которые остаются
внутри `/opt/opsx` и не указывают на другой workspace:

```text
.claude/skills             -> ../skills
.claude/commands/opsx      -> ../../claude/commands/opsx
.codex/skills/opsx-explore -> ../../skills/opsx-explore
.codex/skills/opsx-ff      -> ../../skills/opsx-ff
```

Такая форма нужна для dogfooding: Codex и Claude должны видеть тот же source
surface, который затем подключают потребители. `.claude/settings.local.json`,
`.codex/tmp/`, sessions, auth state и runtime reports не являются частью
wiring и не коммитятся.

## Consumer wiring

Потребительский проект подключает OPSX source of truth из своего репозитория:

```text
.claude/skills             -> /opt/opsx/skills
.claude/commands/opsx      -> /opt/opsx/claude/commands/opsx
.codex/skills/opsx-explore -> /opt/opsx/skills/opsx-explore
.codex/skills/opsx-ff      -> /opt/opsx/skills/opsx-ff
```

Для Codex допустимы generated copies под `.codex/skills/opsx-*`, если symlink
discovery у конкретной версии CLI сломан или запрещен политикой проекта. Такие
copies должны генерироваться из `/opt/opsx/skills/opsx-*` и проверяться drift
gate; Codex runtime state под `.codex/` не коммитится.

## Smoke

Запуск из корня OPSX:

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
.runtime/opsx/wiring-smoke/<run-id>/example-project
```

Report пишется рядом:

```text
.runtime/opsx/wiring-smoke/<run-id>/report.json
```

## Report contract

Schema id:

```text
opsx.wiring-discovery-smoke.v1
```

Report является aggregate-отчетом. Верхний уровень содержит:

- `schema`;
- `run_id`;
- `opsx_root`;
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

- `.claude/skills` resolves to OPSX `skills/`;
- `.claude/commands/opsx` resolves to OPSX `claude/commands/opsx`;
- wrappers `/opsx:explore` and `/opsx:ff` mention the expected skill names;
- wrappers do not reference a consumer-root `skills/` path.

Codex checks:

- `.codex/skills/opsx-explore` resolves to OPSX `skills/opsx-explore`;
- `.codex/skills/opsx-ff` resolves to OPSX `skills/opsx-ff`;
- each discovered `SKILL.md` has frontmatter `name` matching the skill
  directory.

Repo-local checks additionally require relative symlink targets. Consumer
checks may use absolute `/opt/opsx` symlink targets because `/opt/opsx` is the
documented contract path.

## Public safety

Committable wiring artifacts are limited to this document, the smoke script and
public-safe relative symlink-и in the OPSX repo. Runtime reports under
`.runtime/` remain ignored. Do not commit private project names, customer data,
secrets, local traces, screenshots, databases, auth state or machine-specific
workspace paths.
