## Context

Published commits `ccccb62562e1646b595119edd3326763860f14a7`,
`c2c145ce4d107a8dfcd30603f46e46641c2009c0` и
`f6b56f11593e56fddbd6a718f6abe5418ade9129` последовательно зафиксировали
safe scanner baseline, первый replacement decision и fixture-v2 decision.
Published certification `3915f54f017e3bf7b9af785f62519a87b75f9b9c`
сохранила terminal history evidence. Unpublished fixture-v2 implementation и
оба его `NO-GO` verdict остаются forensic-only: их code, recipe, transcript,
cache и runtime evidence нельзя копировать в новый candidate или публиковать.

Fixture-v2 пытался превратить performance в воспроизводимый admission oracle с
tracked recipe/transcript authority, cold/warm ratios, CV replacement rule и
descendant-RSS bounds. Это создало отдельный сложный verification product и не
доказало основной bounded property scanner: число Git process launches не
растёт вместе с history. Новый contract убирает эту authority и проверяет
algorithmic shape непосредственно на real Git.

Этот change является только решением. Он меняет board/OpenSpec/spec
documentation и не редактирует `scripts/public-surface-scan.py`,
`scripts/run-release-baseline.py`, `.github/workflows/release.yml`, tests,
fixtures, schemas или runtime state.

## Goals / Non-Goals

**Goals:**

- Зафиксировать fresh reachable-history traversal с двумя Git children: один
  `git rev-list --all` и один persistent `git cat-file --batch`.
- Ограничить reuse одним invocation и доказать exact coverage независимо от
  candidate traversal.
- Сохранить legacy findings semantics на малых real-Git repositories и
  fail-closed на всех malformed/missing/mistyped/unsafe inputs.
- Отделить correctness admission от elapsed-time, CV и RSS thresholds.
- Связать exact future authorization и implementation lineage с bounded LOC и
  protocol prohibition.

**Non-Goals:**

- Не создавать cross-run cache, fixture recipe, realization transcript,
  benchmark authority, sample-selection rule или descendant-RSS oracle.
- Не удалять и не переписывать published cards, archived changes,
  certification или retained forensic evidence.
- Не создавать successor cards и не реализовывать scanner/tests/CI в этом
  change.
- Не выполнять history scan, benchmark, full baseline, archive, review, commit
  или push во время FF/decision delivery.
- Не вводить новый public schema, CLI output, evidence wire protocol или
  mutation authority.

## Decisions

### 1. Fresh invocation имеет ровно два Git child launches

Каждый production history run безусловно запускает fresh
`git rev-list --all`, строго разбирает весь ordered commit stream, затем
запускает ровно один long-lived `git cat-file --batch`. Scanner не читает
результат прежнего запуска и не проверяет persistent cache до reachability.
После последнего запроса stdin batch child закрывается, весь ответ и process
status проверяются, и успешный report разрешён только при exit `0` обоих
children.

Exact history-mode Git launch count равен `2`, независимо от числа commits,
trees, blobs, refs и occurrences. Нельзя добавлять `git ls-tree`, `git show`,
`git cat-file` per object, object-format discovery child или другой скрытый Git
subprocess. Нужные object type/size/body данные проходят через единственный
batch session.

Альтернатива с `ls-tree`/`show` per commit/path отвергнута, потому что process
count растёт с history. Persistent daemon или cache между invocations также
отвергнуты: они делают correctness зависимым от stale mutable state.

### 2. Memoization существует только в памяти одного invocation

Invocation-local object memo keyed by exact OID сохраняет validated Git object
type и raw bytes после первого batch response. Один commit, tree или blob OID
не запрашивается повторно в том же batch session. Отдельный scan memo keyed by
exact `(blob OID, repository-relative path)` сохраняет policy result; selected
identity сканируется не более одного раза.

Occurrence list при этом не дедуплицируется. Scanner сохраняет ordered actual
`(commit,path,blob)` occurrences и после единственного scan каждой
`(blob,path)` identity детерминированно разворачивает findings на все reachable
commit occurrences в `rev-list`/raw-tree order. Одинаковый blob под двумя exact
paths является двумя scan identities. Rename, path case и raw path bytes не
нормализуются и не объединяются.

Memo живёт только в process memory и уничтожается при exit. Future delivery не
добавляет cache directory/file, cache key/version, environment/CLI cache
control, recipe, materializer, transcript, detached authority или retained
warm state.

Scanner не изменяет refs, worktree contents или Git index. Connected test вне
counted candidate `PATH` до и после каждого successful и fault-injected run
снимает exact oracle: полный ref namespace (refname, direct/symbolic target и
peeled target), exhaustive worktree mapping repository-relative path,
file type/mode и raw bytes, а также exact raw bytes Git index. Каждый
соответствующий before/after component обязан быть byte-for-byte identical;
oracle не выводит expected state из candidate output, memo counters или
persistent cache.

### 3. Все Git framing и path данные разбираются strict fail-closed

`rev-list` parser принимает только empty stream для repository без reachable
refs либо complete LF-terminated records с одним supported full OID в каждой
строке. Empty interior record, whitespace, abbreviated/non-hex OID, duplicate
unexpected framing, missing final LF, stderr/exit failure или truncation
останавливает scan до successful report.

Batch parser связывает каждый request с ровно одним response и принимает
только complete `<oid> <type> <size>\n<body>\n` framing с exact requested OID,
expected `commit|tree|blob` type, canonical non-negative decimal size, exact
body length и final LF. `missing`, malformed header, oversized/truncated body,
unexpected type/OID, unsolicited/duplicate response, premature EOF, broken
pipe или nonzero child exit являются hard failure.

Commit parser требует корректный raw commit header block и ровно один valid
`tree` OID. Raw tree parser требует полные entries `mode SP raw_name NUL oid` с
valid mode/type relationship and full OID. Каждый `raw_name` проверяется до
prefixing: он non-empty, strict UTF-8 round-trips unchanged, не содержит NUL,
slash, backslash, ASCII control/DEL и не равен `.` или `..`. Joined path не
может быть absolute, выйти из repository-relative namespace или попасть в
skip/select policy через normalization. Missing/mistyped objects, unsafe path,
tree cycle и contradictory duplicate object data fail closed.

Scanner буферизует result и не выдаёт partial success/findings как terminal
report до полной проверки reachability stream, batch responses и обоих child
exits. Binary или non-UTF8 blob content сохраняет legacy ignore semantics, но
не ослабляет framing/type/path errors.

### 4. Structural tests доказывают constant process bound и actual coverage

Connected test создаёт два малых temporary real-Git repositories: small и
enlarged с большим числом commits, trees, refs, duplicate blobs, repeated paths
и renames. Для запуска candidate `PATH` начинается с executable wrapper `git`,
который записывает каждый argv и `exec`-ит pinned real Git. Для обоих размеров
лог обязан содержать exact count `2` и только один `rev-list --all` плюс один
`cat-file --batch`; enlarged history не меняет count.

Этот connected test применяет описанный before/after state oracle к каждому
candidate run, включая injected fault runs. Oracle запускается вне counted
candidate `PATH`, поэтому его independent Git inspection не меняет exact
two-child count candidate и не может опираться на candidate evidence.

Отдельный verifier запускается вне counted candidate PATH и сам получает
ordered commits через real `git rev-list --all`, затем actual entries через
real `git ls-tree -r -z --full-tree` для каждого commit. Он strict разбирает
output собственной простой логикой и строит ordered selected
`(commit,path,blob)` tuples. Exact tuple list сравнивается с test-only traversal
observer candidate, а не выводится из candidate findings, memo counters или
synthetic expected counts. Test-only observer не становится production CLI,
schema или wire authority.

Малые real-Git cases сравнивают normalized candidate output с exact legacy
scanner `ccccb625:scripts/public-surface-scan.py` для allowed/leak/redaction,
rename и path identity, binary/NUL и non-UTF8 blob content. Connected fault
wrapper делегирует real Git и затем injects malformed, truncated, mistyped,
missing и unsafe batch/path bytes; каждый case требует nonzero result без
partial success. Эти ephemeral repositories и injectors являются tests, не
tracked benchmark recipe/transcript/authority.

### 5. Performance evidence является observational

Correctness PASS определяется focused parity/fault tests, constant exact child
count, independent tuple equality, strict validation, current scan, final
history scan и full release baseline. Ни wall-clock duration, ни warm ratio,
ни median/CV, ни process/descendant RSS threshold не могут изменить verdict,
разрешить retry или выбрать favorable sample.

`/usr/bin/time -v` записывает elapsed time и maximum resident set size только
как observational metadata. На неизменном exact implementation payload после
focused gates delivery выполняет ровно один standalone final
`python3 scripts/public-surface-scan.py --history` и ровно один
`python3 scripts/run-release-baseline.py`. Внутренний history step полного
baseline является частью единственного baseline invocation, а не отдельным
benchmark sample. Failure любого correctness command останавливает candidate;
timing/RSS не превращает failure в PASS и не разрешает rerun того же payload.

### 6. CI обязан предоставить полный reachable history

Release CI job, который запускает public-history scan или full baseline,
использует checkout с exact `fetch-depth: 0` до scan. Shallow clone, single-ref
checkout или отсутствующие reachable refs не могут считаться доказательством
полноты `--all`; connected workflow smoke проверяет этот contract.

### 7. Authorization и implementation имеют exact ordered lineage

После публикации этого decision с GO создаётся и отдельно публикуется только
`authorize-bounded-structural-public-history-scan`. Его authoritative
tracked-`4.done` source обязан содержать exact six-field object:

```json
{"investigation_card":"openspec/board/4.done/investigate-structural-public-history-scan-proof.md","investigation_id":"investigate-structural-public-history-scan-proof","successor_card":"openspec/board/3.inprogress/deliver-structurally-bounded-public-history-scan.md","successor_id":"deliver-structurally-bounded-public-history-scan","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}
```

Только после remote-reachable authorization publication создаётся
`deliver-structurally-bounded-public-history-scan`. Его `Published
investigation authorization` содержит exact two-field reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-structural-public-history-scan.md","authorization_id":"authorize-bounded-structural-public-history-scan"}
```

Deterministic preflight проверяет reciprocal IDs/paths, clean tracked `4.done`
source, status `valid`, ceiling `301` и protocol allowance `false`. Независимый
implementation acceptance ограничивает total added production code значением
`<=300` LOC относительно exact
`ccccb62562e1646b595119edd3326763860f14a7`; строка 301 не deliverable и нужна
только как минимальный authorization-gate ceiling. Любой новый authority/wire
protocol, >300 production LOC, другой baseline или mismatch останавливает
delivery.

После implementation GREEN и publication создаётся
`parallelize-isolated-release-smoke-cases`; phase-routed runner series
возобновляется только после неё. Никакой successor не создаётся этим decision
change.

## Risks / Trade-offs

- **[Risk] Structural bound не обещает конкретную длительность.** -> Exact
  process bound, object/path memo counts и actual tuple equality являются
  admission gates; `time -v` сохраняет trend data без unstable threshold.
- **[Risk] Invocation-local memo потребляет память пропорционально unique
  reachable objects/paths.** -> Design запрещает недоказуемый RSS oracle, но
  сохраняет observable max-RSS и bounded one-fetch/one-scan invariants; рост,
  неприемлемый на реальном final run, требует нового решения, а не benchmark
  selection.
- **[Risk] PATH wrapper может посчитать verifier children.** -> Candidate и
  independent verifier запускаются отдельно; exact count относится только к
  candidate process environment, verifier использует resolved real Git вне
  wrapper.
- **[Risk] Strict parser отклонит unusual repository data.** -> Это намеренный
  fail-closed public-safety contract; unsafe or unsupported data не может дать
  false PASS.
- **[Risk] Historical fixture-v2 prose остаётся в archives/main history.** ->
  Оно сохраняется как forensic lineage, но modified current requirements явно
  запрещают использовать его как future implementation authority.

## Migration Plan

1. FF публикует только apply-ready decision artifacts; DO позже sync-ит delta
   spec и архивирует decision без scanner/evidence execution.
2. После fresh ordinary review GO и publication этого decision создать и
   publish exact authorization card.
3. После authorization publication создать implementation card, реализовать
   scanner, focused real-Git tests и checkout contract в пределах `<=300`
   production LOC against `ccccb625`.
4. На exact candidate выполнить focused structural gates, один standalone final
   history scan и один full baseline с observational `time -v`, затем fresh
   independent review и scoped publication.
5. После published GREEN продолжить smoke parallelization, затем
   phase-routed runner series.

Rollback для future implementation возвращает production behavior к exact
`ccccb625`; unpublished fixture-v2 implementation и stopped successors не
являются rollback source.

## Open Questions

Нет. Exact child count, parser boundary, verification oracle, LOC ceiling,
authorization identity и successor order фиксированы этим decision.
