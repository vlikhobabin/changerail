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
  `/changerail:review`, `/changerail:pub`, `/changerail:deliver`,
  `/changerail:maintain`;
- Claude short aliases: `/chrl:explore`, `/chrl:ff`, `/chrl:do`,
  `/chrl:review`, `/chrl:pub`, `/chrl:deliver`, `/chrl:maintain`;
- default helper wrappers: `bin/openspec`, `bin/changerail-python`,
  `bin/changerail-review-verdict` and `bin/changerail-evidence`;
- maintenance opt-in helper wrappers: `bin/changerail-maintenance` and
  `bin/changerail-maintenance-runner`, wired only by
  `bin/bootstrap-project --with-maintenance` or an equivalent manual adoption.

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
.codex/skills/changerail-maintain -> ../../skills/changerail-maintain
.codex/skills/chrl-explore -> ../../skills/chrl-explore
.codex/skills/chrl-ff      -> ../../skills/chrl-ff
.codex/skills/chrl-do      -> ../../skills/chrl-do
.codex/skills/chrl-review  -> ../../skills/chrl-review
.codex/skills/chrl-pub     -> ../../skills/chrl-pub
.codex/skills/chrl-deliver -> ../../skills/chrl-deliver
.codex/skills/chrl-maintain -> ../../skills/chrl-maintain
.codex/skills/openspec-*   -> ../../skills/openspec-*
```

Такая форма нужна для dogfooding: Codex и Claude должны видеть тот же source
surface, который затем подключают потребители. `.claude/settings.local.json`,
`.codex/tmp/`, sessions, auth state и runtime reports не являются частью
wiring и не коммитятся.

## Consumer wiring

### POSIX consumer wiring

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
.codex/skills/changerail-maintain -> /opt/changerail/skills/changerail-maintain
.codex/skills/chrl-explore -> /opt/changerail/skills/chrl-explore
.codex/skills/chrl-ff      -> /opt/changerail/skills/chrl-ff
.codex/skills/chrl-do      -> /opt/changerail/skills/chrl-do
.codex/skills/chrl-review  -> /opt/changerail/skills/chrl-review
.codex/skills/chrl-pub     -> /opt/changerail/skills/chrl-pub
.codex/skills/chrl-deliver -> /opt/changerail/skills/chrl-deliver
.codex/skills/chrl-maintain -> /opt/changerail/skills/chrl-maintain
.codex/skills/openspec-*   -> /opt/changerail/skills/openspec-*
bin/openspec                    -> /opt/changerail/bin/openspec
bin/changerail-python           -> /opt/changerail/bin/changerail-python
bin/bootstrap-project           -> /opt/changerail/bin/bootstrap-project
bin/verify-project              -> /opt/changerail/bin/verify-project
bin/changerail-review-verdict   -> /opt/changerail/bin/changerail-review-verdict
bin/changerail-evidence         -> /opt/changerail/bin/changerail-evidence
```

Greenfield POSIX bootstrap по умолчанию создает absolute symlink targets и
tracked `openspec/changerail-consumer-lock.json`. Lock хранит только canonical
public source, version/revision, relative artifact inventory и выбранный
`path_mode`; resolved machine root в него не попадает. Для workspace, который
перемещает ChangeRail и consumer одним деревом, нужен explicit
`--wiring-path-mode relative`.

`--lock-enforcement advisory` оставляет source revision drift non-blocking,
`strict` делает его blocking, а broken/missing symlink остается blocking в обоих
режимах. `--lock-enforcement none` предназначен для explicit development
fixtures и сохраняет lockless compatibility. Lock-owned POSIX wiring можно
repair-ить командой:

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project \
  --changerail-root /opt/changerail \
  --refresh-wiring --skip-verify
```

Refresh не меняет lock, требует совпадающий revision и отказывается заменять
real files/directories, проходить через symlink parent, выходить из project
scope или работать при unrelated Git dirty state.

Для уже подключенного consumer repair можно объединить с ignored auth-link в
bounded configure mode без повторного template rendering:

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project \
  --changerail-root /opt/changerail \
  --configure-existing --refresh-wiring \
  --link-codex-auth AUTH_JSON
```

Все actions проходят preflight до первой мутации. Повторный запуск подтверждает
уже совпадающие symlink-и; project-owned destinations и undeclared links не
заменяются.

При opt-in maintenance (`bin/bootstrap-project --with-maintenance` или
эквивалентная ручная migration) дополнительно появляются:

```text
.changerail/knowledge.yaml
.changerail/maintenance.yaml
bin/changerail-maintenance        -> /opt/changerail/bin/changerail-maintenance
bin/changerail-maintenance-runner -> /opt/changerail/bin/changerail-maintenance-runner
```

Для Codex допустимы generated copies под `.codex/skills/changerail-*` и
`.codex/skills/chrl-*`, если symlink discovery у конкретной версии CLI сломан
или запрещен политикой проекта. Такие copies должны генерироваться из
`/opt/changerail/skills/changerail-*` или `/opt/changerail/skills/chrl-*` и
проверяться drift gate; Codex runtime state под `.codex/` не коммитится.

### Native Windows generated wiring

Native Windows default использует generated project-local copies для command,
skill и helper wiring вместо symlink или junction default. Bootstrap выбирает
этот backend по platform policy, а POSIX consumers продолжают использовать
существующий symlink wiring.

Windows generated wiring rules:

- `.cmd` entrypoints являются native Windows command default для helper
  invocation.
- Generated copies должны быть owned by manifest или tracked project policy,
  чтобы `verify-project` и drift gate могли отличать valid generated content от
  stale copy и project-owned divergence.
- Bootstrap records generated ownership in
  `openspec/changerail-wiring.json`. Each artifact entry uses project-relative
  `path`, `kind` (`file` or `directory`), ChangeRail-relative `source`,
  `digest` and `owner: generated`.
- `bin/bootstrap-project <project> --refresh-wiring` refreshes generated-owned
  artifacts from the ChangeRail source of truth and refuses project-owned
  divergence.
- Drift gate consumes `verify-project --json`; stale, missing or project-owned
  generated wiring is reported as `broken_wiring` with failed verifier check
  details and refresh remediation instead of being treated as current
  ChangeRail source wiring.
- Symlink mode допустим только после explicit operator opt-in and positive
  proof. On native Windows bootstrap can run a direct symlink probe; otherwise
  `--windows-fallback-proof <json>` must provide schema-valid source metadata
  and concrete per-check evidence for passed directory symlink, file symlink
  and privilege/Developer Mode capability checks. Status-only check lists are
  rejected.
- Junction mode допустим только как explicit compatibility fallback с
  link-aware cleanup и Git-safety evidence. `--windows-fallback-proof <json>`
  must provide schema-valid source metadata and concrete evidence for passed
  junction creation, cleanup, Git status, dry-run add and index-safety checks
  before the fallback can report success. Each Git check must explicitly report
  `safe: true` and `unsafe_paths: []`. Status-only or command-only check lists
  are rejected. Unsafe proof diagnostics summarize unsafe path classes without
  printing raw paths or credential-like values.
- Machine-local source roots, raw Windows lab reports, credentials and runtime
  state остаются ignored.

Native Windows smoke после реализации должен проверить generated-copy wiring,
`.cmd` launch, drift/refresh, cleanup, Git status/add/index behavior, paths со
spaces и non-ASCII, оба Windows lab hosts или explicit blocker/caveat.
The aggregate deterministic matrix runs through:

```bash
python3 scripts/smoke-windows-matrix.py --json
```

Live host execution remains explicit and uses ignored
`internal/windows-lab-inventory.json`; tracked summaries may mention only
`windows-host-a`, `windows-host-b`, command class, outcome and ignored evidence
paths. Deterministic local Git safety fixtures also remain available through:

```bash
python3 scripts/smoke-windows-wiring-git-safety.py
```

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

Каждый run также включает regression fixture для skill frontmatter, который
MUST отклонять некавыченый scalar с `: `.

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
- each discovered `SKILL.md` parses complete YAML frontmatter and has parsed
  `name` matching the skill directory.

Repo-local checks additionally require relative symlink targets. Consumer
checks may use absolute `/opt/changerail` symlink targets because `/opt/changerail` is the
documented contract path.

## Public safety

Committable wiring artifacts are limited to this document, the smoke script and
public-safe relative symlink-и in the ChangeRail repo. Runtime reports under
`.runtime/` remain ignored. Do not commit private project names, customer data,
secrets, local traces, screenshots, databases, auth state or machine-specific
workspace paths.
