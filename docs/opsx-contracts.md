# OPSX contracts

Статус: рабочий контракт для review, delivery и evidence handoff.

## Namespace

Новые публичные wire contracts OPSX используют namespace `opsx.*`:

- `opsx.review-verdict.v1`
- `opsx.delivery-manifest.v1`
- `opsx.evidence-index.v1`
- `opsx.delivery-run.v1`
- `opsx.review-cycle-history.v1`

Schemas находятся в `schemas/`:

```text
schemas/opsx-review-verdict.schema.json
schemas/opsx-delivery-manifest.schema.json
schemas/opsx-evidence-index.schema.json
schemas/opsx-delivery-run.schema.json
schemas/opsx-review-cycle-history.schema.json
```

Review verdict-файлы и public schemas должны использовать только
`opsx.review-verdict.v1`; helper отклоняет другие schema ids.

## Review Verdict

Review verdict является runtime-файлом:

```text
.runtime/opsx/reviews/<card-id>.json
```

Он не коммитится. Publish gate принимает только verdict, который:

- валиден по shape и cross-field правилам;
- имеет `result: go`;
- fresh относительно текущего `HEAD`, `git status --porcelain`,
  `git diff HEAD --no-color` и содержимого untracked non-ignored файлов,
  перечисленных через `git ls-files --others --exclude-standard`.

Helper:

```bash
python3 scripts/opsx_review_verdict.py fingerprint --workspace .
python3 scripts/opsx_review_verdict.py validate \
  ".runtime/opsx/reviews/<card-id>.json" --check-fresh --workspace . --json
```

Consumer project может вызывать helper через wrapper:

```bash
bin/opsx-review-verdict fingerprint --workspace .
bin/opsx-review-verdict validate \
  ".runtime/opsx/reviews/<card-id>.json" --check-fresh --workspace . --json
```

Exit codes: `0` valid, `1` validation failed, `2` input error.

Ignored paths не входят в freshness fingerprint. Поэтому запись verdict под
`.runtime/opsx/reviews/` не инвалидирует сам verdict, но изменение содержимого
нового untracked deliverable-файла делает verdict stale.

## Delivery Manifest

Delivery manifest является runtime-файлом:

```text
.runtime/opsx/delivery-manifests/<card-id>.json
```

Он описывает card-owned scope: planned changes, committable paths, excluded
runtime paths, preexisting dirty state и publish handoff details. Publish
использует manifest как initial staging proposal, но обязан повторно сверить
его с `git status` и не stage-ить runtime files.

`committable_paths` может фиксировать `operation`: `add`, `modify`, `delete`,
`rename` или `unknown`. Для удаления manifest сохраняет удаленный
`source_path`; для rename - `source_path` и `target_path`, чтобы staging
proposal включал оба пути board move или другого card-owned перемещения.
Отсутствующая операция означает legacy entry и требует сверки с `git status`.

## Evidence Index

Evidence index описывает retained evidence для verification/review handoff.
Evidence может быть committable, runtime или external, но committed artifact не
должен содержать secrets, credentials, customer data, local traces или большие
сырые логи.

## Delivery Run Record

Delivery run record является runtime-файлом:

```text
.runtime/opsx/delivery-runs/<run-id>/status.json
```

Schema id: `opsx.delivery-run.v1`. Record содержит card, phase, terminal
`result`, timestamps, command metadata, commit при доступном git `HEAD`,
preflight checks, log paths и token usage, когда provider output позволяет его
прочитать. Если usage недоступен, record обязан явно писать
`usage.available: false`.

Tracked runner:

```bash
bin/opsx-delivery-runner preflight openspec/board/3.inprogress/example.md \
  --connectivity-url https://example.invalid/health --json
bin/opsx-delivery-runner run openspec/board/3.inprogress/example.md \
  --model gpt-5 --reasoning-effort medium
```

Runner запускает `codex exec` через repo launcher `bin/codex`, закрывает stdin
child-процесса, выполняет child в effective workspace и экспортирует
`CODEX_WORKDIR=<workspace>`. Если `--workspace` не указан, workspace
резолвится в git-root invocation cwd, а вне git - в текущий cwd. Если
`CODEX_HOME` не задан, runner использует `<workspace>/.codex`; если
`--runtime-root` не задан, status пишется под
`<workspace>/.runtime/opsx/delivery-runs/`. Preflight записывает диагностику
launcher, Codex binary, auth state, `config.toml`, stale symlink-ов в
`CODEX_HOME`, permissions и optional connectivity URL. `DELIVERED`, `NO-GO` и
`BLOCKED` являются терминальными outcome для supervisor-а и печатаются в stdout
runner-а. Structured JSONL events вроде `external-review/no-go` дают `NO-GO`,
а `awaiting-review` дает `BLOCKED`; supervisor не должен выводить outcome из
свободного текста лога.

## Review Cycle History

Latest canonical verdict остается:

```text
.runtime/opsx/reviews/<card-id>.json
```

Review-cycle history является дополнительным runtime evidence:

```text
.runtime/opsx/reviews/<card-id>.history.json
```

Schema id: `opsx.review-cycle-history.v1`. History сохраняет summaries по
cycles: result, counts by finding severity, acceptance outcomes, immutable
finding details или snapshot path для конкретного цикла и путь к canonical
verdict. Publish продолжает проверять только latest canonical
`opsx.review-verdict.v1`; metrics могут читать history, чтобы не терять
предыдущий `no-go`.

Metrics helper:

```bash
bin/opsx-delivery-metrics
bin/opsx-delivery-metrics --csv
```

Он читает structured run records и review-cycle history, печатает per-run и
aggregate metrics, а отсутствующие optional fields выводит как `unknown`.

## Public Safety

Contracts are public source. Примеры должны использовать только generic пути
вроде `/opt/opsx` и `/opt/example-project`. Runtime payloads, verdicts,
manifests и local evidence остаются ignored state.
