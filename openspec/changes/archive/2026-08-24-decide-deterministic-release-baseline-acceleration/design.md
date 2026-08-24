## Context

`scripts/run-release-baseline.py` последовательно вызывает 36 обязательных
команд. Decision касается только внутренней работы трёх из них:

- `python3 scripts/public-surface-scan.py --history`;
- `python3 scripts/smoke-review-preflight.py`;
- `python3 scripts/smoke-delivery-runner.py`.

Команды нельзя удалять, условно пропускать или заменять reusable receipt всего
baseline. Любое ускорение остаётся внутри соответствующего шага и должно
доказать тот же observable result.

### Измеренная исходная точка

Canonical prior evidence index фиксирует standalone history scan с
14:39:56 до 14:50:23, то есть 627.163 s, и последующий полный release baseline
с 15:17:36 до 15:47:47, то есть 1810.799 s. Card-owned ignored evidence index
содержит exact extraction command/output для этих двух prior entries, а также
exact commands/output/duration bounded inventory и object-I/O microbenchmark.
Bounded inventory текущего checkout без сканирования содержимого дал:

| Metric | Value |
| --- | ---: |
| reachable commits | 92 |
| tracked files current tree | 1384 |
| `rev-list --objects --all` entries | 3422 |
| selected commit/path entries | 102706 |
| unique selected blob OIDs | 1652 |
| unique `(blob OID, exact path)` pairs | 1959 |

Текущий `scan_history()` запускает `ls-tree` на каждый commit и отдельный
`git show <commit>:<path>` на каждый selected entry. Поэтому один history run
создаёт примерно 102800 Git processes и повторно сканирует одинаковый
path-sensitive content в среднем более 52 раз.

Bounded object-I/O microbenchmark из retained evidence прочитал одни и те же
200 blobs тремя итерациями. Process-per-blob занял 0.9358/0.9671/0.9356 s,
один `git cat-file --batch` — 0.0231/0.0153/0.0305 s, то есть batch был в
40.6x/63.2x/30.7x быстрее. Это измеряет только process/object-I/O cost и не
подменяет acceptance timing полного шага.

Текущий review smoke содержит 44 статических вызова workspace builders и fresh
standalone cold/warm capture прошёл за 71.325/72.154 s. Текущий delivery smoke
содержит 75 `check_*` функций и 87 статических workspace-builder calls; fresh
cold/warm capture прошёл за 115.873/116.046 s. Exact command, PASS output и
monotonic duration каждого sample находятся в card-owned evidence index. Эти
различия являются host noise, а не persistent reuse: оба script каждый раз
строят fresh fixtures.

Cold reference трёх named stages суммарно равен 814.361 s. Это не объясняет
весь baseline: ещё 996.438 s того retained run принадлежат остальным steps и
orchestration. Для history retained wall-clock sample равен 627.163 s; отдельный
второй 627.163-second run не выполнялся по bounded investigation
constraint. Его warm work count, однако, точно совпадает с cold: current code
не имеет persistent cache и снова запускает 92 `ls-tree` плюс 102706 `git show`
operations. Implementation acceptance поэтому обязана впервые измерить paired
cold/warm wall time после появления cache.

## Goals / Non-Goals

**Goals:**

- Сканировать каждый reachable path-sensitive Git blob ограниченное число раз.
- Сохранить точную path, line, kind, redaction и commit-ref семантику findings.
- Инвалидировать reuse при любом изменении scanner policy или content/path
  input и никогда не доверять повреждённой cache записи.
- Устранить process-per-object через batch Git I/O.
- Выполнять независимые smoke cases параллельно в разных process/temp roots.
- Ограничить jobs и timeout, а diagnostics агрегировать в стабильном порядке.
- Доказать parity, negative behavior, corruption handling и существенное
  ускорение на frozen fixtures.

**Non-Goals:**

- Пропуск любого из 36 baseline steps или исключение smoke cases из registry.
- Cache/receipt результата всего baseline, publish receipt или новая authority.
- Reuse результата history scan без свежего перечисления reachable Git inputs.
- Параллелизация самого `scripts/run-release-baseline.py`.
- Изменение public scanner JSON schema, runner wire schemas, credentials,
  network или consumer-project contract.
- Создание successor cards в этом decision change.

## Decisions

### 1. History scan использует fresh reachability и conservative exact-path content keys

Каждый invocation сначала fail-closed получает полный ordered commit set из
`git rev-list --all` и object format из Git. Никакой cache не разрешает
пропустить это перечисление. Затем scanner строит ordered occurrence table:

```text
(blob_oid, exact_repo_relative_path) -> [commit_oid in rev-list/tree order]
```

Root и `SKIP_DIRS` filters применяются при tree traversal. Exact path является
conservative частью identity: текущая `allowed_opt_path(..., history=True)`
принимает historical `/opt/opsx` безусловно, но scan function принимает
`rel_path`, а future tracked policy может использовать его. Один blob под двумя
paths сканируется дважды; повторение того же
blob по тому же path в нескольких commits сканируется один раз, после чего
findings материализуются для каждого occurrence с соответствующим 12-symbol
`ref`. Так сохраняются существующие duplicates и ordering.

Alternative «cache только по blob OID» отвергнута: она не защищает будущую
tracked path-sensitive policy и rename invalidation. Alternative «cache по
commit» отвергнута: она почти не переиспользует одинаковые blobs между commits.

### 2. Git objects читаются batch protocol, ошибки объектов блокируют шаг

Implementation использует bounded число Git processes: `rev-list` и один или
несколько `git cat-file --batch` readers для commit/tree/blob objects. Raw tree
parser учитывает repository object format, modes, NUL-separated names,
subtrees, symlinks и gitlinks. Он de-duplicate-ит уже прочитанные object OIDs,
но сохраняет `(tree_oid, path_prefix)` traversal там, где prefix меняет полный
path.

Missing object, malformed batch header, short read, unexpected object type,
invalid tree entry, failed Git command или undecodable path завершает history
step non-zero с redacted diagnostic. Существующее silent `continue` для
`ls-tree`/`show` failure не переносится.

Если raw-tree implementation окажется непропорционально сложной для первого
successor, допустим bounded fallback: один `ls-tree -r -z` на commit плюс один
batch blob reader. Acceptance всё равно запрещает process-per-file и требует
одинаковую occurrence table. Fallback не меняет cache semantics.

### 3. Cache является ignored per-content optimization, не verification receipt

Cache располагается только в ignored
`.runtime/changerail/public-surface-scan-cache/v1/`. Она не входит в scanner
JSON output, manifest, review evidence или publish authority.

Cache key вычисляется как SHA-256 canonical tuple:

```text
cache_schema
scanner_policy_digest
git_object_format
blob_oid
sha256(exact_repo_relative_path UTF-8 bytes)
```

`scanner_policy_digest` включает cache schema/version и SHA-256 exact tracked
`scripts/public-surface-scan.py` bytes. Поэтому изменение regex, allowlists,
decoder/binary behavior, scan functions или cache implementation делает все
старые entries miss. Blob OID инвалидирует content changes; exact path digest
инвалидирует rename/path-policy changes. Fresh occurrence enumeration
автоматически добавляет новые refs/blobs и перестаёт материализовать удалённые.
Digest current refs может выводиться только как internal timing diagnostic; он
не является ключом reusable whole-run result.

Entry хранит canonical key fields, normalized findings без commit ref и
SHA-256 canonical payload envelope. Reader проверяет schema, all key fields,
envelope digest, types, allowed finding fields, redacted secret value и bounds
до использования. Missing, truncated, malformed, mismatched или oversized
entry считается cache miss и пересканируется из Git object. Atomic write идёт
через private temporary file, `fsync` и replace. Cache read/write permission
failure отключает reuse для entry и выполняет scan; невозможность прочитать Git
object остаётся hard failure. Corruption никогда не превращается в pass.

### 4. Smoke registry становится явным и process-isolated

Оба smoke получают статический ordered registry стабильных case IDs. Registry
явно перечисляет каждый существующий assertion path; отсутствие/duplicate ID
или registry/function mismatch является startup failure. Внутренний child mode
запускает ровно один case или одну явно связанную последовательную group.

Review smoke делится на небольшие semantic groups, потому что часть assertions
намеренно переиспользует предыдущее workspace state:

- helper/core normalization and scope;
- coverage and execution-target negatives;
- risk/complexity boundaries;
- published authorization lineage;
- source-classification and malformed-card cases.

Delivery smoke по умолчанию использует один `check_*` как case. Явные
sequential groups разрешены только когда второй check проверяет state,
созданный первым; dependency фиксируется рядом с registry, а не через общий
temp root. Docs-only checks тоже запускаются как child cases.

Каждый child получает отдельный `TemporaryDirectory`, sanitized inherited env и
собственную process group. Он не видит temp root другого case. Это устраняет
collisions runtime paths, locks, remotes, fake launchers, ports и environment.
Parallelization внутри production runner или одного case не вводится.

### 5. Concurrency и timeout имеют жёсткие bounds

Parent scheduler использует default:

```text
jobs = min(4, max(1, os.cpu_count() or 1), registered_case_count)
```

Internal `--jobs` принимает только `1..8`; invalid value завершает smoke до
запуска cases. Default per-case/group timeout — 300 s для review и 600 s для
delivery; registry может объявить меньший timeout, но не unlimited. Parent при
timeout посылает TERM всей child process group, ждёт до 5 s, затем KILL и
фиксирует case failure. Не запущенные из-за scheduler/internal exception cases
явно считаются failures; success возможен только при terminal result от каждого
registered ID.

Jobs и timeout являются test-runner controls, не новой repository authority и
не способом исключить case. Release baseline вызывает команды без новых flags.

### 6. Parent агрегирует results только в registry order

Child stdout/stderr удерживаются отдельно с per-stream bound 1 MiB. Parent
собирает completion асинхронно, но печатает summary и failures в статическом
registry order. Result содержит только internal `case_id`, terminal status,
exit code, duration и bounded diagnostic; это не tracked schema.

Parent возвращает zero только если получен один successful terminal result для
каждого registry ID. Crash, timeout, duplicate/missing result, invalid result,
oversized output или worker-pool exception возвращает non-zero. На failure
parent всё равно reap-ит все already-started children и не оставляет temp roots
или processes. Completion race не меняет exit code или diagnostic order.

### 7. Acceptance отделяет legacy completeness oracle от scheduler parity

`--jobs 1` остаётся scheduler-parity mode, а не oracle полноты: frozen positive
и negative fixtures запускаются с jobs 1 и default jobs; сравниваются case ID
set, terminal result, exit code и normalized diagnostics. Перед extraction
successor генерирует machine-checkable immutable inventory, anchored к exact
published parent `f03b7052c90c486512d16b308064729dd854657f` blobs
`bc60b3d1561e0cfd5fdd461ca7c057d1039bec0b` (review) и
`e87242a63089751f614a3d33b602ba46d7c4792d` (delivery). AST/source-span
inventory включает каждый top-level scenario/assert block `main()` review smoke
и каждый delivery `check_*` definition плюс invocation из `main()`, с stable
ID, line/column span и SHA-256 exact source bytes. Registry ownership должен
быть exact one-to-one: no gap, duplicate, unknown ID, changed source/span hash
или stale parent blob допустимы не будут. Для каждого registered ID focused test
выполняет fault injection (либо эквивалентную mutation его oracle) и доказывает,
что parent становится red в deterministic registry position. Legacy whole-script
PASS сам по себе недостаточен. Искусственные sleep cases завершаются в разном
порядке и должны выводиться в registry order; crash и timeout одного child
обязаны сделать весь smoke red без зависших processes.

History parity fixture строит commits с unchanged blob, rename, одинаковым blob
под двумя paths, binary/invalid UTF-8, secret-like assignment, new/deleted refs
и corrupted cache. Для current historical `/opt/opsx` fixture обязан ожидать
identical allowed result под обоими paths, одновременно доказывая distinct cache
identities и rename invalidation; он не заявляет несуществующий allowed/disallowed
history result. Legacy uncached oracle и candidate должны вернуть byte-equivalent
normalized findings после исключения только timing/cache counters, которые не
входят в public JSON.

### 8. Timing/RSS gates используют frozen scale и воспроизводимый protocol

History successor фиксирует `history-fixture-v1`: 48 commits, 1152 selected
occurrences, 96 unique `(blob,path)` identities и 72 unique blobs, включая
unchanged, rename, current-policy two-path, binary/invalid UTF-8, secret-like,
ref deletion и corruption cases. Smoke fixture фиксирует exact parent blobs,
their AST/source-span inventory, 44 review workspace-builder calls, 75 delivery
`check_*` functions и 87 delivery workspace-builder calls. Any fixture count or
hash drift creates a new version, not a silently smaller benchmark.

Every evidence run records fixture version/hash, checkout commit, Python and Git
versions, OS/kernel, CPU model/logical count, total RAM and active `--jobs`.
After two discarded warmups, it records five monotonic samples per mode with
fresh temp roots; history uses legacy uncached, empty-cache candidate and its
immediate warm rerun. Median is accepted only when coefficient of variation is
at most 15%; otherwise repeat once and then report not-verifiable. On one host
and fixture, history medians MUST be cold <=20% legacy and warm <=5% legacy;
smoke default-job median MUST be <=60% jobs-1 median. Absolute seconds remain
observational, never portable acceptance limits.

At 100 ms intervals parent samples VmRSS for itself and every live child process
group descendant. Every child MUST have VmHWM <=256 MiB and aggregate sampled
RSS MUST be <=128 MiB + 256 MiB * active job ceiling (<=1152 MiB at default 4,
<=2176 MiB at allowed max 8). Missing process data or an exceeded numeric bound
is red. Timing/RSS evidence is required at successor implementation/review, not
a brittle hard gate in every ordinary baseline run.

### 9. Ordered successor scopes

После публикации decision maintainer создаёт две отдельные cards, но не в этом
FF:

1. `accelerate-path-sensitive-public-history-scan`: scanner/cache/batch reader,
   focused parity/corruption/invalidation/timing fixtures и monotonic per-step
   duration в human-readable baseline output. Timing не меняет pass/fail и не
   является reusable receipt. Successor не меняет smoke parallelization или
   baseline inventory.
2. `parallelize-isolated-release-smoke-cases`: зависит от первого только для
   финального baseline evidence; меняет два smoke registries/schedulers и
   focused isolation/order/crash/timeout/parity/timing fixtures. Он не меняет
   production delivery/review behavior.

Каждый successor обязан пройти focused tests, strict OpenSpec, current public
scan, `git diff --check` и один полный release baseline после своей реализации.
Полный baseline не выполняется в этом planning-only decision.

## Risks / Trade-offs

- [Risk] Неполная path identity даст false green для historical allowlist. ->
  Exact relative path входит в key; rename и same-blob/different-path fixtures
  обязательны.
- [Risk] Cache corruption скроет finding. -> Envelope/key/type validation и
  rescan-on-any-invalid-entry; negative fixture подменяет clean entry.
- [Risk] Batch parser пропустит object/path. -> Сравнение occurrence table и
  findings с legacy oracle, hard failure на malformed/short reads.
- [Risk] Parallel fixtures конфликтуют через global temp/env/port. -> Отдельные
  child process groups/temp roots, ephemeral ports и sanitized env.
- [Risk] Faster failure hides unscheduled cases. -> Success требует terminal
  result каждого registry ID; scheduler exceptions materialize failures.
- [Risk] Fixed jobs overloads small hosts. -> Default capped CPU-aware 4,
  operator override capped 8, sequential jobs 1 remains supported.
- [Risk] Timing fluctuates. -> Five-sample medians on frozen local fixtures;
  semantic gates remain authoritative even when timing evidence is noisy.
- [Trade-off] Exact path in cache duplicates scans across benign renames. ->
  Выбрана safety/parity; 1959 pairs всё равно на два порядка меньше 102706
  occurrences.

## Migration Plan

1. Publish этот decision после independent review без production changes.
2. Реализовать и проверить history successor, включая cold/warm evidence и
   полный baseline.
3. Реализовать smoke successor, включая sequential/parallel parity, exact
   standalone timings и полный baseline.
4. Rollback каждого successor — удалить internal optimization и вернуться к
   sequential implementation; baseline inventory и mandatory commands не
   меняются.

## Open Questions

- none
