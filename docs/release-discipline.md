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

Текущая начальная версия:

```text
0.1.0
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

## Release Checklist

Перед публикацией release maintainer должен:

1. Обновить `VERSION`.
2. Перенести entries из `Unreleased` в новый version section в `CHANGELOG.md`.
3. Добавить `BREAKING:` entries при изменении публичного contract.
4. Обновить compatibility notes.
5. Обновить migration guide.
6. Запустить OpenSpec validation и repository baseline checks.
7. Запустить release CI contract smoke.
8. Запустить smoke checks, которые относятся к измененной поверхности.
9. Проверить, что [security policy](../SECURITY.md) существует, связан из
   публичных docs и не содержит private contact details или local paths.
10. Выполнить independent review gate перед publish.

Для executable supply-chain updates maintainer также обновляет tracked pins:

```bash
npm view @modelcontextprotocol/server-filesystem version dist.integrity --json
npm view @upstash/context7-mcp@2.1.6 version dist.integrity --json
git ls-remote https://github.com/actions/checkout.git refs/tags/v4
git ls-remote https://github.com/actions/setup-node.git refs/tags/v4
```

После обновления нужно проверить, что `.mcp.json`, `.codex/config.toml`,
`templates/project/*`, `mcp-npm-lock.json`, `.github/workflows/changerail-ci.yml`
и `scripts/smoke-release-ci.py` согласованы.

Для MCP npm pins также нужно выполнить trusted setup check:

```bash
/opt/changerail/bin/verify-project /opt/example-project
npm view @modelcontextprotocol/server-filesystem@2026.7.10 dist.integrity --json
npm view @upstash/context7-mcp@2.1.6 dist.integrity --json
```

`scripts/smoke-verify-project.py` проверяет tampered-integrity fixture через
локальный fake `npm view`, а реальные registry lookups остаются частью
operator/release verification перед publish.

Schema coverage в release и project verification включает все публичные
contract schemas:

```text
schemas/changerail-review-verdict.schema.json
schemas/changerail-review-cycle-history.schema.json
schemas/changerail-delivery-manifest.schema.json
schemas/changerail-delivery-run.schema.json
schemas/changerail-evidence-index.schema.json
```

Минимальный локальный baseline:

```bash
openspec validate --all --strict
python3 scripts/smoke-release-ci.py
python3 scripts/public-surface-scan.py --self-test
python3 scripts/public-surface-scan.py
python3 scripts/public-surface-scan.py --history
python3 -m json.tool .mcp.json
python3 - <<'PY'
import tomllib
for path in (".codex/config.toml",):
    with open(path, "rb") as f:
        tomllib.load(f)
print("TOML_OK")
PY
git diff --check
```

## CI Gate

Tracked CI workflow:

```text
.github/workflows/changerail-ci.yml
```

Local CI contract smoke:

```bash
python3 scripts/smoke-release-ci.py
```

The CI workflow runs:

- `./bin/openspec validate --all --strict`;
- docs/config baseline checks from `AGENTS.md`;
- Python syntax checks for scripts and helper executables;
- `scripts/smoke-wiring-discovery.py`;
- `scripts/smoke-verify-project.py`;
- `scripts/smoke-bootstrap-project.py`;
- `scripts/smoke-drift.py` against a generated generic runtime project.

CI drift checks must use generated fixtures under `.runtime/` and must not use
private workspace inventory.

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
