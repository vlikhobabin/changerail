## Context

Release predecessor прошел полный qualification floor, но final independent
review cycle 3 вернул один process blocker. После normal publish создает clean
payload commit, новая invocation снова начинает с current-worktree verdict
freshness и dirty working-tree manifest scope. Эти gates доказывают состояние
до staging и по определению не могут подтвердить уже закоммиченный clean
payload. Поэтому расположенная ниже idempotent tag/release/assets continuation
недостижима после безопасной остановки.

Final reviewed predecessor tree —
`284d05faa41b13defc0b995cba223ae0600e8edd`, diff fingerprint —
`sha256:ab12bb20f5449b1aeda0d354c990fb4bf8626d07ea8cf9f35fa56d1180971835`.
Same-card rescue budget исчерпан `2/2`; это решение не открывает третий rescue.
Release commit, tag и hosted release отсутствуют.

Exact linked successor `enable-post-commit-release-resume-entry` уже описывает
state-specific entry, но его единый payload поглощает predecessor additions.
Project-owned `.changerail/source-classification.yaml` считает добавленные
строки Python под `scripts/` production, кроме шести exact non-production
paths. Текущий measured baseline относительно опубликованной базы равен 299:

| Path | Added production-counted LOC |
| --- | ---: |
| `scripts/build-source-distribution.py` | 145 |
| `scripts/run-release-baseline.py` | 1 |
| `scripts/smoke-release-ci.py` | 2 |
| `scripts/smoke-source-distribution.py` | 151 |
| **Итого** | **299** |

Даже минимальный committed-manifest helper и focused probes добавят counted
Python lines. Поэтому ordinary ceiling 300 нельзя обойти классификацией или
переносом проверок: сначала требуется это investigation, затем отдельный exact
authorization source.

## Goals / Non-Goals

**Goals:**

- установить точную причину недостижимого post-commit resume entry;
- выбрать минимальную atomic implementation boundary для exact successor;
- связать measured baseline с реалистичным cumulative LOC forecast и hard
  ceiling не выше 400;
- определить separate authorization identity без inline/free-form waiver;
- зафиксировать focused и final-certification verification floor;
- оставить текущий change docs/OpenSpec-only.

**Non-Goals:**

- реализовывать successor, tag/release/assets transaction или workflow;
- создавать authorization-card в этом change;
- менять source classification, manifest/verdict schemas или review limits;
- добавлять provider, credential type, execution target, wire protocol или
  mutation authority;
- ослаблять normal pre-staging gates, тесты или final release qualification;
- переоткрывать predecessor archived changes или расходовать новый rescue.

## Decisions

### 1. Blocker является entry-state mismatch, а не release identity defect

Normal entry остается pre-commit certification path: deterministic preflight,
current-worktree `--check-fresh`, full verification, working-tree parity,
staging и staged parity выполняются перед первым payload commit. Post-commit
resume начинается только после clean exact commit и remote branch equality,
поэтому он не повторяет gates, чьи входные данные уже исчезли.

Resume вместо этого валидирует существующий positive verdict без claim о
freshness текущего clean tree, exact parent/tree lineage, единственный live
`3.inprogress` successor card, clean workspace, committed
`parent..payload`/manifest parity и exact remote feature branch. Только затем
он входит в уже спроектированную idempotent identity machine для tag, hosted
release и assets.

Rejected: ослабить или удалить normal freshness/scope gates. Rejected:
считать clean HEAD новым reviewed state или запускать дополнительный LLM
review. Rejected: продолжать третий same-card rescue predecessor.

### 2. Минимальная successor boundary остается одной atomic fail-closed связкой

Runtime/read-only proof ограничен существующим helper surface:

- `scripts/changerail_delivery_manifest.py` получает `scope-check --target
  committed --commit <payload>`; target требует ровно одного parent и
  сравнивает normalized add/modify/delete/rename operations с существующим
  manifest без изменения его schema;
- `scripts/smoke-delivery-manifest-derive.py` добавляет table-driven exact,
  missing, extra, operation-mismatch, wrong-commit и non-single-parent cases;
- `scripts/smoke-wiring-discovery.py` отдельно наблюдает normal/resume gate
  sets и fail-closed negative marker fixtures.

Canonical operator behavior остается в `skills/changerail-pub/SKILL.md`, а
direct routing — в `skills/changerail-deliver/SKILL.md`. Existing reference
`skills/changerail-do/references/changerail-delivery-manifest.md`,
`docs/release-discipline.md`, `changerail-release-discipline` и
`changerail-skill-surface` синхронизируют тот же contract. Одна stale фраза в
archived predecessor design может быть исправлена без переписывания его
решений. `.github/workflows/*`, schemas и generated wiring не входят в scope.

Эти части atomic, потому что prose routing без committed proof допускает
недоказанный clean commit, а helper без раннего route остается недостижим.
Split допустим только после нового investigation, если ceiling не выполняется;
он не может публиковать половину admission boundary.

### 3. Cumulative forecast равен 359..399, hard ceiling — 400

Forecast использует actual classification, а не net LOC или исключение smoke:

| Incremental surface | Forecast added counted LOC |
| --- | ---: |
| committed target, CLI validation и normalized diff reuse | 30..45 |
| table-driven committed manifest probes | 20..35 |
| wiring gate-set/negative marker probes | 10..20 |
| **Новый incremental subtotal** | **60..100** |
| **Cumulative с measured baseline 299** | **359..399** |

Successor должен консолидировать существующие helpers и fixtures, а не
наращивать параллельную implementation. Future authorization ceiling выбран
равным 400, оставляя максимум 101 новую counted строку поверх baseline.
Preflight measurement `401+` является hard stop для split/new investigation;
нельзя менять `.changerail/source-classification.yaml`, переносить behavior в
docs или удалять regression cases ради прохождения ceiling.

Forecast не является waiver и не утверждает будущий exact count. Единственным
authoritative count остается deterministic review preflight exact successor
working tree.

### 4. Authorization будет отдельным clean tracked source

Exact future authorization id:
`authorize-bounded-post-commit-release-resume-entry-payload`.

Initial path:
`openspec/board/2.todo/authorize-bounded-post-commit-release-resume-entry-payload.md`.

Published path:
`openspec/board/4.done/authorize-bounded-post-commit-release-resume-entry-payload.md`.

После publication этого investigation отдельная authorization-card должна
пройти собственные delivery, independent review и publish и содержать ровно
один six-field object:

```json
{"investigation_card":"openspec/board/4.done/investigate-post-commit-release-resume-entry-boundary.md","investigation_id":"investigate-post-commit-release-resume-entry-boundary","successor_card":"openspec/board/3.inprogress/enable-post-commit-release-resume-entry.md","successor_id":"enable-post-commit-release-resume-entry","production_loc_ceiling":400,"allow_new_authority_or_wire_protocol":false}
```

В `Depends On` этой authorization-card MUST присутствовать exact investigation
id `investigate-post-commit-release-resume-entry-boundary`.

Только затем successor может получить reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-post-commit-release-resume-entry-payload.md","authorization_id":"authorize-bounded-post-commit-release-resume-entry-payload"}
```

В дополнение к reference exact successor MUST объявить тот же investigation id
`investigate-post-commit-release-resume-entry-boundary` в собственном
`Depends On`. Canonical deterministic preflight MUST проверить обе dependency
edges до semantic review и fail closed при missing или mismatched relation.

Ни JSON example в design, ни `Published investigation authorization: none` в
текущей card не являются действующей authorization. Missing, unpublished,
dirty, mismatched или over-ceiling source останавливает review preflight.

### 5. Verification floor наблюдает обе entry states и полный release boundary

Focused RED/GREEN floor exact successor:

- `python3 scripts/smoke-delivery-manifest-derive.py` доказывает committed
  scope parity и isolated wrong-state rejection через production helper;
- `python3 scripts/smoke-wiring-discovery.py` доказывает разные normal/resume
  gate traces и отсутствие pre-commit gates в resume;
- negative cases подтверждают zero mutation при dirty/pre-commit, wrong
  lineage/card/scope/remote и inconsistent release identity.

Final-certification floor выполняется на одном frozen successor tree и
последовательно на CPU `0,1`: core `23/23`, затем extended `12/12`, затем
release-CI `27/27`. Дополнительно обязательны current/history public scans,
trusted npm SRI `4/4`, action pins `2/2`, два byte-identical source distribution
build с полным successor archive layout и fresh SHA-256, JSON/TOML parsing,
strict OpenSpec validation и `git diff --check`.

Перед LLM launch deterministic preflight должен принять exact published
authorization, проверить `Depends On` exact investigation id и в successor, и
в authorization-card, измерить cumulative production LOC `<=400` и
согласовать единый successor manifest со всем predecessor и
linked-replacement payload. После этого отдельный fresh-context xhigh review
проверяет тот же exact tree. Эти проверки не разрешают publication mutation до
fresh `GO`.

## Risks / Trade-offs

- **[Risk] 100-line incremental budget узок для behavioral probes.** →
  Переиспользовать normalization и table-driven fixtures; при 401+ остановить
  delivery для split/new investigation, не сокращать semantic coverage.
- **[Risk] Prose routing может расходиться с helper semantics.** → Focused
  wiring smoke извлекает разные gate sets, а committed smoke проходит через
  production helper.
- **[Risk] Investigation JSON могут принять за waiver.** → Card сохраняет
  authorization `none`; design явно требует отдельный clean published source и
  reciprocal exact successor reference.
- **[Risk] Predecessor qualification могут ошибочно переиспользовать.** → Его
  counts являются только lineage/floor; successor повторяет полную матрицу и
  получает новый tree/fingerprint/evidence.
- **[Risk] Docs-only decision влияет на release-critical boundary.** →
  Investigation получает `critical`/xhigh independent review до publication.

## Migration Plan

1. Deliver this docs/OpenSpec-only change, sync its single delta requirement,
   archive it, obtain fresh xhigh `GO` and publish the investigation to main.
2. Create and separately deliver/review/publish the exact authorization card
   with the six-field object, ceiling 400 and `Depends On` exact published
   investigation id.
3. Add the two-field published authorization reference and `Depends On` the
   same exact investigation id to the exact successor card; preserve its
   predecessor payload and unified manifest.
4. Run successor `$changerail-do`, continuously measure cumulative counted LOC
   and stop at 401 before review rather than changing classification or scope.
5. Complete the full verification floor, fresh xhigh review and normal publish;
   use `--resume-release` only after a proven pushed payload handoff.

Rollback текущего investigation до publication удаляет только docs/OpenSpec
payload обычным reviewed flow. После publication отмена решения требует новой
tracked card; никакие release objects этим change не создаются и не удаляются.

## Open Questions

- none
