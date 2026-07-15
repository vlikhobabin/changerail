# ChangeRail contracts

Статус: рабочий контракт для review, delivery и evidence handoff.

## Namespace

Новые публичные wire contracts ChangeRail используют namespace `changerail.*`:

- `changerail.review-verdict.v1`
- `changerail.delivery-manifest.v1`
- `changerail.evidence-index.v1`
- `changerail.delivery-run.v1`
- `changerail.delivery-plan.v1`
- `changerail.delivery-plan-status.v1`
- `changerail.review-cycle-history.v1`

Schemas находятся в `schemas/`:

```text
schemas/changerail-review-verdict.schema.json
schemas/changerail-delivery-manifest.schema.json
schemas/changerail-evidence-index.schema.json
schemas/changerail-delivery-run.schema.json
schemas/changerail-delivery-plan.schema.json
schemas/changerail-delivery-plan-status.schema.json
schemas/changerail-review-cycle-history.schema.json
```

Review verdict-файлы и public schemas должны использовать только
`changerail.review-verdict.v1`; helper отклоняет другие schema ids.
`verify-project` и release checks покрывают полный набор schemas выше.

Runtime helpers валидируют указанные документы по tracked Draft 2020-12 schemas
с проверкой `format`, `additionalProperties`, conditional required fields и
nested types до применения semantic checks ChangeRail. Любая ошибка schema
validation дает fail-closed non-zero результат со structured diagnostic.

## Review Verdict

Review verdict является runtime-файлом:

```text
.runtime/changerail/reviews/<card-id>.json
```

Он не коммитится. Publish gate принимает только verdict, который:

- валиден по shape и cross-field правилам;
- имеет `result: go`;
- содержит `reviewer.independence` attestation с `fresh_context: true`,
  `did_not_plan_or_implement: true` и непустым `basis`;
- fresh относительно текущего `HEAD`, `git status --porcelain`,
  `git diff HEAD --no-color` и содержимого untracked non-ignored файлов,
  перечисленных через `git ls-files --others --exclude-standard`.

Helper:

```bash
python3 scripts/changerail_review_verdict.py fingerprint --workspace .
python3 scripts/changerail_review_verdict.py validate \
  ".runtime/changerail/reviews/<card-id>.json" --check-fresh --workspace . --json
```

Validation сначала применяет `schemas/changerail-review-verdict.schema.json`,
затем проверяет verdict semantics: согласованность `go`, reviewer independence
и optional freshness.

Consumer project может вызывать helper через wrapper:

```bash
bin/changerail-review-verdict fingerprint --workspace .
bin/changerail-review-verdict validate \
  ".runtime/changerail/reviews/<card-id>.json" --check-fresh --workspace . --json
```

Exit codes: `0` valid, `1` validation failed, `2` input error.

Ignored paths не входят в freshness fingerprint. Поэтому запись verdict под
`.runtime/changerail/reviews/` не инвалидирует сам verdict, но изменение содержимого
нового untracked deliverable-файла делает verdict stale.

Independence attestation является проверяемым контрактом и операторским
заявлением reviewer-а. Helper проверяет наличие и истинность полей, но не может
криптографически доказать личность reviewer-а или полную изоляцию памяти за
пределами freshness fingerprint.

## Delivery Manifest

Delivery manifest является runtime-файлом:

```text
.runtime/changerail/delivery-manifests/<card-id>.json
```

Он описывает card-owned scope: planned changes, committable paths, excluded
runtime paths, preexisting dirty state и publish handoff details. Publish
использует manifest как initial staging proposal, но обязан повторно сверить
его с `git status` и не stage-ить runtime files.

`workspace.repository` является sanitized identity. Helper удаляет URL
userinfo, passwords, query string и fragment из remote URLs; для SCP-style SSH
remotes сохраняет host/repository path без raw SSH username. Manifest не должен
содержать credentials, access tokens или private operator identity из remote
URL.

Helper может вывести или обновить manifest из текущей карточки и workspace
state:

```bash
python3 scripts/changerail_delivery_manifest.py derive \
  openspec/board/3.inprogress/example.md --write --json
python3 scripts/changerail_delivery_manifest.py staging-plan \
  .runtime/changerail/delivery-manifests/example.json --json
```

Validation сначала применяет `schemas/changerail-delivery-manifest.schema.json`,
затем проверяет manifest-specific semantic invariants.

`committable_paths` может фиксировать `operation`: `add`, `modify`, `delete`,
`rename` или `unknown`. Для удаления manifest сохраняет удаленный
`source_path`; для rename - `source_path` и `target_path`, чтобы staging
proposal включал оба пути board move или другого card-owned перемещения.
Отсутствующая операция означает legacy entry и требует сверки с `git status`.

Manifest derivation использует NUL-delimited git status data и записывает
точные repository-relative paths без shell quoting artifacts. Paths со spaces,
quotes, Unicode или literal ` -> ` text должны попадать в manifest как реальные
repository paths. Paths с valid non-UTF-8 bytes сохраняются через
`surrogateescape` round-trip и записываются в JSON в escaped форме, чтобы
manifest оставался valid UTF-8 file и `os.fsencode` восстанавливал исходные
path bytes. Untracked directories разворачиваются до точных non-ignored file
paths; directory-wide untracked path отклоняется до попадания в staging
proposal.

После publish ignored manifest можно обновить без staging runtime state:

```bash
python3 scripts/changerail_delivery_manifest.py publish-update \
  .runtime/changerail/delivery-manifests/example.json \
  --status pushed --commit <commit> --remote origin --branch main \
  --pushed-at <utc> --mode review-gated
```

## Evidence Index

Evidence index описывает retained evidence для verification/review handoff.
Evidence может быть committable, runtime или external, но committed artifact не
должен содержать secrets, credentials, customer data, local traces или большие
сырые логи.

## Delivery Run Record

Delivery run record является runtime-файлом:

```text
.runtime/changerail/delivery-runs/<run-id>/status.json
```

Schema id: `changerail.delivery-run.v1`. Record содержит card, phase, terminal
`result`, timestamps, command metadata, commit при доступном git `HEAD`,
preflight checks, log paths и token usage, когда provider output позволяет его
прочитать. Если usage недоступен, record обязан явно писать
`usage.available: false`.

Обязательный минимум status record остается стабильным: `schema`, `run_id`,
`updated_at`, `workspace`, `card`, `phase`, `result`, `timestamps`, `command` и
`usage`. Поле `performance` optional и best-effort: runner пишет его только для
измерений, которые может наблюдать из structured child JSONL, review history,
git status или publish metadata. Отсутствующее optional timing значение означает
`unknown`, а не `0`.

`performance` может содержать:

- `wall_time_seconds`;
- `event_counts` и `agent_message_count`;
- `command_execution_count`, `commands` и `slowest_commands` с
  runner-observed `started_at`, `ended_at` и `duration_seconds`;
- `file_change_count`;
- `timeline` с bounded runner-observed событиями;
- `review.cycle_count`, `review.first_review_latency_seconds`,
  `review.time_to_final_go_seconds` и per-cycle timing;
- `publish.latency_seconds` и `publish.pushed_at`, когда publish metadata
  доступна.

`usage` всегда содержит `available`. Когда provider output позволяет, runner
может дополнительно писать `input_tokens`, `cached_input_tokens`,
`uncached_input_tokens`, `output_tokens`, `reasoning_tokens` и `total_tokens`.
Если explicit `total_tokens` отсутствует, metrics может вычислять display-only
total как `input_tokens + output_tokens`, не меняя runtime record.

Tracked runner:

```bash
bin/changerail-delivery-runner preflight openspec/board/3.inprogress/example.md \
  --connectivity-url https://example.invalid/health --json
bin/changerail-delivery-runner run openspec/board/3.inprogress/example.md \
  --model gpt-5 --reasoning-effort medium
```

Runner запускает `codex exec` через repo launcher `bin/codex`, закрывает stdin
child-процесса, выполняет child в effective workspace и экспортирует
`CODEX_WORKDIR=<workspace>`. Если `--workspace` не указан, workspace
резолвится в git-root invocation cwd, а вне git - в текущий cwd. Если
`CODEX_HOME` не задан, runner использует `<workspace>/.codex`; если
`--runtime-root` не задан, status пишется под
`<workspace>/.runtime/changerail/delivery-runs/`. Preflight записывает диагностику
launcher, Codex binary, auth state, `config.toml`, stale symlink-ов в
`CODEX_HOME`, permissions и optional connectivity URL. Connectivity diagnostics
записывают только sanitized endpoint metadata, status или exception class; raw
URL, query values и raw exception text не являются частью structured status.
Child stdout/stderr logs остаются raw ignored runtime evidence и не должны
публиковаться как public artifacts. `DELIVERED`, `NO-GO` и
`BLOCKED` являются терминальными outcome для supervisor-а и печатаются в stdout
runner-а. Structured JSONL events вроде `external-review/no-go` дают `NO-GO`,
а `awaiting-review` дает `BLOCKED`; supervisor не должен выводить outcome из
свободного текста лога. Эти structured events являются preferred source of
truth; если их нет, fallback по `exit_code == 0` допустим только после проверки,
что нет structured review-gated blocking evidence. Для текущей card runner
проверяет canonical verdict
`.runtime/changerail/reviews/<card-id>.json`: свежий unpublished `result: no-go`
дает terminal outcome `NO-GO`, а stale/invalid unpublished verdict блокирует
успешный fallback как `BLOCKED`. Игнорируемый stale verdict сам по себе не
переопределяет успешный fallback, если card уже опубликована и находится под
`openspec/board/4.done`.

## Delivery Plan

Delivery plan является consumer-owned JSON-файлом:

```text
delivery-plan.json
```

Schema id: `changerail.delivery-plan.v1`. Plan описывает bounded queue через
workspace aliases, consumer-root-relative workspace paths, card ids, card
filenames или board paths, dependencies, waves, `max_parallel`,
`per_workspace_parallelism` и optional per-card model/reasoning overrides.
Required format is JSON, чтобы core runner не получал обязательную YAML
dependency. YAML может быть добавлен позднее только как optional extension.

Plan-файл является public-safe input contract. Он не должен содержать
credentials, secrets, raw remotes, auth state, `.runtime/` state или
machine-specific absolute workspace paths. Public examples должны использовать
generic paths such as `/opt/example-a` only outside the plan itself; inside the
plan workspace paths are relative to an operator-supplied consumer root:

```json
{
  "schema": "changerail.delivery-plan.v1",
  "id": "example-plan",
  "max_parallel": 2,
  "per_workspace_parallelism": 1,
  "push_mode": "push",
  "workspaces": [
    {"alias": "service-a", "path": "service-a"},
    {"alias": "service-b", "path": "service-b"}
  ],
  "waves": [
    {"id": 1},
    {"id": 2, "depends_on": [1]}
  ],
  "cards": [
    {
      "id": "service-a-card",
      "workspace": "service-a",
      "card": "openspec/board/3.inprogress/service-a-card.md",
      "wave": 1
    },
    {
      "id": "service-b-card",
      "workspace": "service-b",
      "card": "service-b-card.md",
      "depends_on": ["service-a-card"],
      "wave": 2
    }
  ]
}
```

Schema validation checks shape and public-safe path fields. Runner semantic
validation must additionally fail closed on cycles, duplicate aliases or card
ids, missing workspaces/cards/dependencies, invalid wave/dependency relations
and incompatible concurrency settings before the first live child launch.

## Delivery Plan Status

Delivery plan status является ignored runtime-файлом:

```text
.runtime/changerail/delivery-plans/<run-id>/status.json
```

Schema id: `changerail.delivery-plan-status.v1`. Status содержит plan id,
plan fingerprint, phase, aggregate result, terminal outcome, push/no-push mode,
resolved workspace/card state, preflight checks, locks, summary counts and
references to each child card's `changerail.delivery-run.v1` status record.

Queue status does not replace child delivery run records. Every live card still
uses the existing single-card runner and keeps its own
`.runtime/changerail/delivery-runs/<run-id>/status.json`. Queue status stores
references such as child run ids and status paths; raw stdout/stderr logs stay
ignored runtime evidence and are not embedded in aggregate status.

Tracked queue runner commands:

```bash
bin/changerail-delivery-runner plan delivery-plan.json --consumer-root /opt/example-workspace --json
bin/changerail-delivery-runner preflight-plan delivery-plan.json --consumer-root /opt/example-workspace --json
bin/changerail-delivery-runner run-plan delivery-plan.json --consumer-root /opt/example-workspace
bin/changerail-delivery-runner resume-plan delivery-plan.json --consumer-root /opt/example-workspace \
  --status-path /opt/example-workspace/.runtime/changerail/delivery-plans/<run-id>/status.json
bin/changerail-delivery-runner status-plan \
  /opt/example-workspace/.runtime/changerail/delivery-plans/<run-id>/status.json --json
```

`preflight-plan` fails closed before live launch on invalid schema,
cycle/duplicate/missing dependency, missing or ambiguous card, canceled card,
invalid wave relation, invalid concurrency or workspace readiness failure.
`run-plan` and `resume-plan` create ignored workspace locks, invoke the existing
single-card runner for each live card and update aggregate status without
scraping free-text logs. Locks that appear stale are diagnostic evidence only
and are not automatically removed.

## Review Cycle History

Latest canonical verdict остается:

```text
.runtime/changerail/reviews/<card-id>.json
```

Review-cycle history является дополнительным runtime evidence:

```text
.runtime/changerail/reviews/<card-id>.history.json
```

Schema id: `changerail.review-cycle-history.v1`. History сохраняет summaries по
cycles: result, counts by finding severity, acceptance outcomes, immutable
finding details или snapshot path для конкретного цикла и путь к canonical
verdict. Publish продолжает проверять только latest canonical
`changerail.review-verdict.v1`; metrics могут читать history, чтобы не терять
предыдущий `no-go`.

Metrics helper:

```bash
bin/changerail-delivery-metrics
bin/changerail-delivery-metrics --csv
```

Он читает structured run records и review-cycle history, печатает per-run и
aggregate metrics, а отсутствующие optional fields выводит как `unknown`.

## Public Safety

Contracts are public source. Примеры должны использовать только generic пути
вроде `/opt/changerail` и `/opt/example-project`. Runtime payloads, verdicts,
manifests и local evidence остаются ignored state.
