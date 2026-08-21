# ChangeRail contracts

Статус: рабочий контракт для review, delivery, evidence и maintenance handoff.

## Namespace

Новые публичные wire contracts ChangeRail используют namespace `changerail.*`:

- `changerail.review-verdict.v1`
- `changerail.review-preflight-result.v1`
- `changerail.delivery-manifest.v1`
- `changerail.evidence-index.v1`
- `changerail.delivery-run.v1`
- `changerail.delivery-plan.v1`
- `changerail.delivery-plan-status.v1`
- `changerail.review-cycle-history.v1`
- `changerail.source-classification.v1`
- `changerail.consumer-lock.v1`
- `changerail.repository-knowledge.v1`
- `changerail.maintenance-policy.v1`
- `changerail.maintenance-scan-report.v1`
- `changerail.maintenance-detector-result.v1`
- `changerail.maintenance-report.v1`
- `changerail.maintenance-state.v1`
- `changerail.maintenance-baseline.v1`
- `changerail.maintenance-triage.v1`
- `changerail.maintenance-run.v1`
- `changerail.maintenance-quality-rollup.v1`
- `changerail.maintenance-proposal-decision.v1`

Schemas находятся в `schemas/`:

```text
schemas/changerail-review-verdict.schema.json
schemas/changerail-review-preflight-result.schema.json
schemas/changerail-delivery-manifest.schema.json
schemas/changerail-evidence-index.schema.json
schemas/changerail-delivery-run.schema.json
schemas/changerail-delivery-plan.schema.json
schemas/changerail-delivery-plan-status.schema.json
schemas/changerail-review-cycle-history.schema.json
schemas/changerail-source-classification.schema.json
schemas/changerail-consumer-lock.schema.json
schemas/changerail-repository-knowledge.schema.json
schemas/changerail-maintenance-policy.schema.json
schemas/changerail-maintenance-scan-report.schema.json
schemas/changerail-maintenance-detector-result.schema.json
schemas/changerail-maintenance-report.schema.json
schemas/changerail-maintenance-state.schema.json
schemas/changerail-maintenance-baseline.schema.json
schemas/changerail-maintenance-triage.schema.json
schemas/changerail-maintenance-run.schema.json
schemas/changerail-maintenance-quality-rollup.schema.json
schemas/changerail-maintenance-proposal-decision.schema.json
```

Review verdict-файлы и public schemas должны использовать только
`changerail.review-verdict.v1`; helper отклоняет другие schema ids.
`verify-project` и release checks покрывают полный набор schemas выше.

Runtime helpers валидируют указанные документы по tracked Draft 2020-12 schemas
с проверкой `format`, `additionalProperties`, conditional required fields и
nested types до применения semantic checks ChangeRail. Любая ошибка schema
validation дает fail-closed non-zero результат со structured diagnostic.

## Consumer Lock

Tracked `openspec/changerail-consumer-lock.json` фиксирует public-safe
ChangeRail `version`, exact Git `revision`, canonical HTTPS source, wiring
backend/path mode/artifact inventory, выбранные profiles и
`advisory|strict` enforcement. Schema `changerail.consumer-lock.v1` запрещает
absolute source paths, credential-bearing URI, incomplete revisions,
unsupported profiles и path traversal.

Lock не хранит resolved ChangeRail root. Для POSIX symlink wiring artifact
использует только project-relative `path` и ChangeRail-relative `source`.
`openspec/changerail-wiring.json` остается отдельным frozen ownership manifest
для generated Windows copies и не заменяется consumer lock.

## Review Preflight

Перед model payload review existing helper выполняет deterministic preflight:

```bash
bin/changerail-review-verdict preflight \
  openspec/board/3.inprogress/example.md --workspace . --normalize \
  --output .runtime/changerail/review-preflights/example.json --json
```

Результат `changerail.review-preflight-result.v1` содержит exact workspace
fingerprint, manifest/board/scope state, risk route, reasoning effort,
complexity guard и per-check outcomes. Safe normalization обновляет card/change
metadata и operation details только когда comparable path set не меняется;
missing/extra paths остаются blockers. `blocked` и
`investigation-required` не запускают LLM и не расходуют implementation review
budget. `machine-reviewed` является payload gate для явно deterministic/process
scope без added production code; `ready-for-llm-review` выбирает `high` для
ordinary или `xhigh` для critical review.

Опциональный tracked consumer-файл
`.changerail/source-classification.yaml` использует schema id
`changerail.source-classification.v1` и позволяет проекту объявить production
source kinds для domain-specific форматов без встраивания прикладных имен в
ChangeRail core:

```yaml
schema: changerail.source-classification.v1
source_kinds:
  - id: bsl
    suffixes: [".bsl"]
    production_roots: ["src/production"]
    measure: lines
  - id: designer-xml
    suffixes: [".xml"]
    production_roots: ["src/designer"]
    measure: xml-structure
```

Paths в файле являются repository-relative POSIX prefixes, не shell glob-ами.
Absolute paths, traversal, duplicate source-kind ids, unsafe roots или
schema-invalid values блокируют preflight до LLM review. Если файл отсутствует,
preflight использует прежний built-in classifier: common source suffixes и
executable helpers считаются production, а domain-specific `.bsl`/`.xml` не
становятся production по одному suffix.

`complexity_guard.source_breakdown` содержит bounded детализацию по kind:
`source_kind`, `measure_strategy`, counted `path_count`, `raw_added_lines`,
`effective_complexity`, `fallback`, bounded `paths` samples и при необходимости
excluded-path counters/notes. Raw source content, ignored runtime state и
private data в result не копируются.

Declared BSL использует `lines`: added `.bsl` lines под объявленными production
roots входят в `added_production_loc`. Built-in non-production path parts
`test`, `tests`, `fixtures`, `examples`, `schemas`, `templates`, `docs` и
`openspec` продолжают побеждать даже при широком production root.

Declared Designer XML использует `xml-structure`: helper считает effective
structural units по XML elements и non-empty scalar text values вместо
безусловного raw line count, когда XML можно измерить safely. Generic XML
schemas, templates, fixtures, examples, docs, OpenSpec files и unclassified
`.xml` не считаются production source. Для malformed или conservatively
unmeasurable classified XML preflight использует raw added lines как fallback
или блокирует gate; он не возвращает silent zero для classified production XML.

С флагом `--diagnostics` preflight добавляет public-safe timing breakdown:
fingerprint, OpenSpec validation, scoped whitespace check и public-surface scan.
Fingerprint diagnostics отдельно показывают changed-path discovery,
reviewed-tree construction, untracked content hashing, final assembly, cache
hit/miss и выбранный tree-builder mode. Эти данные не раскрывают raw repository
content и не меняют canonical freshness values.

Default complexity guard останавливает payload больше 300 production LOC и
новый authority/wire protocol. Bounded exception требует, чтобы successor
содержал только reference:

```json
{"authorization_card":"openspec/board/4.done/example-authorization.md","authorization_id":"example-authorization"}
```

Referenced `4.done` card должен быть unchanged tracked `HEAD` artifact и сам
содержать `Investigation authorization` JSON с exact investigation/successor
card/id, ceiling `301..500` и protocol allowance. Preflight также проверяет
`investigation Blocks successor`, `successor Depends On investigation` и
`authorization source Depends On investigation`; отсутствие или mismatch
остаётся `investigation-required`.
Relation принимает только exact bare id, `<id>.md` или canonical
`openspec/board/<lane>/<id>.md`; foreign stem и non-board path не совпадают.

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
- fresh относительно текущего `HEAD`, NUL-delimited Git status, tracked diff и
  содержимого untracked non-ignored файлов, перечисленных через
  `git ls-files --others --exclude-standard`;
- содержит `workspace.tree_sha` — Git tree SHA reviewed payload, который publish
  обязан сверить с tree создаваемого commit до stage/commit.

Helper:

```bash
bin/changerail-review-verdict fingerprint --workspace . --diagnostics
bin/changerail-review-verdict validate \
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
нового untracked deliverable-файла делает verdict stale и меняет reviewed tree.

Reviewed tree строится из `HEAD` плюс machine-readable changed-path set через
path-scoped temporary index, когда Git может представить текущие изменения
точно. Full-tree `git add -A` остается internal reference/fallback для unsafe
states и parity tests. Валидация verdict, deterministic preflight и publish
freshness используют одну canonical fingerprint implementation; ignored cache
under `.runtime/changerail/review-fingerprint-cache/` может переиспользоваться
только после проверки текущего `HEAD`, changed-path metadata, file content/mode
metadata и Git exclude-visible state.

Для unborn repository helper пишет `workspace.head_commit: "unborn"` и всё равно
вычисляет `workspace.tree_sha` через temporary Git index. Это позволяет review
связать initial reviewed payload с будущим first commit без выдуманного commit
SHA.

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
его с `git status` и не stage-ить runtime files. Manifest также является
ignored ledger для exact publication metadata: reviewed `payload_commit`,
final `published_commit`, remote, branch, status и timestamps.

`workspace.repository` является sanitized identity. Helper удаляет URL
userinfo, passwords, query string и fragment из remote URLs; для SCP-style SSH
remotes сохраняет host/repository path без raw SSH username. Manifest не должен
содержать credentials, access tokens или private operator identity из remote
URL.

Helper может вывести или обновить manifest из текущей карточки и workspace
state:

```bash
bin/changerail-delivery-manifest derive \
  openspec/board/3.inprogress/example.md --write --json
bin/changerail-delivery-manifest staging-plan \
  .runtime/changerail/delivery-manifests/example.json --json
bin/changerail-delivery-manifest scope-check \
  .runtime/changerail/delivery-manifests/example.json \
  --target working-tree --json
bin/changerail-delivery-manifest scope-check \
  .runtime/changerail/delivery-manifests/example.json \
  --target staged --json
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

`scope-check` сверяет заявленный manifest scope с фактическим Git scope
отдельно для working tree и staged index. Helper использует NUL-delimited Git
data и operation-aware сравнение для `add`, `modify`, `delete` и `rename`;
rename сравнивается по `source_path` и `target_path`, а не по human-readable
`old -> new` строке. JSON result содержит per-target `missing`, `extra` и
`mismatched` arrays; любой непустой список дает fail-closed non-zero exit.
Ignored runtime paths из manifest `excluded_runtime_paths` и Git ignored files
не считаются committable scope.

Перед staging publish должен проверить manifest against working tree:

```bash
bin/changerail-delivery-manifest scope-check \
  .runtime/changerail/delivery-manifests/example.json \
  --target working-tree --json
```

После explicit staging publish должен проверить staged index:

```bash
bin/changerail-delivery-manifest scope-check \
  .runtime/changerail/delivery-manifests/example.json \
  --target staged --json
```

Manifest может хранить concise handoff summary без raw logs:

- `verification_summary`: итог проверки, короткое резюме и command/evidence
  references;
- `review_summary`: latest review result, cycle, finding counts и verdict path;
- `final_card_state`: итоговый board path/status и stable result summary.

Helper обновляет такие поля через `handoff-update`; `finalize-card` также
записывает `final_card_state` при post-publish board move. Raw command output,
review history и local evidence остаются ignored runtime artifacts.

После publish ignored manifest можно обновить без staging runtime state:

```bash
bin/changerail-delivery-manifest publish-update \
  .runtime/changerail/delivery-manifests/example.json \
  --status pushed --payload-commit <payload-commit> \
  --published-commit <published-commit> --remote origin --branch main \
  --pushed-at <utc> --mode review-gated
```

Validation is fail-closed for pushed publish ledgers: `status: pushed` is valid
only when `payload_commit`, `published_commit`, remote, branch and `pushed_at`
are all present.

Для explicit `--no-push` manifest должен фиксировать skipped local-only publish
evidence вместо remote readiness:

```bash
bin/changerail-delivery-manifest publish-update \
  .runtime/changerail/delivery-manifests/example.json \
  --status skipped --payload-commit <payload-commit> \
  --published-commit <local-final-commit> \
  --reason "push skipped by --no-push" --mode local-only
```

Tracked done-card text не должен хранить собственный exact final commit hash или
mutable push status. Эти значения остаются в ignored manifest и Git history,
чтобы deterministic card-only amend не создавал stale metadata.

## Evidence Index

Evidence index описывает retained evidence для verification/review handoff:

```text
.runtime/changerail/evidence/<scope>/index.json
```

Schema id: `changerail.evidence-index.v1`. Для ChangeRail-owned verification
commands helper `bin/changerail-evidence` запускает argv array и сохраняет:
stable evidence id, command identity, timestamps, exit code, статус
`passed`/`failed`/`timeout`, classification `mandatory`/`diagnostic`/
`not_applicable`, concise summary и repository-relative raw output path.

Raw output и index остаются ignored runtime state под
`.runtime/changerail/evidence/`. Tracked cards, manifests и verdicts могут
содержать только summary и structured evidence references: evidence id,
index path и raw output path. Manifest `verification_summary.commands[]` и
review verdict `acceptance[]`/`findings[]` поддерживают такие references без
встраивания raw logs.

Helper отказывается запускать command с очевидными secret-like argv values и
редактирует obvious token-like output before retention. Это safety screen, а
не доказательство отсутствия секретов; команды с credentials не должны
передаваться в retained capture.

Пример:

```bash
bin/changerail-evidence capture --card-id example-card --id openspec-all \
  --classification mandatory --timeout 300 -- \
  openspec validate --all --strict
bin/changerail-evidence validate \
  .runtime/changerail/evidence/example-card/index.json --json
```

Evidence может быть committable, runtime или external, но committed artifact не
должен содержать secrets, credentials, customer data, local traces или большие
сырые логи.

## Repository Knowledge

Repository knowledge catalog и maintenance policy являются tracked opt-in
contracts для deterministic maintenance harness. Default paths:

```text
.changerail/knowledge.yaml
.changerail/maintenance.yaml
```

Schema ids:

```text
changerail.repository-knowledge.v1
changerail.maintenance-policy.v1
```

Catalog record содержит:

- `path`: repository-relative knowledge artifact path.
- `status`: `active`, `historical`, `superseded` или `generated`.
- `type`: `tutorial`, `how-to`, `reference`, `explanation`, `architecture`,
  `adr`, `runbook`, `historical` или `generated`.
- `owner`: строка owner-а или `null`, если owner не назначен.
- `source_globs`: array source paths/globs; empty array означает, что source
  связь не объявлена.
- `verify`: array команд или checks; empty array означает, что отдельный check
  не объявлен.
- `review_after`: date `YYYY-MM-DD` или `null`, если freshness deadline не
  задан.
- `supersedes`: array repository-relative paths; empty array означает, что
  predecessor/replacement связь не объявлена.

Catalog и policy YAML читаются через PyYAML, затем валидируются JSON Schema
Draft 2020-12. Contract-owned objects используют `additionalProperties: false`.
Semantic validation дополнительно нормализует repository-relative paths и
fail-closed отклоняет absolute paths, traversal (`..`) и root escape.
`active` catalog record не может ссылаться на отсутствующий path. `historical`,
`superseded` и `generated` records не задают directory layout и не требуют
автоматического удаления.

Отсутствующая `.changerail/maintenance.yaml` означает, что maintenance policy не
configured; existing consumers без opt-in policy остаются unaffected. Runtime
reports, scan history и raw evidence для будущего maintenance harness должны
оставаться под ignored `.runtime/changerail/maintenance/`.

Helper surface:

```bash
bin/changerail-maintenance validate-catalog
bin/changerail-maintenance validate-catalog \
  --catalog .changerail/knowledge.yaml --policy .changerail/maintenance.yaml
bin/changerail-maintenance render-index --check
bin/changerail-maintenance render-index --write
bin/changerail-maintenance scan --json
```

`validate-catalog` поддерживает explicit `--catalog` и `--policy` overrides,
но paths остаются repository-relative и проходят ту же fail-closed safe-path
validation. POSIX wrapper `bin/changerail-maintenance` и native Windows wrapper
`bin/changerail-maintenance.cmd` запускают один и тот же Python helper через
shared runtime selector.

`render-index` строит deterministic Markdown index из validated catalog records.
Ordering stable: normalized `path`, затем `type`, затем `status`; YAML order не
влияет на output. Default render mode и `--check` read-only. `--check`
сравнивает ожидаемый content с configured generated index path и возвращает
non-zero при drift, не меняя файл. Только `--write` обновляет generated index
path, заданный policy `generated_index_path` или explicit `--index`.

`scan` является read-only deterministic integrity gate. Он не использует LLM,
не запускает arbitrary generator commands и всегда пишет один JSON document в
stdout. Report schema id: `changerail.maintenance-scan-report.v1`. Каждый
detector result внутри report использует
`changerail.maintenance-detector-result.v1`. Report разделяет:

- `detectors[].findings`: catalog/link/generated/reference findings;
- `detectors[].errors`: detector failure, timeout или invalid detector output;
- `configuration_diagnostics`: invalid policy/catalog/input diagnostics, когда
  schema-valid complete report нельзя построить.

Exit semantics:

- `0`: complete schema-valid report создан, configured `fail_on` threshold не
  достигнут;
- `1`: complete schema-valid report создан, finding или detector error достиг
  configured `fail_on` threshold;
- `2`: invalid configuration или невозможность создать schema-valid report.

Optional policy `scan` configuration remains additive. Minimal policy with only
`schema`, `catalog_path` and `generated_index_path` is still valid and enables
no detectors implicitly. Configured fields:

- `include_globs` / `exclude_globs`: repository-relative documentation universe
  for coverage and active-scope checks;
- `active_scope_globs`: optional narrower active knowledge scope;
- `enabled_detectors`: `catalog-coverage`, `repository-orphans`,
  `markdown-local-links`, `generated-freshness`,
  `forbidden-active-references`, `adapters`;
- `fail_on`: severity threshold `info`, `minor`, `major` or `blocker`;
- `timeout_seconds`: per-scan detector budget used by bounded detectors;
- `detectors.*`: per-detector options such as Markdown extensions, passive
  generated-index check mode and forbidden active-reference patterns.

Core detectors are intentionally deterministic:

- catalog coverage checks only the explicitly configured documentation universe
  and reports uncovered files; an empty configured universe is a detector error,
  not a silent pass;
- repository orphan detection distinguishes active catalog targets that are
  missing from discovered knowledge files that lack an active catalog record;
- Markdown local link/anchor detection uses `markdown-it-py` token parsing and
  the documented GitHub-compatible anchor algorithm: lowercase heading text,
  convert spaces/hyphens to single hyphens, remove punctuation, and append
  `-1`, `-2` for duplicate headings;
- generated freshness compares maintained source/output state or the existing
  `render-index --check` behavior without running configured generator
  commands;
- forbidden active references scan only configured active knowledge scope and
  report repository-relative path evidence.

Adapter detector configuration is optional and generic. It lets consumer-owned
native checks feed architecture or instruction findings into the same scan
report without adding language-specific analyzers to ChangeRail core:

```yaml
scan:
  enabled_detectors:
    - adapters
  timeout_seconds: 30
  adapters:
    - id: architecture-check
      argv:
        - python3
        - scripts/example-adapter.py
      timeout_seconds: 10
      options:
        profile: architecture
```

Adapters run with `shell=False`, repository cwd and bounded timeout. `argv` is
an array; shell-string command configuration is rejected by schema validation.
Adapter stdout must be one `changerail.maintenance-detector-result.v1` JSON
object with generic fields such as detector id, severity, code, message and
repository-relative path evidence. ChangeRail normalizes any adapter-provided
`path`, `source_path` or `target_path` through the same safe-path rules used by
catalog and policy validation.

Adapter failures cannot become false green results:

- timeout -> detector error `adapter_timeout`;
- non-zero exit -> detector error `adapter_nonzero_exit`;
- invalid JSON or schema-invalid output -> detector error
  `invalid_adapter_json` or `invalid_adapter_output`;
- absolute paths, traversal or root escapes in adapter evidence -> detector
  error `unsafe_adapter_path`.

## Maintenance Lifecycle Findings

Maintenance lifecycle report является normalized layer поверх raw scan output.
`scan` продолжает публиковать неизмененный
`changerail.maintenance-scan-report.v1`; lifecycle consumers используют:

```bash
bin/changerail-maintenance report --json
bin/changerail-maintenance report --json --write-state
```

Report schema id: `changerail.maintenance-report.v1`. Runtime state schema id:
`changerail.maintenance-state.v1`. State path по умолчанию:

```text
.runtime/changerail/maintenance/state.json
```

`report` строится только из complete schema-valid scan report. Если source scan
incomplete, schema-invalid, содержит unsafe evidence или runtime state corrupt /
unsupported, lifecycle report fail-closed: `complete: false`, blocker
diagnostic и non-zero exit. Corrupt state не заменяется implicit write-ом.

Каждый normalized finding содержит:

- `fingerprint`: stable `sha256:<hex>` identity;
- `evidence_fingerprint`: separate evidence hash;
- `detector`, `rule`, `severity`, `confidence`, `path`;
- `evidence_refs`, `remediation`, `first_seen`, `last_seen`, `owner`,
  `risk_class` и lifecycle `status`.

Identity material является canonical JSON over `identity_version`, detector
result id, finding rule/code и normalized repository-relative subject.
`message`, `severity`, `evidence`, timestamps и absolute workspace root не
участвуют в identity. Evidence fingerprint считается отдельно от sanitized
material evidence, поэтому новое evidence меняет `evidence_fingerprint`, но не
меняет `fingerprint`.

Lifecycle normalization read-only by default. Без restored state `first_seen`
является текущим observation timestamp, и report явно пишет
`state.continuity: not_restored`. Сохранение continuity требует explicit
`--write-state`; state и previews остаются ignored runtime artifacts under
`.runtime/changerail/maintenance/`. Если operator задает custom `--state`,
path всё равно должен находиться ниже `.runtime/changerail/maintenance/`; state
write в tracked path fail-closed.

Unknown absolute paths, traversal paths, URL-like external references,
backslash paths и secret-like raw values in detector evidence rejected before
lifecycle output. Unsafe values не копируются в report.

## Maintenance Baseline And Cards

Tracked baseline path по умолчанию:

```text
.changerail/maintenance-baseline.yaml
```

Schema id: `changerail.maintenance-baseline.v1`. Baseline содержит отдельные
collections:

- `accepted`: reviewed finding identities keyed by `fingerprint`;
- `waivers`: temporary suppressions keyed by `fingerprint`.

Waiver требует `owner`, `reason` и ISO-8601 `expires_at` или `review_after`.
Expired waiver не suppress-ит current finding: lifecycle report оставляет
finding `status: open` и добавляет diagnostic. Accepted или active waived
finding не участвует в open-finding threshold calculation. Date-only waiver
boundary нормализуется в lifecycle report как UTC midnight date-time для
`suppressed_until`.

Baseline preview/write surface:

```bash
bin/changerail-maintenance accept-baseline --json
bin/changerail-maintenance accept-baseline --write --json
```

Default mode пишет schema-valid baseline preview under ignored
`.runtime/changerail/maintenance/previews/` и не меняет tracked files.
`--write` может менять только `.changerail/maintenance-baseline.yaml`.

Triage annotations are schema-bound JSON with schema id
`changerail.maintenance-triage.v1`:

```bash
bin/changerail-maintenance triage --annotations <path> --json
```

`triage` only validates and normalizes supplied annotations. It does not invoke
an LLM or external model process.

Board-card bridge:

```bash
bin/changerail-maintenance cards --json
bin/changerail-maintenance cards --write --json
```

Default mode writes card previews under ignored
`.runtime/changerail/maintenance/previews/cards/`. `--write` creates or updates
tracked board cards. Before write, the bridge scans
`openspec/board/1.backlog` through `openspec/board/5.canceled` for the exact
line:

```text
Maintenance Origin: <sha256 fingerprint>
```

The same identity updates the existing card evidence summary and never creates
another card. Written card titles, summaries and evidence references use only
sanitized repository-relative metadata; raw detector output, absolute consumer
paths, secret-like `finding.path` values, credentials and unredacted snippets
remain indirect runtime evidence.

## Maintenance Run Status

Maintenance runner status является runtime-файлом:

```text
.runtime/changerail/maintenance/runs/<run-id>/status.json
```

Schema id: `changerail.maintenance-run.v1`. Status содержит workspace, mode,
phase, result, timestamps, command metadata, lock diagnostics,
timeout/budget diagnostics, optional usage availability и references на
retained report/annotation/preview artifacts. Raw command logs, credentials и
local traces не inline-ятся в status.

Runner surface:

```bash
bin/changerail-maintenance-runner scan --json
bin/changerail-maintenance-runner triage --annotations <path> --json
```

`scan` вызывает deterministic `bin/changerail-maintenance report --json` и не
требует Codex auth. `triage` принимает schema-bound annotation input или
operator-supplied child command output and validates it as
`changerail.maintenance-triage.v1`; successful card previews остаются below
ignored `.runtime/changerail/maintenance/`.

Control flow читает только structured status fields and validated JSON
artifacts. Human prose from child output is never enough for success:
schema-invalid report, invalid triage JSON, timeout or lock conflict records
`result: BLOCKED` or `FAILED` with stable `terminal_reason`.

The runner owns an atomic repository-local non-overlap lock under the ignored
maintenance runtime root. Stale or externally created locks block a new run and
must be handled by an operator; the runner does not delete uncertain locks
automatically.

## Maintenance Feedback

Maintenance feedback command работает read-only и пишет ровно один
`changerail.maintenance-detector-result.v1` JSON document для explicit feedback
inputs:

```bash
bin/changerail-maintenance feedback \
  --adapter-id lifecycle --review-history <path> --json
bin/changerail-maintenance feedback \
  --adapter-id delivery --delivery-run <path> --json
bin/changerail-maintenance feedback \
  --adapter-id external --detector-result <path> --json
```

Supported inputs:

- schema-valid `changerail.review-cycle-history.v1` review-cycle history;
- schema-valid `changerail.delivery-run.v1` records whose `result` and
  `terminal_outcome` are `BLOCKED` and whose `terminal_reason` is structured;
- schema-valid external `changerail.maintenance-detector-result.v1` producer
  records.

Feedback normalization fail-closed отклоняет malformed, unsafe,
schema-invalid или unsupported records. Команда не выводит findings из prose
logs, diagnostics или review comments. External producers пересекают adapter
boundary только через detector-result schema и repository-relative safe-path
validation.

## Maintenance Quality Rollup

Maintenance quality command работает read-only и по умолчанию пишет
human-readable text, с `--json` пишет один
`changerail.maintenance-quality-rollup.v1` JSON document, а с `--csv` - stable
CSV:

```bash
bin/changerail-maintenance quality --report <latest-report>
bin/changerail-maintenance quality --report <latest-report> --json
bin/changerail-maintenance quality --report <latest-report> --csv
```

Quality inputs являются explicit repository-relative files:

- `--report`: latest schema-valid `changerail.maintenance-report.v1`;
- `--history`: historical lifecycle reports used for resolved/history metrics;
- `--triage`: schema-valid `changerail.maintenance-triage.v1`;
- `--proposal`: schema-valid `changerail.maintenance-proposal-decision.v1`.

Proposal-decision records являются runtime quality observations. Они фиксируют
accepted/rejected proposal outcomes как evidence для rollup metrics и не дают
authority на board writes, commits, pushes или publication.

Metric status имеет contract semantics:

- `known`: metric рассчитан из complete schema-valid inputs;
- `unknown`: required producer input отсутствует, incomplete или не может
  поддержать calculation.

Incomplete lifecycle history оставляет dependent metrics unknown.
Schema-invalid reports, triage records или proposal decisions дают diagnostics
и non-zero exit вместо guessed quality data.

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
  runner-observed `started_at`, `ended_at`, `duration_seconds` и optional
  bounded `output` metadata: stdout/stderr bytes, total bytes, threshold,
  threshold-exceeded flag, truncation flag и classification;
- `command_output` aggregate summary с documented threshold, observed/oversized
  command counts, largest observed command bytes и bounded top oversized
  command labels;
- `file_change_count`;
- `timeline` с bounded runner-observed событиями;
- `review.cycle_count`, `review.first_review_latency_seconds`,
  `review.time_to_final_go_seconds`, optional `review.rescue_budget` и
  per-cycle timing;
- `publish.latency_seconds` и `publish.pushed_at`, когда publish metadata
  доступна.

`performance.review.rescue_budget` является best-effort summary copy. Если для
той же карточки доступна review-cycle history, metrics использует history как
canonical source, а run summary только как fallback без history.

`usage` всегда содержит `available`. Когда provider output позволяет, runner
может дополнительно писать `input_tokens`, `cached_input_tokens`,
`uncached_input_tokens`, `output_tokens`, `reasoning_tokens` и `total_tokens`.
Если explicit `total_tokens` отсутствует, metrics может вычислять display-only
total как `input_tokens + output_tokens`, не меняя runtime record.
Command output bytes не являются token usage estimate: это runner-observed
metadata из structured child command events. Если token usage недоступен, metrics
показывает token fields как `unknown`, но все равно может показать output-byte
amplification, когда `performance.command_output` присутствует.

Tracked runner:

```bash
bin/changerail-delivery-runner preflight openspec/board/3.inprogress/example.md \
  --connectivity-url https://example.invalid/health --json
bin/changerail-delivery-runner run openspec/board/3.inprogress/example.md \
  --model gpt-5 --reasoning-effort medium
bin/changerail-delivery-runner resume \
  --status-path .runtime/changerail/delivery-runs/<run-id>/status.json
bin/changerail-delivery-runner status \
  .runtime/changerail/delivery-runs/<run-id>/status.json
bin/changerail-delivery-runner status --run-id <run-id> --json
```

Single-card `status` является read-only reader-ом для existing
`changerail.delivery-run.v1` records. Selector может быть explicit
`status.json`, `--run-id` внутри effective runtime root или latest status under
`<workspace>/.runtime/changerail/delivery-runs/`. Одновременные selectors,
missing/corrupt/schema-invalid или unsupported status records fail-closed и не
fallback-ят на другой run. Human output показывает compact attention fields:
card, run id, phase, result, `updated_at`, optional `terminal_reason`,
selected status path и canonical related runtime paths для manifest, review
verdict, review history и evidence index. Existing linked artifacts
валидируются по tracked schemas before trust; invalid manifest/verdict/history
или evidence index дает non-zero diagnostic вместо guessed guidance. Если
valid manifest содержит `runtime_pause_reasons`, reader печатает только stored
`summary` и `next_action` values. `--json` возвращает validated source
`changerail.delivery-run.v1` record без unschematized wrapper.

Runner запускает `codex exec` через настроенный launcher, закрывает stdin
child-процесса, выполняет child в effective workspace и экспортирует
`CODEX_WORKDIR=<workspace>`. Runner также передает child-у compact discovery
policy через prompt и environment: начинать с scoped paths, `rg -l`, counts,
top-level file lists или bounded excerpts, считать truncated output и exit `130`
inconclusive evidence, а raw stdout/stderr оставлять ignored runtime evidence.
Default per-command output threshold - 65536 bytes, с override через
`CHANGERAIL_COMMAND_OUTPUT_THRESHOLD_BYTES`. Для ChangeRail source checkout default launcher -
tracked `/opt/changerail/bin/codex`; consumer repository не обязан иметь
tracked `bin/codex`, если оператор запускает ChangeRail runner извне или
передает supported launcher через `--launcher`. Если `--workspace` не указан, workspace
резолвится в git-root invocation cwd, а вне git - в текущий cwd. Если
`CODEX_HOME` не задан, runner использует ignored mutable home
`<workspace>/.runtime/changerail/codex-home`; tracked project policy остаётся в
`<workspace>/.codex/config.toml`. Runtime `config.toml` содержит только exact
absolute trust binding выбранного workspace, поэтому Codex persistence не
меняет review payload. Existing ignored project `.codex/auth.json` или
`.codex/auth.toml` подключается в runtime home symlink-ом без чтения и
копирования credential contents. Если
`--runtime-root` не задан, status пишется под
`<workspace>/.runtime/changerail/delivery-runs/`. Preflight записывает диагностику
launcher, Codex binary, auth state, effective project policy, stale symlink-ов
в runtime home и project `.codex/`, permissions, publish target и optional
connectivity URL. Explicit operator `CODEX_HOME` остаётся operator-owned:
runner использует его config/auth state и не генерирует там файлы. Если такой
home проходит exact trusted automation gate и используется tracked ChangeRail
`bin/codex`, preflight дополнительно требует поддержку Codex option
`--dangerously-bypass-approvals-and-sandbox`, а реальный child получает этот
option перед `exec`. Это узкий explicit opt-in для externally sandboxed
unattended runner: он делает уже выданную authority effective, но не заменяет
config/auth/clean-tree/upstream/publish-target checks. Generated default home и
custom launchers не получают Codex-specific bypass автоматически. Remote
publish-target proof выполняет `git ls-remote --exit-code <remote>
refs/heads/<branch>` и сохраняет только sanitized command/result/detail:
remote name, branch, remote URL class, failure class, retryability, attempt
count и bounded detail. Failure classes: `ssh_config`, `dns`, `auth`,
`missing_branch`, `timeout`, `unknown_remote_failure`. Bounded retry/backoff
допустим только для `dns`, `timeout` и `unknown_remote_failure`; auth, SSH
config и branch uncertainty остаются fail-closed. Connectivity diagnostics
записывают только sanitized endpoint metadata, status или exception class; raw
URL, query values и raw exception text не являются частью structured status.
Если single-card preflight не может доказать remote publish target, written
status records `terminal_reason: publish_target_preflight_failed`; failed
`publish target` check remains the source for sanitized `failure_class`,
retryability, attempts and evidence.
Child stdout/stderr logs остаются raw ignored runtime evidence и не должны
публиковаться как public artifacts. `DELIVERED`, `NO-GO` и
`BLOCKED` являются терминальными outcome для supervisor-а и печатаются в stdout
runner-а. Structured JSONL events вроде `external-review/no-go` дают `NO-GO`,
а `awaiting-review` дает `BLOCKED`; exact marker lines
`terminal_outcome: ...` и `terminal_reason: ...` принимаются только из
completed agent-message event, не из произвольного prose. Эти structured
signals являются preferred source of truth; если их нет, fallback по
`exit_code == 0` допустим только после проверки, что есть доказательство
опубликованной карточки под `openspec/board/4.done`. Для текущей card runner
сначала проверяет canonical verdict
`.runtime/changerail/reviews/<card-id>.json`: schema-valid unpublished
`result: no-go` дает terminal outcome `NO-GO`, даже если обязательная tracked
rescue/replacement card после review сделала negative fingerprint stale. Такой
negative verdict только блокирует публикацию и не требует freshness. Для
`result: go` current-tree freshness остается обязательной; stale/invalid
positive verdict блокирует fallback как `BLOCKED/review_verdict_invalid`. Если
verdict fallback не применим и карточка
не опубликована, successful child exit записывается как `BLOCKED` с
`terminal_reason: unpublished_card`. `fix_budget_exhausted`,
`external_blocker` и другие stable reasons сохраняются в status как
`terminal_reason`; ignored raw logs не являются источником этих reasons.
Malformed reason из authoritative terminal event не принимается как classifier:
runner записывает стабильный `terminal_reason: malformed_terminal_reason` для
operator diagnostics.
Если preflight возвращает `CODEX auth: fail` или `CODEX_HOME symlinks: fail`,
оператор должен использовать remediation из
`docs/consumer-adoption-runbook.md#codex-auth-for-delivery-runner`: ignored
project-local marker, explicit `CODEX_HOME` или supported auth environment
variable без публикации credentials.

Single-card `resume` принимает prior `changerail.delivery-run.v1` status как
контекст после blocked remote publish-target preflight, но не доверяет прежнему
preflight как proof. Runner повторяет полный fresh preflight текущего workspace
и запускает `$changerail-deliver` только если publish target доказан заново.
Если prior status отсутствует, невалиден, относится к другой card/workspace или
fresh proof снова не проходит, resume пишет `BLOCKED` и не запускает delivery.

## Delivery Plan

Delivery plan является consumer-owned JSON-файлом:

```text
delivery-plan.json
```

Schema id: `changerail.delivery-plan.v1`. Plan описывает bounded queue через
workspace aliases, consumer-root-relative workspace paths, card ids, card
filenames или board paths, dependencies, waves, `max_parallel`,
`per_workspace_parallelism`, optional per-card model/reasoning overrides и
optional `recovery_for` для linked rescue/replacement cards.
Required format is JSON, чтобы core runner не получал обязательную YAML
dependency. YAML может быть добавлен позднее только как optional extension.
Для обычных serial queues JSON можно создать helper-командой
`generate-plan`; это не отдельный формат, а генератор того же
`changerail.delivery-plan.v1` contract.

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

Пример генерации такого плана из ordered card list:

```bash
bin/changerail-delivery-runner generate-plan --id example-plan \
  --workspace service-a=service-a --workspace service-b=service-b \
  --card service-a-card.md \
  --card service-b-card=service-b:service-b-card.md \
  --depends service-b-card=service-a-card \
  --output delivery-plan.json --consumer-root /opt/example-workspace
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
Queue admission uses the configured single-card runner `preflight
--write-status` command as a child-equivalent publish-target receipt before
workspace locks or delivery children. `run-plan` and `resume-plan` rerun that
receipt immediately before dispatching each later unresolved card. Если child
preflight блокируется на remote publish target, aggregate card status
сохраняет `terminal_reason: publish_target_preflight_failed`, compact
reason/failure class и `run_status_path`, а не raw child logs.
For queue plans, plan runner запускает ChangeRail single-card runner, the
single-card runner запускает Codex, and `CODEX_WORKDIR` и effective
`CODEX_HOME` bind each child to its consumer workspace.

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

Queue `NO-GO`, `BLOCKED` и missing/invalid child status остаются fail-fast:
aggregate run не запускает новые downstream cards после unsafe child outcome и
не публикует failed child payload. Child `terminal_reason` сохраняется в
aggregate card status, включая `fix_budget_exhausted` и
`missing_or_invalid_child_status`. Autonomous recovery после `NO-GO` или
`fix_budget_exhausted` должен быть представлен как linked rescue/replacement
card с `recovery_for`; external blockers не создают implementation recovery
автоматически. `resume-plan` принимает fingerprint drift только для узкого
добавления valid recovery card: она должна ссылаться на prior recoverable
source, быть в том же workspace/wave и наследовать dependencies. Source
становится `recovered` и получает `recovered_by` только после успешной delivery
recovery card; downstream dependencies запускаются после этого.

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

Known rescue-budget history добавляет optional top-level object:

```json
"rescue_budget": {
  "limit": 2,
  "used": 1,
  "remaining": 1,
  "exhausted": false
}
```

Per-cycle optional `same_card_rescue_attempt` отделяет review number от
post-review rescue attempt counter: initial review is `review_cycle: 1` and
`same_card_rescue_attempt: 0`; re-review after one scoped same-card rescue uses
`review_cycle: 2` and `same_card_rescue_attempt: 1`. Legacy history без этих
optional fields остается valid и отображается как `unknown`.

Новый writer также может хранить независимые counters:

```json
"phase_counters": {
  "planning_cycles": 1,
  "delivery_fix_cycles": 2,
  "implementation_review_cycles": 1,
  "live_admission_reviews": 0
}
```

Planning, deterministic preflight и live-admission review не увеличивают
`implementation_review_cycles` и не расходуют same-card rescue budget.

Metrics helper:

```bash
bin/changerail-delivery-metrics
bin/changerail-delivery-metrics --csv
```

Он читает structured run records и review-cycle history, печатает per-run и
aggregate metrics, including `first_pass_go` and rescue budget
`limit`/`used`/`remaining`/`exhausted`; отсутствующие optional fields выводит
как `unknown`.

## Public Safety

Contracts are public source. Примеры должны использовать только generic пути
вроде `/opt/changerail` и `/opt/example-project`. Runtime payloads, verdicts,
manifests и local evidence остаются ignored state.
