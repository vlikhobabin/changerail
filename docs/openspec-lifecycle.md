# OpenSpec lifecycle source

Статус: рабочий контракт для `openspec-*` skills и wrapper `bin/openspec`.

## Область

ChangeRail поставляет OpenSpec lifecycle surface как часть общего source of truth:

- `skills/openspec-apply-change/`
- `skills/openspec-archive-change/`
- `skills/openspec-bulk-archive-change/`
- `skills/openspec-continue-change/`
- `skills/openspec-explore/`
- `skills/openspec-ff-change/`
- `skills/openspec-new-change/`
- `skills/openspec-onboard/`
- `skills/openspec-propose/`
- `skills/openspec-sync-specs/`
- `skills/openspec-verify-change/`
- `bin/openspec`

Эти файлы нужны lifecycle skills ChangeRail: `changerail-ff` и `changerail-do` используют
OpenSpec actions для proposal/spec/tasks, apply, verify, sync и archive.

## Source And License

Текущая версия `skills/openspec-*` синхронизирована с generated OpenSpec skill
surface для OpenSpec CLI `1.3.1`.

Frontmatter каждого импортированного skill сохраняет provenance:

```yaml
license: MIT
compatibility: Requires openspec CLI.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "1.3.1"
```

Политика синка: обновление этих skills выполняется отдельным ChangeRail change,
который фиксирует новую версию CLI, проверяет diff generated text, обновляет
эту страницу и запускает repository verification baseline.

## CLI Wrapper

`bin/openspec` запускает pinned OpenSpec CLI:

```bash
/opt/changerail/bin/openspec --version
```

Default pin:

```text
@fission-ai/openspec@1.3.1
```

Для контролируемой локальной проверки можно временно переопределить версию:

```bash
OPENSPEC_VERSION=1.3.1 /opt/changerail/bin/openspec validate --all
```

Wrapper выключает telemetry по умолчанию через `OPENSPEC_TELEMETRY=0`, если
operator явно не задал другое значение.

## Consumer Wiring

Consumer project может подключать `openspec-*` skills так же, как `changerail-*`:

```text
.claude/skills              -> /opt/changerail/skills
.codex/skills/openspec-*    -> /opt/changerail/skills/openspec-*
bin/openspec                -> /opt/changerail/bin/openspec
```

OpenSpec artifacts (`openspec/board`, `openspec/changes`, `openspec/specs`) при
этом остаются в consumer repository.

## Verification

Минимальная проверка после обновления OpenSpec lifecycle surface:

```bash
/opt/changerail/bin/openspec --version
/opt/changerail/bin/openspec validate --all --strict
git diff --check
```

Если изменение затрагивает generated skill source, дополнительно сравните
frontmatter `generatedBy` с pin версии CLI и проверьте public-surface scan на
machine-local paths.
