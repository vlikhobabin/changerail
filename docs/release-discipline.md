# Release Discipline

ChangeRail использует semver и changelog, чтобы consumer projects могли осознанно
обновлять `/opt/changerail`, а maintainers могли отличать compatible updates от
breaking changes.

## Version Source

Текущая версия ChangeRail хранится в root file:

```text
VERSION
```

Формат строго `MAJOR.MINOR.PATCH`.

Текущая подготовленная версия:

```text
0.5.0
```

До `1.0.0` ChangeRail остается pre-stable. Это значит:

- patch release исправляет документацию, smoke checks или мелкие defects без
  изменения публичных contracts;
- minor release может добавлять или менять workflow contracts, но все breaking
  changes должны быть явно отмечены в changelog и migration guide;
- major release до `1.0.0` не используется.

После `1.0.0` правила становятся обычными:

- `PATCH` - compatible fixes;
- `MINOR` - compatible additions;
- `MAJOR` - breaking changes.

## Changelog

Root `CHANGELOG.md` является публичным журналом изменений. Каждая версия должна
содержать разделы:

- `Added`
- `Changed`
- `Fixed`
- `Breaking`

Любое breaking change должно иметь строку с префиксом:

```text
BREAKING:
```

Breaking change для ChangeRail - это изменение, которое требует действий от
consumer project или меняет публичный workflow contract:

- behavior skills или Claude command wrappers;
- OpenSpec lifecycle expectations;
- schemas under `schemas/`;
- bootstrap templates;
- `bin/bootstrap-project`, `bin/verify-project`, `bin/openspec`;
- drift, wiring, review или publish gates;
- required ignore/runtime policy.

## Compatibility

Compatibility source of truth живет в [compatibility notes](compatibility.md).
Перед release maintainer проверяет, что notes покрывают:

- Codex CLI;
- Claude Code;
- OpenSpec CLI.
- automatically executed MCP npm package pins.
- native Windows `.cmd`/generated-copy support claims and any live host
  blockers.

OpenSpec CLI compatibility должна явно ссылаться на pin в `bin/openspec`.
MCP npm packages должны быть exact-version pinned в tracked config/templates и
описаны в `mcp-npm-lock.json` с integrity metadata. `verify-project` сверяет
tracked integrity с `npm view <package>@<version> dist.integrity --json`, поэтому
release gate должен выполняться в trusted environment с доступом к npm registry.

## Migration

Migration source of truth живет в [migration guide](migration-guide.md).
Перед release maintainer добавляет запись для перехода:

```text
<previous-version> -> <next-version>
```

Если update не требует действий от consumer projects, запись все равно нужна и
должна сказать, какие verification gates достаточно запустить.
Если update меняет workflow contract, lifecycle skill behavior, review/publish
gate или autonomous agent policy, migration notes обязательны даже когда
symlink-based consumer projects не меняют tracked files. Такая запись должна
назвать session restart, verification commands и refresh steps для проектов,
которые держат локальные копии skills или runbooks.

## First Stable Release Scope

Первый stable release строится только из чистого reviewed generic core на
точной опубликованной базе `origin/main`. Наличие локальной ветки, worktree,
forensic commit или ignored evidence не включает payload в release candidate.
Dirty, rejected и явно deferred work может войти только отдельной scoped
карточкой после собственных verification и fresh independent review.

Полный final baseline запускается в изолированном clone exact candidate,
который содержит только release-reachable refs. Обычный linked worktree делит
локальный ref graph с исходным repository и не является достаточным
доказательством bounded history scan: локальные forensic/deferred refs не
должны ни расширять, ни ослаблять проверку истории будущего release tag.

Machine-local inventory веток/worktree хранится только под ignored
`.runtime/changerail/release-scope/`. Реальные локальные пути, частные имена
веток и содержимое dirty worktree не переносятся в tracked release docs.

Phase-routed delivery и runtime artifact retention отложены и не блокируют
первый stable release. После green baseline version/changelog, compatibility,
migration, tag и distribution metadata готовит отдельная critical
final-certification карточка; scope-normalization change не публикует release
самостоятельно.

## Release Checklist

Перед публикацией release maintainer должен:

1. Обновить `VERSION`.
2. Перенести entries из `Unreleased` в новый version section в `CHANGELOG.md`.
3. Добавить `BREAKING:` entries при изменении публичного contract.
4. Обновить compatibility notes.
5. Обновить migration guide.
6. Запустить Linux-focused core release baseline.
7. Отдельно запустить обязательную extended regression suite и проверить
   exact CI inventory contract.
8. Запустить дополнительные trusted-network checks, если release меняет
   executable dependency pins.
9. Проверить, что [security policy](../SECURITY.md) существует, связан из
   публичных docs и не содержит private contact details или local paths.
10. Выполнить independent review gate перед publish.

Для pre-stable bootstrap releases факт выхода релиза публикуется reviewed
payload-ом с обновленными `VERSION`, `CHANGELOG.md`, compatibility notes и
migration guide. Git tag и packaged distribution metadata остаются отдельным
release step, когда проект явно включает tag-based публикацию.

Для executable supply-chain updates maintainer также обновляет tracked pins:

```bash
npm view @modelcontextprotocol/server-filesystem version dist.integrity --json
npm view @upstash/context7-mcp@2.1.6 version dist.integrity --json
npm view @playwright/mcp@0.0.68 version dist.integrity --json
npm view chrome-devtools-mcp@0.20.3 version dist.integrity --json
git ls-remote https://github.com/actions/checkout.git refs/tags/v4
git ls-remote https://github.com/actions/setup-node.git refs/tags/v4
```

После обновления нужно проверить, что `.mcp.json`, `.codex/config.toml`,
`templates/project/*`, `mcp-npm-lock.json`, `.github/workflows/changerail-ci.yml`
и `scripts/smoke-release-ci.py` согласованы.
Approved optional browser MCP pins are allowed in consumer-local config only:
they must be present in `mcp-npm-lock.json`, covered by `verify-project` smoke
fixtures and absent from root ChangeRail config and default project templates.
Любой upgrade optional browser MCP package остается отдельной release-задачей с
явным review of exact version and SRI metadata.

Для MCP npm pins также нужно выполнить trusted setup check:

```bash
/opt/changerail/bin/verify-project /opt/example-project
npm view @modelcontextprotocol/server-filesystem@2026.7.10 dist.integrity --json
npm view @upstash/context7-mcp@2.1.6 dist.integrity --json
npm view @playwright/mcp@0.0.68 dist.integrity --json
npm view chrome-devtools-mcp@0.20.3 dist.integrity --json
```

`scripts/smoke-verify-project.py` проверяет tampered-integrity fixture через
локальный fake `npm view`, а реальные registry lookups остаются частью
operator/release verification перед publish.

Schema coverage в release и project verification включает все публичные
contract schemas:

```text
schemas/changerail-review-verdict.schema.json
schemas/changerail-review-preflight-result.schema.json
schemas/changerail-review-cycle-history.schema.json
schemas/changerail-delivery-manifest.schema.json
schemas/changerail-delivery-run.schema.json
schemas/changerail-evidence-index.schema.json
```

Локальный release baseline:

```bash
python3 -m venv .runtime/changerail/ci-venv
.runtime/changerail/ci-venv/bin/python -m pip install \
  --disable-pip-version-check -r requirements-dev.txt
python3 scripts/run-release-baseline.py
python3 scripts/run-release-baseline.py --suite extended
```

Default command воспроизводит Linux-focused `core` admission: OpenSpec и config
validation, syntax/lint, bounded public-history regression, public-surface,
wiring/bootstrap/consumer-CI, generated drift и repository-integrity checks.
Exact отдельная команда `python3 scripts/run-release-baseline.py --suite
extended` выполняет heavy review/delivery/maintenance regressions. One-command
delivery regression `python3 scripts/smoke-delivery-runner.py` принадлежит
только `extended`, выполняется там ровно один раз и MUST NOT входить в default
core. `--list` показывает exact ordered inventory выбранной suite; combined
`all` route отсутствует. Raw runtime reports остаются under `.runtime/` and are
not committed.

Windows entrypoint, wiring Git-safety и aggregate matrix остаются retained
opt-in diagnostics вне обеих release suites. Их отсутствие не блокирует
текущий Linux-focused release claim.

Native Windows release claims require one of two reviewed outcomes: a passing
`python3 scripts/smoke-windows-matrix.py --live --inventory
internal/windows-lab-inventory.json --json` run, or an explicit blocker in
compatibility notes that names only generic host ids, sanitized dependency
state and ignored evidence paths. Missing Python runtime modules, missing npm or
missing npx are host prerequisites, not a full support pass. Будущая native
Windows claim также требует обе release suites и current/history public-surface
scans; до такой fresh proof текущая claim остаётся Linux-focused, а missing
Windows evidence не блокирует её публикацию.

## CI Gate

Tracked CI workflows:

```text
.github/workflows/changerail-ci.yml
.github/workflows/changerail-extended.yml
```

Push/pull-request route выполняет ровно
`python3 scripts/run-release-baseline.py`. Scheduled/manual route выполняет
ровно `python3 scripts/run-release-baseline.py --suite extended`. Оба pinned
checkout запрашивают `fetch-depth: 0`.

Local CI contract smoke:

```bash
python3 scripts/smoke-release-ci.py
```

`scripts/smoke-release-ci.py` сравнивает оба `--list` с exact ordered 22-item
core и 12-item extended inventories, требует uniqueness/disjointness, проверяет
negative missing/extra/duplicate/overlap cases и fail closed при drift любого
workflow route. Windows diagnostics не входят ни в один inventory.

CI drift checks must use generated fixtures under `.runtime/` and must not use
private workspace inventory.
Direct `scripts/smoke-drift.py` usage is inventory-driven: pass `--config`,
`--workspace-root` or `--project`. No-argument invocation is expected to fail.

## Update Ritual For Consumers

Consumer project, который получает ChangeRail через `/opt/changerail`, должен обновляться
явно:

1. Перейти в `/opt/changerail`.
2. Проверить `CHANGELOG.md`, `docs/compatibility.md` и
   `docs/migration-guide.md`.
3. Обновить checkout на нужный commit или tag.
4. Запустить project-local verification:

```bash
/opt/changerail/bin/verify-project /opt/example-project
```

5. Для workspace-level проверки запустить drift gate с operator inventory,
   который хранится вне public repo, например в ignored `internal/`.

Rollback остается git-level операцией: вернуть `/opt/changerail` на предыдущий
commit/tag и повторить verification.
