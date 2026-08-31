## Context

Published safe base `16d441e8b5f4d8a415ae011e46cce5b3863a1010`
содержит decision для bounded public-history scanner, но ещё не содержит его
implementation и release-suite split. Исходная unpublished delivery-попытка с
fingerprint
`sha256:572256168a43edd2f97c26eca3f22be68473ff4007726c71624d364d63c467c7`
прошла шесть source acceptance checks, затем исчерпала review cycles `1..3` и
same-card rescue attempts `0..2` (`2/2`). Последний `NO-GO` выявил, что
фактический runner уже вынес one-command delivery smoke из core, но
`changerail-release-discipline` всё ещё нормативно требовал его от default
baseline.

Этот change является clean linked replacement. Старые unpublished card,
archives, runtime reports и raw logs не являются input payload или evidence:
полезны только перечисленные публично-безопасные blocker classes — raw
mode/framing oracle, timeout/non-zero oracle, suite inventory/non-overlap,
full-checkout fetch depth и final normative ownership. Implementation,
manifest, evidence и independent review должны быть построены заново от safe
base.

Затрагиваются `scripts/public-surface-scan.py`, новый focused fixture,
`.changerail/source-classification.yaml`, `scripts/run-release-baseline.py`,
`scripts/smoke-release-ci.py`, `.github/workflows/changerail-ci.yml`, новый
extended workflow, `docs/release-discipline.md`, `docs/compatibility.md` и два
OpenSpec capabilities. Весь coherent unit остаётся ordinary risk с high review
effort, не более 300 added production LOC, без новой authority, dependency,
release-ref CLI или wire/report protocol.

## Goals / Non-Goals

**Goals:**

- реализовать опубликованную bounded `HEAD` unique-blob architecture и
  сохранить structured commit/path attribution;
- доказать semantic parity, strict raw/batch framing, lifecycle failure,
  process-count и wall-clock ceilings focused fixture;
- сделать default core Linux-focused и отделить scheduled/manual extended
  regressions с exact, unique и disjoint command ownership;
- закрепить one-command delivery regression только за exact invocation
  `python3 scripts/run-release-baseline.py --suite extended` во всех code,
  CI, docs и normative specs;
- потребовать fresh manifest/evidence/review после реализации.

**Non-Goals:**

- импорт или публикация старого dirty payload и его archived changes;
- изменение current-tree roots, detection/redaction rules или
  `changerail.public-surface-scan.v1`;
- новый release ref option, сканирование unrelated refs или shallow-history
  acceptance;
- удаление Windows implementation или новая native Windows certification;
- режим `all`, который повторно объединяет suites в один admission monolith.

## Decisions

### 1. Coherent replacement строится заново от safe base

Delivery реализует scanner, fixture, suite runner/workflows, CI oracle, docs и
оба delta contracts в одном reviewed diff. Частичный docs-only repair
отклонён: он оставил бы implementation и normative ownership происходящими из
разных payloads. Старые unpublished card/archives не копируются и не
cherry-pick-ятся; они не входят в manifest scope.

Production-counted additions всего unit обязаны остаться `<=300` LOC. Если
fresh implementation превышает ceiling или требует новую authority/schema,
delivery останавливается для нового split/investigation.

### 2. History mode использует три bounded Git lifecycle

`--history` один раз разрешает полный `HEAD^{commit}` и shallow state, затем
запускает один
`git log --full-history -m --raw -z --root --no-renames --no-abbrev
--format=tformat:%x1e%H` для selected public roots и один persistent
`git cat-file --batch`. Unrelated local/worktree/remote refs не участвуют.
Missing/unborn `HEAD`, shallow ancestry или failure любого lifecycle дают
redacted structured finding и non-zero result.

Raw parser работает по bytes как state machine `marker -> header -> path`.
Marker — `0x1e` плюс full resolved object id; только первый header может иметь
один leading LF. Header проверяет field count, full OIDs, old/new modes,
single-parent status и допустимый переход object type/mode. Delete,
submodule/tree и zero-object transitions не передаются content reader;
regular/symlink non-zero blobs группируются как
`blob oid -> [(commit oid, path)]`. `cat-file --batch` принимает только exact
requested oid, type `blob`, decimal size, ровно объявленные bytes и trailing
LF.

Focused fixture обязан отдельно доказать raw mode/framing oracle: valid
root/add/modify/delete, symlink, rename-as-delete/add и merge-resolution cases
принимаются, а malformed marker/header/path state, invalid mode/status/OID
transition, combined/extra fields, truncation и unexpected batch response
отклоняются. Отдельный lifecycle oracle инъецирует timeout и non-zero exit для
resolve/log/batch boundaries, premature EOF и pipe failure. Во всех negative
cases output остаётся generic/redacted, scanner не выдаёт pass и не копирует
raw bytes или stderr.

### 3. Focused fixture является самостоятельным deterministic gate

`scripts/smoke-public-surface-history.py` строит temporary public-safe fixture
минимум с 250 commits и 20 paths, reused blobs, deletion, rename,
merge-resolution blob, binary/invalid UTF-8, multi-path finding, excluded root
и unrelated ref. Он доказывает scan-each-unique-blob-once, complete attribution,
не более трёх Git processes и завершение под external `timeout 30s`.
`.changerail/source-classification.yaml` классифицирует fixture как test, а не
production. Clean-checkout default core выполняется под external
`timeout 300s`.

### 4. Runner публикует два exact и непересекающихся inventory

Default `python3 scripts/run-release-baseline.py` означает `core`; runner также
поддерживает deterministic `--list`. Core inventory в фиксированном порядке:

1. `./bin/openspec validate --all --strict`
2. `python3 -m json.tool .mcp.json`
3. TOML parse `.codex/config.toml` через `python3 -c`
4. `python3 scripts/smoke-contract-schemas.py`
5. `python3 scripts/compile-python-inventory.py`
6. `python3 scripts/smoke-python-runtime.py`
7. `ruff check bin scripts`
8. `python3 scripts/smoke-release-ci.py`
9. `python3 scripts/public-surface-scan.py --self-test`
10. `python3 scripts/smoke-public-surface-history.py`
11. `python3 scripts/public-surface-scan.py`
12. `python3 scripts/public-surface-scan.py --history`
13. `python3 scripts/smoke-wiring-discovery.py`
14. `python3 scripts/smoke-verify-project.py`
15. `python3 scripts/smoke-runtime-diagnostics.py`
16. `python3 scripts/smoke-bootstrap-project.py`
17. `python3 scripts/smoke-consumer-ci.py`
18. reset generated drift fixture under ignored runtime state
19. `./bin/bootstrap-project .runtime/changerail/ci-drift/example-project
    --name example-project --kind generic --lock-enforcement none`
20. `python3 scripts/smoke-drift.py --project
    .runtime/changerail/ci-drift/example-project`
21. `git diff --check`
22. `git status --short --ignored`

Extended inventory, также в фиксированном порядке:

1. `python3 scripts/smoke-review-verdict-validation.py`
2. `python3 scripts/smoke-review-fingerprint.py`
3. `python3 scripts/smoke-review-fingerprint-benchmark.py`
4. `python3 scripts/smoke-review-fingerprint-cache.py`
5. `python3 scripts/smoke-review-preflight.py`
6. `python3 scripts/smoke-retained-evidence.py`
7. `python3 scripts/smoke-maintenance-runner.py`
8. `python3 scripts/smoke-delivery-manifest.py`
9. `python3 scripts/smoke-delivery-manifest-derive.py`
10. `python3 scripts/smoke-delivery-runner.py`
11. `python3 scripts/smoke-delivery-metrics.py`
12. `python3 scripts/smoke-openspec-archive-diagnostics.py`

Windows entrypoint, wiring Git-safety и aggregate matrix commands не входят ни
в core, ни в extended и остаются explicit opt-in diagnostics. Режим `all`
отсутствует. `scripts/smoke-release-ci.py` сравнивает `--list` с exact sets,
проверяет order, uniqueness, disjointness, rejects missing/extra/overlap и
доказывает, что `scripts/smoke-delivery-runner.py` принадлежит только extended.

### 5. CI routes соответствуют suite ownership

Default push/pull-request workflow после setup исполняет ровно
`python3 scripts/run-release-baseline.py`, то есть default core inventory.
Отдельный scheduled/manual workflow исполняет ровно
`python3 scripts/run-release-baseline.py --suite extended`; default workflow
не содержит эту команду и не запускает extended-owned smoke напрямую. Оба
workflow используют pinned actions и `fetch-depth: 0`, чтобы release history
не зависела от shallow checkout. Contract smoke fail closed при missing route,
trigger, full-history checkout, inventory item или overlap.

### 6. Release discipline является финальным normative owner

`changerail-release-ci` владеет suite composition и CI routing.
`changerail-release-discipline` владеет maintainer-facing release procedure и
явно заменяет старое требование: default core MUST NOT выполнять
one-command delivery regression; обязательная проверка выполняется только
exact extended invocation. `docs/release-discipline.md` повторяет этот handoff,
а `docs/compatibility.md` описывает Linux-focused current claim и retained
opt-in Windows diagnostics.

### 7. Operator-authorized remediation остаётся bounded test-only scope

После первоначального delivery blocker оператор отдельно разрешил исправить
только runtime обязательного `scripts/smoke-verify-project.py` без новой board
card или OpenSpec change. Smoke разделён ровно на два process worker-а с
замороженными inventories `39 + 30`; parent сохраняет исходный порядок всех 69
scenario results и fail closed при exception, crash, timeout, missing,
duplicate или malformed terminal result. Отдельный
`scripts/smoke-verify-project-sharding.py` наблюдает именно process boundary,
паритет, порядок, single failure propagation, isolation и cleanup, поэтому он
падал бы при возврате исходного sequential runtime или ослаблении parent
protocol.

Оба remediation-файла входят в card-owned manifest. Sharding oracle явно
классифицирован как non-production test, поэтому production ceiling coherent
unit остаётся 272 LOC. Долгосрочная simplification не входит в этот change.

## Risks / Trade-offs

- **[Raw Git grammar может принять неоднозначный mode/status]** → byte-level
  valid/invalid transition matrix и fail-closed state machine.
- **[Persistent process зависает или завершается после partial output]** →
  explicit timeout/non-zero/EOF/pipe oracles и bounded cleanup.
- **[Suite check потеряется или окажется в обоих routes]** → exact ordered
  `--list` contract и negative removal/extra/overlap fixtures.
- **[Normative prose снова разойдётся с runner]** → delta requirement меняет
  `Release baseline includes one-command delivery regression`, а review
  проверяет code/docs/spec ownership вместе.
- **[Extended больше не блокирует каждый push]** → scheduled/manual workflow
  остаётся fail-closed и является обязательным release evidence до publish.
- **[Windows regression перестаёт быть default admission]** → current claim
  Linux-focused; retained scripts остаются syntax/lint-covered opt-in tools.
- **[Process sharding меняет порядок или скрывает падение worker-а]** → exact
  `39 + 30` inventory, deterministic parent aggregation и focused fail-closed
  process oracle.

## Migration Plan

1. Из safe base сначала добавить fresh RED focused fixture и suite ownership
   oracle, включая framing/lifecycle и normative mismatch cases.
2. Реализовать bounded scanner, довести focused fixture до GREEN и подтвердить
   production LOC ceiling.
3. Ввести core/extended runner inventories, default/extended workflows и exact
   CI contract; затем обновить public docs и оба main specs через OpenSpec sync.
4. Выполнить focused, core, extended, strict OpenSpec, public-surface и
   whitespace gates; собрать fresh manifest/evidence без старых runtime данных.
5. Архивировать change через `changerail-do` и передать весь coherent payload
   новому independent reviewer. На regression публиковать ничего нельзя;
   возврат — к safe base и fresh replacement attempt.

## Open Questions

Нет. Exact suite ownership и one-command invocation являются фиксированным
product decision; их изменение требует нового reviewed change.
