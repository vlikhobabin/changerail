# Runbook maintenance-операций

Этот runbook описывает безопасный lifecycle maintenance для consumer
repositories. Он рассчитан на оператора или агента, который уже подключил
ChangeRail wiring и хочет регулярно проверять repository knowledge, доводить
finding-и до карточек и сохранять evidence без неявной публикации.

Основной reference по JSON contracts находится в
[ChangeRail contracts](changerail-contracts.md). Подключение существующего
проекта описано отдельно в
[runbook подключения существующего проекта](consumer-adoption-runbook.md).

## Safety Boundary

Maintenance surface по умолчанию read-only:

- `validate-catalog`, `render-index --check`, `scan`, `report`, `triage`,
  `feedback`, `quality`, `cards` без `--write` не меняют tracked files;
- runtime evidence, reports, previews, locks и state живут ниже ignored
  `.runtime/changerail/maintenance/`;
- maintenance-команды не дают authority на commit, push, issue comments, pull
  requests, external API mutations или публикацию карточек вне явного
  ChangeRail publish flow.

Write operations всегда требуют отдельного флага и остаются локальными:

- `render-index --write` обновляет только configured generated index;
- `report --write-state` обновляет только ignored lifecycle state;
- `accept-baseline --write` обновляет только
  `.changerail/maintenance-baseline.yaml`;
- `cards --write` создает или обновляет tracked board cards с
  `Maintenance Origin: <sha256 fingerprint>`.

Даже после `cards --write` оператор отдельно ревьюит diff и запускает обычный
delivery/publication workflow. Maintenance не коммитит и не пушит.

## Prerequisites

Новый пустой consumer можно создать сразу с maintenance opt-in:

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project \
  --name example-project \
  --kind generic \
  --with-maintenance
```

Для существующего consumer сначала выполните обычный adoption из
[consumer adoption runbook](consumer-adoption-runbook.md). Затем добавьте
tracked policy/catalog и helper wiring:

```bash
cd /opt/example-project
mkdir -p .changerail bin
ln -sfnT /opt/changerail/bin/changerail-maintenance bin/changerail-maintenance
ln -sfnT /opt/changerail/bin/changerail-maintenance-runner bin/changerail-maintenance-runner
```

Минимальные tracked файлы opt-in:

```text
.changerail/knowledge.yaml
.changerail/maintenance.yaml
.changerail/KNOWLEDGE.md
bin/changerail-maintenance
bin/changerail-maintenance-runner
```

Шаблоны для новых проектов лежат в `templates/project/.changerail/`. Для живого
проекта переносите records в catalog вручную: не заменяйте существующие
проектные правила blind overwrite-ом.

Native Windows использует generated-copy wiring и `.cmd` helpers:

```bat
set CHANGERAIL_ROOT=C:\opt\changerail
set PROJECT=C:\opt\example-project
"%CHANGERAIL_ROOT%\bin\bootstrap-project.cmd" "%PROJECT%" --name example-project --kind generic --with-maintenance
"%PROJECT%\bin\changerail-maintenance.cmd" validate-catalog --json
"%PROJECT%\bin\changerail-maintenance-runner.cmd" scan --timeout 900 --json
```

Windows-примеры выше используют только wrappers, которые есть в `bin/*.cmd`.

## Catalog And Policy

Catalog описывает поддерживаемые knowledge artifacts:

```bash
cd /opt/example-project
bin/changerail-maintenance validate-catalog --json
```

Default paths:

```text
.changerail/knowledge.yaml
.changerail/maintenance.yaml
```

Catalog records должны покрывать active instructions, runbooks, architecture
docs, generated indexes и важные project-specific references. Policy задает
scan universe через `include_globs`, `exclude_globs`, optional
`active_scope_globs`, enabled detectors и fail threshold.

Используйте только repository-relative paths. Absolute paths, traversal и root
escape отклоняются fail-closed и не восстанавливаются из prose.

## Generated Index

Generated index является deterministic Markdown-представлением catalog. Новый
bootstrap с `--with-maintenance` пишет его на первом запуске.

Read-only drift check:

```bash
bin/changerail-maintenance render-index --check --json
```

Explicit local update:

```bash
bin/changerail-maintenance render-index --write --json
```

Коммитьте `.changerail/KNOWLEDGE.md` только после review generated diff.

## First Scan

После появления catalog и policy запустите первый green scan:

```bash
bin/changerail-maintenance scan --json
```

Ожидаемое green-состояние:

- команда завершается с exit code `0`;
- output schema равен `changerail.maintenance-scan-report.v1`;
- `complete` равен `true`;
- enabled detectors не имеют blocker/major findings на configured `fail_on`
  threshold;
- `configuration_diagnostics` пустой.

Exit code `1` означает complete report с findings на threshold или выше. Exit
code `2` означает invalid configuration или input failure; такой output нельзя
использовать как green evidence.

## Lifecycle Report And State

Lifecycle report нормализует scan findings в stable identities:

```bash
bin/changerail-maintenance report --json
```

Report содержит stable `fingerprint`, отдельный `evidence_fingerprint`,
status, owner/risk поля при наличии и sanitized evidence references. Без
restored state значение `first_seen` берется из текущего observation time, а
continuity явно помечается как `not_restored`.

State persistence всегда explicit и ignored:

```bash
bin/changerail-maintenance report --json --write-state
```

Default state path:

```text
.runtime/changerail/maintenance/state.json
```

Custom `--state` должен оставаться ниже `.runtime/changerail/maintenance/`.
Tracked state paths отклоняются.

## Baseline And Waivers

Baseline позволяет оператору принять known findings или задать temporary
waivers:

```bash
bin/changerail-maintenance accept-baseline --json
```

Default preview mode пишет только ignored runtime previews и structured
summary. Explicit write обновляет tracked baseline:

```bash
bin/changerail-maintenance accept-baseline \
  --owner example-team \
  --reason "accepted starter backlog" \
  --write \
  --json
```

Tracked path:

```text
.changerail/maintenance-baseline.yaml
```

Waivers используйте для temporary suppressions с `owner`, `reason` и
`expires_at` или `review_after`. Expired waivers не скрывают current findings.

## Audit And Triage

Для recurring deterministic audit используйте bounded runner:

```bash
bin/changerail-maintenance-runner scan --timeout 900 --json
```

Runner сохраняет status ниже:

```text
.runtime/changerail/maintenance/runs/<run-id>/status.json
```

Для agent-assisted triage передайте schema-valid annotations или child command,
stdout которого является `changerail.maintenance-triage.v1`:

```bash
bin/changerail-maintenance-runner triage \
  --annotations .runtime/changerail/maintenance/triage/example.json \
  --json
```

Runner валидирует structured JSON. Human prose, logs или partial diagnostics
недостаточны для success.

## Card Handoff

Сначала посмотрите card preview:

```bash
bin/changerail-maintenance cards --json
```

Пишите tracked backlog cards только после review preview:

```bash
bin/changerail-maintenance cards --write --json
```

Каждая written card содержит точный origin marker:

```text
Maintenance Origin: <sha256 fingerprint>
```

Bridge сканирует все board lanes и обновляет существующую карточку с тем же
origin вместо создания duplicate. Raw detector output остается в ignored
runtime evidence; card text содержит sanitized repository-relative metadata.

## Scheduler Examples

Public scheduler examples находятся в `examples/maintenance/`:

- [GitHub Actions read-only audit](../examples/maintenance/github-actions-readonly.yml):
  scheduled/default-branch audit с `contents: read` и uploaded runtime
  evidence.
- [Separated CI jobs](../examples/maintenance/ci-readonly-vs-write.yml):
  read-only analysis отделен от любого будущего write-capable workflow.
- [Codex scheduled task](../examples/maintenance/codex-scheduled-task.md):
  local или hosted scheduled task для isolated checkout.
- [systemd service](../examples/maintenance/systemd/changerail-maintenance.service)
  и [timer](../examples/maintenance/systemd/changerail-maintenance.timer):
  local POSIX scheduler для dedicated checkout.

Scheduler prerequisites:

- consumer checkout уже имеет ChangeRail helper wiring;
- `.changerail/knowledge.yaml` и `.changerail/maintenance.yaml` tracked;
- `.runtime/changerail/maintenance/` ignored;
- read-only scheduled jobs не получают commit, push, comment, pull-request или
  external API mutation credentials.

Любой write-capable follow-up должен быть отдельным explicit workflow с
отдельной authority и human-reviewed scope.

## Feedback

Feedback normalization преобразует explicit records в один
`changerail.maintenance-detector-result.v1` document:

```bash
bin/changerail-maintenance feedback \
  --adapter-id lifecycle \
  --review-history .runtime/changerail/reviews/history.json \
  --json

bin/changerail-maintenance feedback \
  --adapter-id delivery \
  --delivery-run .runtime/changerail/delivery-runs/example/status.json \
  --json

bin/changerail-maintenance feedback \
  --adapter-id external \
  --detector-result .runtime/changerail/maintenance/external/result.json \
  --json
```

Supported inputs:

- schema-valid `changerail.review-cycle-history.v1` review history;
- schema-valid blocked `changerail.delivery-run.v1` terminal records со
  structured `terminal_reason`;
- schema-valid external `changerail.maintenance-detector-result.v1` producer
  records.

Invalid, unsafe или unsupported inputs fail closed. Команда не выводит findings
из prose logs, review comments или unstructured diagnostics. Adapter boundary
явный: external producers проходят через detector-result schema и те же
safe-path checks, что core detectors.

## Quality Rollup

Quality rollup read-only и поддерживает text, JSON и CSV views:

```bash
bin/changerail-maintenance quality \
  --report .runtime/changerail/maintenance/report-latest.json

bin/changerail-maintenance quality \
  --report .runtime/changerail/maintenance/report-latest.json \
  --history .runtime/changerail/maintenance/report-earlier.json \
  --triage .runtime/changerail/maintenance/triage/example.json \
  --proposal .runtime/changerail/maintenance/proposals/example.json \
  --json

bin/changerail-maintenance quality \
  --report .runtime/changerail/maintenance/report-latest.json \
  --csv
```

JSON output schema:

```text
changerail.maintenance-quality-rollup.v1
```

Proposal decision evidence schema:

```text
changerail.maintenance-proposal-decision.v1
```

Metrics имеют status `known` только когда рассчитаны из complete schema-valid
inputs. Missing optional producer evidence, incomplete history или invalid
records превращаются в `unknown` metrics и/или diagnostics; helper не
придумывает temporary thresholds и не выводит quality из prose. Proposal
decisions являются quality observations, а не publication authority.

## Final Consumer Gate

После maintenance adoption или изменения maintenance docs/config запустите:

```bash
bin/changerail-maintenance validate-catalog --json
bin/changerail-maintenance render-index --check --json
bin/changerail-maintenance scan --json
bin/verify-project .
git diff --check
```

Maintainers ChangeRail при изменении public source of truth дополнительно
запускают release/public-surface gate из `README.md` или
`docs/release-discipline.md`.
