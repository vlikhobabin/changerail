# Release Discipline

OPSX использует semver и changelog, чтобы consumer projects могли осознанно
обновлять `/opt/opsx`, а maintainers могли отличать compatible updates от
breaking changes.

## Version Source

Текущая версия OPSX хранится в root file:

```text
VERSION
```

Формат строго `MAJOR.MINOR.PATCH`.

Текущая начальная версия:

```text
0.1.0
```

До `1.0.0` OPSX остается pre-stable. Это значит:

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

Breaking change для OPSX - это изменение, которое требует действий от
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

OpenSpec CLI compatibility должна явно ссылаться на pin в `bin/openspec`.

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
9. Выполнить independent review gate перед publish.

Минимальный локальный baseline:

```bash
openspec validate --all --strict
python3 scripts/smoke-release-ci.py
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
.github/workflows/opsx-ci.yml
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

Consumer project, который получает OPSX через `/opt/opsx`, должен обновляться
явно:

1. Перейти в `/opt/opsx`.
2. Проверить `CHANGELOG.md`, `docs/compatibility.md` и
   `docs/migration-guide.md`.
3. Обновить checkout на нужный commit или tag.
4. Запустить project-local verification:

```bash
/opt/opsx/bin/verify-project /opt/example-project
```

5. Для workspace-level проверки запустить drift gate с operator inventory,
   который хранится вне public repo, например в ignored `internal/`.

Rollback остается git-level операцией: вернуть `/opt/opsx` на предыдущий
commit/tag и повторить verification.
