## Context

Published decisions at
`ccccb62562e1646b595119edd3326763860f14a7` and
`c2c145ce4d107a8dfcd30603f46e46641c2009c0` freeze the public-history
semantics, safe-parent oracle, `48/1152/96/72` scale, cold `<=20%`, warm
`<=5%`, population-CV and RSS rules. They do not publish the exact recipe that
produced `history-fixture-v1`; a fingerprint and counts cannot serve as a
generator specification or SHA-256 preimage.

The unpublished clean successor stopped before review because this missing
preimage made the required benchmark independently unverifiable. Its card and
Git status are status facts only. Its code, tests, OpenSpec artifacts, cache,
runtime records, benchmark output and other evidence are not inputs to this
decision or any later successor.

The independent legacy source remains exact published scanner blob
`74b218d8d92274d73ffaea129404749a330e8320` at `ccccb625`, whose exact file
bytes have SHA-256
`bd353167a9a3460047c4b25ef41827709bd2304b5b72945d244ffac01094bd6d`.
The safe baseline-runner blob is
`01e8fac656f359077f65a26b508a74ada389ce89`, raw SHA-256
`ab42c91b2951d8e530123602dd9cddc5895ff090a0689ff80ee54dd1314d1317`.

## Goals / Non-Goals

**Goals:**

- Определить materializable tracked preimage для `history-fixture-v2` до
  создания scanner candidate.
- Сделать Git realization независимой от absolute root, host config,
  filesystem order, clock и randomness.
- Закрепить fixture, legacy oracle, harness и verdict arithmetic отдельными
  pinned digests без circular/self reference.
- Сохранить exact scale, semantic cases, thresholds, CV/RSS и trial protocol,
  одновременно запретив favorable selection или перенос authority в candidate.
- Разделить fixture publication, bounded authorization и implementation на три
  ordered successors с exact fail-closed preflight reference.

**Non-Goals:**

- Восстановление, подбор preimage или повторное использование
  `history-fixture-v1` для будущего GREEN.
- Чтение или перенос остановленного successor code/tests/evidence.
- Реализация recipe, materializer, harness, scanner, cache или baseline timing в
  этом change.
- Создание successor cards, archive, verdict, commit или push.
- Запуск history scan, benchmark или полного release baseline.
- Изменение consumer CLI/wire schema, runtime authority, baseline inventory,
  scanner semantics или smoke parallelization.

## Decisions

### 1. v1 остается историческим, а v2 получает новый tracked preimage

`history-fixture-v1` сохраняется как published historical record и объясняет
происхождение scale/thresholds, но больше не может подтверждать GREEN. Его
fingerprint
`sha256:4575cd8b42082d57c25cf474427579c3559aa8a5b3989413a91c40a876c5cf28`
и `48/1152/96/72` не определяют bytes, commit graph, refs или generation order.

Первый successor `materialize-public-history-benchmark-fixture-v2` публикует до
candidate следующие exact paths:

```text
schemas/changerail-public-history-fixture-recipe-v2.schema.json
fixtures/public-history-v2/recipe.json
fixtures/public-history-v2/materialize.py
fixtures/public-history-v2/realization.jsonl
fixtures/public-history-v2/authority.json
fixtures/public-history-v2/benchmark.py
fixtures/public-history-v2/selftest.py
```

Эти paths являются одной indivisible verification fixture. Production scanner,
runtime cache, consumer templates и release baseline не читают recipe или
authority при обычном запуске. Поэтому fixture format не является новым
consumer wire protocol или publish authority.

Alternative "дописать generator вокруг v1 digest" отвергнута: digest не задает
preimage. Alternative "создать recipe внутри candidate" отвергнута: candidate
смог бы выбрать workload под собственную реализацию.

### 2. Recipe schema фиксирует данные, а не алгоритм их выдумывания

`schemas/changerail-public-history-fixture-recipe-v2.schema.json` имеет schema
id `changerail.public-history-fixture-recipe.v2`. Loader обязан reject duplicate
JSON keys, unknown fields, non-canonical base64, unresolved IDs и duplicate IDs
до любого `git` process или filesystem mutation. Exact tracked recipe bytes
пинятся отдельно; canonical reserialization не заменяет digest exact bytes.

`recipe.json` содержит только следующие ordered inputs:

- exact `schema`, fixture id `history-fixture-v2` и единственный object format
  `sha1`;
- ordered identities с explicit base64 name/email bytes;
- ordered blobs с explicit canonical RFC 4648 base64 bytes; binary и invalid
  UTF-8 content записываются буквально, без seed, compression или formula;
- ровно 48 ordered commits: stable ID, ordered parent IDs, author/committer ID,
  integer Unix seconds, timezone `+0000`, exact base64 message bytes и ordered
  file operations;
- каждая file operation задает `add` или `delete`, exact base64 path bytes,
  а `add` также задает exact mode из `100644|100755|120000` и blob ID;
- ordered ref operations с sequence, `update|delete`, exact base64 ref bytes и
  target commit ID для `update`; add/delete order не выводится из final refs;
- ordered semantic-case IDs и expected outcomes;
- exact expected counts: 48 commits, 1152 selected occurrences, 96 unique
  `(blob,path)` identities и 72 unique blobs.

Все path/ref/content/message bytes находятся в recipe. Timestamp, timezone,
identity, parent order, tree mode, ref order и deletion не берутся из clock,
locale, hostname, UUID, random, directory enumeration или Git defaults. Schema
запрещает dynamic expressions, seeds и "repeat N" shortcuts: published recipe
сам является complete ordered raw-byte preimage.

Semantic-case set остается exact:

```text
unchanged-blob
rename
same-blob-two-path
binary-content
invalid-utf8-content
secret-like-assignment-and-redaction
ref-add
ref-delete
cache-corruption
```

Current historical `/opt/opsx` behavior ожидает одинаковый allowed result для
обоих paths, но distinct `(blob,path)` identities и rename invalidation. Recipe
не меняет scanner policy ради создания искусственной allowed/disallowed пары.

### 3. Materializer строит raw Git objects детерминированно

`materialize.py` принимает только pinned recipe, новый empty destination и
explicit transcript path. Он fail-closed проверяет schema и counts, создает
SHA-1 repository, затем строит blob/tree/commit object bytes напрямую и пишет
их через bounded Git plumbing. Tree entries сериализуются по Git byte ordering;
commit bytes содержат exact tree, ordered parent headers, identities,
timestamps/timezone и message bytes из recipe. Каждый returned OID и object type
проверяется до продолжения. Ref operations выполняются по одному в recipe order
и после каждого шага читаются обратно; delete не схлопывается с final snapshot.

Inherited environment очищается и строится allowlist: `LC_ALL=C`, `LANG=C`,
`TZ=UTC`, `GIT_CONFIG_NOSYSTEM=1`, isolated `HOME`/`XDG_CONFIG_HOME`, disabled
prompts/hooks/signing/replacement refs и explicit object/ref format. `GIT_*`,
`SSH_*`, credentials, user config, alternates, grafts и replace refs не
наследуются. Materializer не обращается к network и не вызывает clock/random.

Canonical `realization.jsonl` использует UTF-8 ASCII-escaped JSON, sorted object
keys, compact separators и один LF на record. Record order exact: header,
recipe operations, realized blobs, trees, commits, per-step refs, final refs,
ordered selected occurrences, counts, normalized legacy output digest and final
summary. Raw bytes представлены canonical base64. Absolute root, inode, mtime,
temporary path, process ID и host metadata запрещены в transcript.

Fixture publication создает два different fresh absolute roots A/B, выполняет
materializer independently и требует:

- byte-identical `realization.jsonl` через `cmp`;
- identical ordered object/ref/path records and exact `48/1152/96/72` counts;
- identical normalized legacy output bytes/digest;
- identical domain-separated fixture fingerprint
  `sha256(b"changerail.public-history-fixture.v2\\0" + transcript_bytes)`.

Не требуется byte-identical `.git` directory: authority описывает authentic Git
objects, refs и observable fixture, а не filesystem metadata.

### 4. Detached authority pins every component without self-reference

`authority.json` имеет exact closed shape with schema
`changerail.public-history-fixture-authority.v2`, fixture id, expected counts,
fixture fingerprint, legacy-oracle identity и ordered component rows. Rows
пинят exact path и lowercase SHA-256 exact tracked bytes отдельно для:

```text
recipe-schema
recipe
materializer
realization-transcript
benchmark-harness
authority-selftest
```

Каждый row имеет собственный digest; path/digest нельзя переиспользовать для
другого component id. Ни один pinned file не содержит собственный digest,
`authority.json` не содержит digest самого себя, а transcript не содержит свой
digest или fixture fingerprint. Это устраняет self-reference.

После публикации fixture второй successor
`authorize-bounded-public-history-scan-replacement-v2` пинит published fixture
commit, exact `authority.json` path и SHA-256 authority bytes. Таким образом
authority file получает внешний anchor только в более позднем published
artifact; его не нужно менять после вычисления digest. Missing, untracked,
modified, duplicate, wrong-path или digest-mismatched component делает fixture
invalid до candidate execution.

### 5. Legacy oracle независим от candidate

Materializer/harness извлекает scanner только из exact
`ccccb62562e1646b595119edd3326763860f14a7:scripts/public-surface-scan.py`,
проверяет Git blob OID `74b218d8d92274d73ffaea129404749a330e8320` и raw SHA-256
`bd353167a9a3460047c4b25ef41827709bd2304b5b72945d244ffac01094bd6d`,
затем запускает эти bytes отдельным process с sanitized environment и empty
legacy cache. Oracle не import-ит candidate, stopped successor, current scanner
helper или candidate normalizer.

Pinned pre-candidate harness канонизирует только published output contract;
normalization не удаляет findings, ref/path/order, exit status или diagnostics.
Candidate и legacy получают один materialized root snapshot. Their normalized
output bytes, exit code, ordered finding fields and legacy digest must be
identical. Exhausted/stopped output and prior GREEN prose are never oracle.

### 6. Harness and self-tests are part of fixture authority

`benchmark.py` is published before candidate and accepts only an explicit
candidate script path plus pinned authority. It verifies every component digest,
materializes two roots, checks transcript equivalence and oracle parity, then
runs the frozen benchmark. Candidate cannot supply another recipe, materializer,
oracle, normalizer, transcript, harness, timer or verdict calculator.

`selftest.py` is also pinned and must prove connected RED for at least:

- duplicate/unknown/missing recipe fields, invalid base64/mode/path/ref,
  unresolved parents/blob IDs and wrong exact counts;
- tampering each pinned component, authority path/digest substitution,
  self-digest injection and changed root leaking into transcript;
- wrong legacy commit/blob/raw digest, candidate import into oracle and changed
  normalized output;
- omission or reorder of every semantic case, commit/file/ref operation and
  object/ref/path transcript record;
- sample count/order, warmup, timer boundary, cache, median, population CV,
  threshold and rerun mutations;
- missing/partial RSS samples, child VmHWM or aggregate bound breach;
- selective sample deletion, rounding before verdict, favorable set selection,
  alternate candidate flag/env and authority modification.

Self-tests use synthetic duration/RSS rows and short fake processes for verdict
logic; they do not make a prior benchmark PASS reusable. The materialization
successor must run them plus the real two-root/legacy realization before it is
reviewed and published.

### 7. Scale, benchmark protocol and no-gaming rules remain immutable

v2 changes preimage authority only. It preserves exact scale
`48/1152/96/72`, semantic cases, candidate/legacy workload, public output,
timed process boundary and numeric policy from v1.

Each complete trial uses a new fixture root. The timer starts immediately
before scanner process spawn and stops only after process exit plus complete
stdout/stderr collection. Fixture construction, authority verification, empty
cache preparation, host metadata and RSS post-processing remain outside the
timer. Exact within-trial order is legacy uncached, candidate empty-cache cold,
then immediate candidate warm without Git/policy/cache mutation.

Exactly two complete warmup trials are discarded, followed by exactly five
measured complete trials. Median and population CV use unrounded monotonic
seconds. Cold/legacy median MUST be `<=0.20`; warm/legacy MUST be `<=0.05`.
When every mode CV is `<=0.15`, rerun is forbidden. Otherwise the entire first
five-trial set is discarded and exactly one complete replacement set runs; no
row/set may be selected by outcome. Second instability is `NOT-VERIFIABLE`.
Stable threshold failure is terminal and cannot be retried.

Each measured scanner/Git child has VmHWM `<=256 MiB`. Parent samples itself
and every process-group descendant at 100 ms; sequential history benchmark has
active job ceiling 1 and aggregate RSS `<=128 MiB + 256 MiB`, i.e. `<=384 MiB`.
Missing child/interval/sample data or exceeded bound is red. Evidence records
fixture authority/fingerprint, candidate checkout/fingerprint, Python/Git,
OS/kernel, CPU/logical count, RAM, exact environment controls, all raw samples
and the single deterministic verdict.

No manual cache priming, hidden reuse, affinity/priority difference, alternate
candidate flags, workload reduction, changed refs, timer movement, rounding,
sample deletion, threshold rewrite, fallback oracle or best-of-N selection is
allowed. Runtime evidence stores samples/host data but never defines fixture
bytes or authority.

### 8. Successors are ordered fixture -> authorization -> implementation

No successor card is created by this decision. After this decision has fresh
independent review and publication, maintainers proceed strictly:

1. `materialize-public-history-benchmark-fixture-v2` publishes and reviews the
   seven fixture paths, two-root transcript equivalence, legacy oracle output,
   detached digests and self-tests. It creates no scanner candidate.
2. `authorize-bounded-public-history-scan-replacement-v2` is created only after
   fixture publication. It pins the published fixture commit and authority
   digest and publishes exactly one six-field authorization object:

```json
{"investigation_card":"openspec/board/4.done/investigate-materialized-public-history-benchmark-v2.md","investigation_id":"investigate-materialized-public-history-benchmark-v2","successor_card":"openspec/board/3.inprogress/deliver-path-sensitive-public-history-scan-replacement-v2.md","successor_id":"deliver-path-sensitive-public-history-scan-replacement-v2","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}
```

3. `deliver-path-sensitive-public-history-scan-replacement-v2` is created only
   after authorization publication. Its card declares only this exact reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-public-history-scan-replacement-v2.md","authorization_id":"authorize-bounded-public-history-scan-replacement-v2"}
```

Preflight must resolve both cards as unchanged tracked `4.done` artifacts,
verify reciprocal investigation/successor IDs and paths, return authorization
status `valid`, ceiling `301` and protocol allowance `false`. The implementation
has a stricter acceptance ceiling of `<=300` added production LOC relative to
exact `ccccb625`, so line 301 is not deliverable; 301 exists only as the least
schema-valid authorization ceiling for the repeated-defect guard. New authority
or wire protocol remains forbidden.

The candidate starts from published authorization lineage, but production
semantics and LOC compare only against exact safe `ccccb625`. It may not copy or
read stopped successor code/tests/evidence, modify any fixture-authority path,
or create its own fixture/harness. Same-card repair/rescue remains `0/0/0`;
initial `NO-GO`, stable threshold failure, over-300 LOC, authority mismatch or
missing proof is terminal.

`parallelize-isolated-release-smoke-cases` remains blocked until the v2
implementation publishes after complete focused/current/authentic-history/
benchmark/full-baseline GREEN and fresh independent `GO`.

### 9. This decision has zero executable scope

The current payload changes only the todo card and
`openspec/changes/decide-materialized-public-history-benchmark-v2/`. Its
production/test/runtime LOC is exactly zero. Apply syncs one release-CI delta,
archives this one decision and prepares it for review; it does not create
fixture/successor files or execute the future verification floor.

## Risks / Trade-offs

- [Risk] Recipe may be complete syntactically but omit a semantic edge. ->
  Explicit case IDs, exact counts, legacy output digest and connected per-case
  self-test mutations are all mandatory.
- [Risk] Host Git config changes objects or refs. -> Raw object construction,
  exact bytes, sanitized environment, OID/type readback and two-root transcript
  equivalence fail closed.
- [Risk] Detached digest file can be edited with components. -> Later published
  authorization pins its exact path, commit and SHA-256; candidate cannot edit
  either source.
- [Risk] Shared normalization could conceal parity differences. -> Harness is
  pre-candidate and pinned; self-tests mutate each retained field/order and
  prove RED.
- [Risk] 301 authorization could be mistaken for implementation allowance. ->
  Card/spec acceptance independently requires `<=300`; preflight ceiling 301
  only satisfies the authorization schema/repeated-defect chain.
- [Trade-off] v2 bytes differ from v1. -> Exact v1 bytes are unknowable; scale,
  semantics and acceptance policy remain fixed while v2 becomes reproducible.

## Migration Plan

1. Deliver, sync, archive, independently review and publish this decision-only
   change without executable files or performance evidence.
2. Create and publish only the fixture materialization successor; record its
   exact published commit and authority SHA-256.
3. Create and publish only the exact authorization successor with ceiling 301,
   protocol false and the pinned fixture source.
4. Create the v2 implementation candidate with the exact authorization
   reference, unchanged fixture authority and `<=300` production LOC.
5. Run the indivisible candidate verification floor once focused/self-tests and
   canonical benchmark are GREEN; publish only after fresh independent review.
6. Only then unblock smoke parallelization. Before candidate publication,
   rollback removes later fixture/auth artifacts; stopped v1 payload is never a
   rollback source.

## Open Questions

- none
