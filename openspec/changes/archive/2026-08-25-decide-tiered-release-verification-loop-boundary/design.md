## Context

Published acceleration decision `ccccb625` оставила все 36 process steps
mandatory и разрешила только internal optimization. Published Git-header rescue
`b7bd6f7` и authorization `45a2de9` затем подготовили clean structural scanner,
но terminal forensic summary показал другой dominant failure mode: baseline
выполнил дорогие Windows checks и только на десятом process step обнаружил, что
worktree-local pinned `ruff` недоступен. Terminal code, diff и raw evidence в
это решение не переносятся.

Текущий baseline также запускает `smoke-windows-entrypoints.py`,
`smoke-windows-wiring-git-safety.py`, `smoke-bootstrap-project.py` и
`smoke-verify-project.py` отдельно, а затем повторяет те же четыре scripts как
children шестипунктовой local Windows matrix. Проверки нужны, повторные
processes нет. Решение поэтому явно supersede-ит прежний process-invocation
non-goal, но сохраняет полный semantic coverage и запрет whole-baseline cache.

## Goals / Non-Goals

**Goals:**

- Отклонять unusable release toolchain до первого semantic child.
- Заменить command-string inventory frozen semantic IDs с exactly-one owner.
- Выполнять шесть local Windows cases bounded-concurrently в isolated roots и
  удалить четыре standalone duplicates без потери assertions.
- Отделить cheap non-authoritative affected inner loop от единственного
  authoritative full-release profile.
- Сохранить default local Windows gate полностью offline относительно host
  inventory и оставить live checks explicit operator gate.
- Разделить tiered orchestration, isolated `verify-project` cases и clean
  scanner v2 на три bounded, independently authorized implementation lineage.

**Non-Goals:**

- Отключать public-surface, history, review, delivery, Windows или consumer
  checks в full-release profile.
- Делать affected selection publish authority или reusable full-suite cache.
- Запускать Windows live hosts из local baseline или CI.
- Параллелить произвольные top-level release checks с shared state.
- Менять public-history parser/scanner в tiered implementation.
- Читать, копировать, исправлять или публиковать terminal forensic successor.
- Создавать authorization/implementation cards, менять executable code, main
  spec, CI, archive, review record, commit или remote в этом decision change.

## Decisions

### 1. Admission завершается до первого semantic child

`scripts/run-release-baseline.py` сначала строит environment один раз и
выполняет bounded startup admission. До его полного PASS ни один registry case,
OpenSpec validation, smoke или Windows child не запускается. Admission обязан:

- найти release child Python в effective baseline `PATH`, выполнить bounded
  probe и подтвердить Python `>=3.11`;
- прочитать exact pins из `requirements-runtime.txt` и
  `requirements-dev.txt`, затем тем же child Python подтвердить import и exact
  installed distribution versions `jsonschema==4.23.0`,
  `markdown-it-py==3.0.0`, `PyYAML==6.0.3` и `ruff==0.6.9`;
- подтвердить, что resolved `ruff` принадлежит выбранному release environment,
  исполняется и сообщает exact `ruff 0.6.9`, а не только присутствует в PATH;
- bounded-probe-ить `git`, `node`, `npm` и `npx`, подтвердить exact repository
  root и executable tracked `./bin/openspec`, default pin `1.3.1`, отсутствие
  conflicting `OPENSPEC_VERSION` и usable pinned OpenSpec `--version` через тот
  же npm/npx path;
- проверить наличие, executable/readable state и unique ownership всех frozen
  registry targets до их запуска.

Missing executable/module/package, version/path mismatch, timeout, malformed
probe или unavailable pinned OpenSpec завершают run non-zero с bounded
diagnostic, `semantic_started: 0` и полным списком admission failures. Проверки
не short-circuit-ятся на первом missing tool, но semantic execution начинается
только после aggregate PASS. `which` без version/import probe недостаточен.

### 2. Full-release authority принадлежит 35 leaf semantic IDs

Source of truth является одна ordered registry, а CI contract smoke проверяет
её ownership вместо дублирующего command-string list. Canonical bytes состоят
из следующих IDs, каждый с trailing `LF`; SHA-256 равен
`7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`:

```text
openspec.validation
config.json-parse
config.toml-parse
contracts.schema-validation
python.syntax-inventory
python.runtime-selection
windows.entrypoints
project.bootstrap
project.verify-drift
windows.wiring-git-safety
windows.lab-dry-run
windows.runtime-wiring-dry-run
python.lint
ci.workflow-contract
public-surface.self-test
public-surface.current
public-surface.history
wiring.discovery
runtime.diagnostics
consumer-ci
review.verdict-validation
review.fingerprint
review.fingerprint-benchmark
review.fingerprint-cache
review.preflight
evidence.retained
maintenance.runner
delivery.manifest
delivery.manifest-derive
delivery.runner
delivery.metrics
openspec.archive-diagnostics
drift.generated-fixture
git.whitespace
git.ignored-status
```

Registry entry имеет один stable ID, ровно одного owner и одну direct command
либо explicit sequential group. `drift.generated-fixture` является одной
semantic group для reset, bootstrap и drift assertion. Windows aggregator сам
не получает дополнительный semantic PASS: он владеет ровно шестью leaf IDs.
Duplicate ID/owner, missing/unknown ID, digest drift, result не от declared
owner или отсутствие terminal result fail closed. Human output и diagnostics
всегда агрегируются в указанном order; duration остаётся observational.

Это заменяет правило «каждая прежняя process command обязана быть вызвана».
Полноту теперь доказывает exact leaf registry. Review-preflight и
delivery-runner smoke остаются отдельными mandatory IDs; их ранее принятое
internal isolated parallelization scope не ослабляется.

### 3. Windows matrix владеет шестью isolated local cases

`scripts/smoke-windows-matrix.py` получает exact ordered local registry из
шести IDs `windows.entrypoints`, `project.bootstrap`, `project.verify-drift`,
`windows.wiring-git-safety`, `windows.lab-dry-run` и
`windows.runtime-wiring-dry-run`. Каждый child получает отдельные temp,
runtime, report, stdout и stderr roots, sanitized environment и собственную
process group.

Internal `--jobs` принимает только `1..8`; default равен
`min(4, max(1, os.cpu_count() or 1), 6)`. Каждый case имеет finite timeout не
больше `900 s`, stdout и stderr bounded по `1 MiB` на stream. Timeout, crash,
malformed/duplicate result, oversized output или scheduler exception ведут к
TERM всей child group, grace не больше `5 s`, затем KILL/reap и non-zero matrix
result. Parent завершает/reap-ит уже запущенные children и материализует один
terminal result для каждого ID; completion race не меняет registry-order
output.

Focused fixtures выполняют exact registry с `--jobs 1` и default jobs,
сравнивают ID set, normalized status/diagnostic order и exit code, а также
проверяют out-of-order completion, invalid jobs, timeout, crash, oversized
output, root/env collision и cleanup. Четыре standalone baseline/CI processes
для entrypoints, wiring Git safety, bootstrap и verify-project удаляются;
соответствующие IDs исполняются exactly once внутри matrix.

### 4. Local и live Windows authority не смешиваются

`full-release` вызывает только default local matrix. Этот mode не открывает
default или explicit inventory path, не разрешает host credentials и не
создаёт network/SSH/WinRM connection. Negative fixture подставляет trap
inventory и network launchers и доказывает нулевой доступ.

Live matrix остаётся отдельным explicit
`smoke-windows-matrix.py --live --inventory <ignored-path>` operator gate. Её
outcome не входит в 35 local full-release IDs, не запускается CI и требуется
только для отдельного Windows-host support claim. `--live` нельзя передать
через release profile или environment override.

### 5. Affected selector всегда non-authoritative и расширяется fail-closed

Canonical CLI имеет default `--profile full-release` и explicit
`--profile affected --base <ref>`. Affected selector один раз получает
NUL-framed status для committed, staged, unstaged и non-ignored untracked paths
от base до current workspace. Add/modify/delete учитывают exact path; rename и
copy учитывают old и new path; multi-area change берёт ordered union IDs.

Base обязан resolve-иться в commit. Invalid/unavailable/non-ancestor base,
malformed Git framing, undecodable path, больше `4096` paths, больше `4096`
bytes на path или больше `8 MiB` aggregate status не дают empty selection, а
переключают effective selection на все 35 IDs. Closed tracked path map назначает
каждому known family один или несколько IDs либо sentinel `full`. Новый или
неизвестный path, ambiguous overlap, selector/registry/toolchain/CI self-change
и изменение `requirements*.txt`, `bin/openspec`, baseline, Windows matrix,
release-CI smoke/workflow или normative release-CI profile contract также
выбирают full inventory.

Даже узкий affected run всегда включает minimum floor:
`openspec.validation`, `public-surface.current`, `git.whitespace` и
`git.ignored-status`; Python paths дополнительно включают syntax/lint. Focused
tests перечисляют каждую tracked path через closed map и отдельно покрывают
A/M/D/R/C, untracked, multi-area, invalid base, bounds, unknown path и every
self-change sentinel. Selector никогда не выполняет command из changed content
до toolchain admission.

Requested profile определяет authority: run, запрошенный как `affected`, имеет
`authoritative: false`, даже если fallback фактически выполнил все 35 IDs.
Affected evidence может ускорять DO/fix inner loop, но review/pub preflight
отклоняет его как full-suite claim.

### 6. Только full-release является review/pub/CI evidence

Full-release выполняет все 35 IDs после admission, fail-fast на первом failed
ordered owner и возвращает non-zero при missing, duplicate, crash, timeout или
non-pass result. Final JSON summary фиксирует requested/effective profile,
authority bit, frozen inventory digest, ordered selected/result IDs,
toolchain probe outcome, fallback reasons и status. Это versioned CLI evidence,
но не reusable command bypass и не cross-run cache.

Review и publish contracts принимают release-suite claim только от exact
`--profile full-release` evidence, связанного существующим manifest/evidence
mechanism с тем же payload fingerprint. `affected`, incomplete inventory,
другой digest, changed payload или unretained/unparseable summary являются
missing mandatory evidence. Existing unchanged-payload evidence reuse остаётся
допустимым только там, где lifecycle contract уже разрешает его; оно не
разрешает пропустить один predeclared final full-release capture implementation
lineage. CI вызывает canonical runner только с `--profile full-release`, а
`smoke-release-ci.py` проверяет profile и semantic inventory, не legacy
standalone commands.

Для каждого executable successor final full-release capture predeclared,
создаётся один раз после focused GREEN и считается terminal без retry: PASS
разрешает fresh review, FAIL/TIMEOUT требует новой clean repair/replacement
lineage, а не повтор после наблюдения результата. Decision/authorization cards
history и full baseline не запускают.

### 7. Три authorization lineage имеют отдельные baselines и limits

После publication decision сначала создаётся docs-only
`authorize-bounded-tiered-release-verification-loop`. Его единственный
six-field object связывает это investigation с exact successor:

```json
{"investigation_card":"openspec/board/4.done/investigate-tiered-release-verification-loop-boundary.md","investigation_id":"investigate-tiered-release-verification-loop-boundary","successor_card":"openspec/board/3.inprogress/implement-tiered-release-verification-loop.md","successor_id":"implement-tiered-release-verification-loop","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Только после remote-reachable authorization создаётся tiered implementation с
exact two-field source reference. Она добавляет `<=499` production LOC
относительно `45a2de98924c61bb9e944767013ea09918bba4b0`, реализует только
admission/registry/profiles/Windows/CI authority, получает `critical` fresh
Sol/`xhigh` review и не меняет public-history scanner algorithm.

После publication tiered implementation её exact published HEAD становится
новым LOC baseline. Затем отдельная docs-only
`authorize-bounded-parallel-verify-project-cases` связывает это же
investigation с successor `parallelize-isolated-verify-project-cases` через
ceiling `501` и protocol flag `false`:

```json
{"investigation_card":"openspec/board/4.done/investigate-tiered-release-verification-loop-boundary.md","investigation_id":"investigate-tiered-release-verification-loop-boundary","successor_card":"openspec/board/3.inprogress/parallelize-isolated-verify-project-cases.md","successor_id":"parallelize-isolated-verify-project-cases","production_loc_ceiling":501,"allow_new_authority_or_wire_protocol":false}
```

This successor adds `<=500` production LOC relative to exact published tiered
HEAD and defines one static registry for all current approximately 73 assertions and 45 run paths, with frozen
source-span/semantic-ID completeness. Every external case receives one
immutable base fixture and isolated copy-on-write/reflink-or-copy child; pure
in-process validators stay in-process only where the CLI boundary is not under
test. Jobs are `1..8` with default at most `4`, jobs-1/default normalized
parity, deterministic order, bounded timeout/output and child reaping. Minimal
exact-owned end-to-end CLI sentinels remove only semantic duplicates, the closed
path map integrates with affected selection, and no cross-run cache exists.
This successor follows tiered orchestration; scanner-v2 is independent of it
and may use the same exact published tiered HEAD baseline.

После publication tiered implementation отдельная docs-only
`authorize-clean-git-compatible-structural-history-scan-v2` связывает это же
investigation с successor `deliver-clean-git-compatible-structural-history-scan-v2`
через ceiling `301` и protocol flag `false`. Scanner v2 создаётся только после
этой remote-reachable authorization, добавляет `<=300` production LOC
относительно exact published tiered HEAD, сохраняет published Git-header/batch/
no-mutation contracts и не меняет tiered orchestration authority.

Все три authorization cards и implementation cards создаются отдельными
flows, а не fast-forward этого decision. Ceiling `500` не разрешает production
line 500; ceiling `501` разрешает максимум 500 production lines; ceiling `301`
не разрешает line 301. Existing `parallelize-isolated-release-smoke-cases`
remains the separate review/delivery-smoke successor with its semantic
ownership rules.

### 8. Decision review route bounded

Этот docs-only decision имеет `critical` risk, new authority `no`, repeated
defect `no`, production/test/runtime LOC `0`: он описывает и связывает будущую
authority, но не изменяет executable authority или wire behavior. Terminal
repeated defects являются входом simplification investigation, а forensic
implementation не переносится. После Terra/high DO он получает
fresh independent Sol/`xhigh` review. Разрешён максимум один scoped same-card
repair fresh Terra/high и затем fresh Sol/`xhigh` re-review; второй NO-GO
завершает lineage без публикации.

## Risks / Trade-offs

- **[Risk] Semantic ID скрывает потерянную assertion.** -> Frozen ID list,
  exact-one owner, current-script parity fixtures и fault injection делают
  missing/duplicate ownership red.
- **[Risk] Parallel Windows cases делят скрытый global state.** -> Per-ID roots,
  sanitized env/process groups, jobs-1 parity и collision fixture.
- **[Risk] Parallel `verify-project` case теряет assertion.** -> Static
  source-span/semantic-ID completeness covers every current assertion and run
  path; pure validators and CLI sentinels have distinct exact owners.
- **[Risk] Affected map ошибочно omits check.** -> Closed coverage каждой
  tracked path, minimum floor и full fallback на любое unknown/ambiguity/
  self-change.
- **[Risk] Tool exists, но не usable.** -> Admission запускает version/import/
  repository/OpenSpec probes, а не полагается на PATH lookup.
- **[Risk] Affected full fallback ошибочно принимается как authority.** ->
  Authority зависит от requested profile и остаётся false.
- **[Trade-off] Invalid base запускает full suite вместо быстрого отказа.** ->
  Это сохраняет verification coverage; report явно фиксирует fallback reason.
- **[Trade-off] Один terminal full capture повышает цену позднего дефекта.** ->
  Focused jobs-1/default, negative selector и toolchain fixtures обязаны быть
  GREEN до capture; после terminal failure используется clean lineage.

## Migration Plan

1. Deliver, independently review Sol/`xhigh` и publish только этот decision.
2. Создать, publish и remote-verify tiered authorization source.
3. Реализовать tiered orchestration от exact `45a2de9`, выполнить focused
   matrix/selector/admission tests и один terminal full-release capture, затем
   fresh critical review/publish.
4. Создать и publish `verify-project` authorization, затем реализовать bounded
   isolated cases от exact published tiered HEAD.
5. Создать и publish scanner-v2 authorization относительно exact published
   tiered HEAD, независимо от `verify-project` implementation.
6. Реализовать clean scanner v2, выполнить full structural adversarial matrix и
   один terminal full-release capture, затем fresh critical review/publish.
7. После scanner publication продолжить isolated review/delivery smoke
   acceleration и phase-routed authorization chain.

Rollback до публикации сохраняет только published predecessor. После
публикации rollback выбирает предыдущий remote-reachable commit; authoritative
profile или semantic IDs не изменяются без нового decision.

## Open Questions

Нет. Profiles, authority, IDs, Windows ownership, selector fallback,
toolchain admission, lineage order, LOC baselines и review route зафиксированы.
