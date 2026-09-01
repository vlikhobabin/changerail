## Context

Predecessor release payload уже определяет exact `v1.0.0` tag/release/assets
identity и корректный uninterrupted порядок: fresh review на dirty working
tree, scoped payload commit/push, tag, hosted release, assets и только затем
card finalization. Final review cycle 3 показал единственный process blocker:
после безопасной остановки новая invocation сначала выполняет normal
current-worktree freshness и dirty manifest scope gates. На clean payload
commit они по определению не могут совпасть с pre-commit verdict, поэтому
расположенная ниже release continuation недостижима.

Это первая linked replacement после исчерпания same-card rescue `2/2`.
Existing release payload, synced spec и два archived changes остаются частью
одного будущего successor commit; новый change не переопределяет distribution
или release contract, а добавляет достижимый вход в уже разрешенную
transaction.

## Goals / Non-Goals

**Goals:**

- разделить normal и post-commit resume entry до запуска несовместимых gates;
- сохранить initial pre-staging freshness, verification и dirty scope checks;
- принимать resume только для clean exact payload commit с доказанными
  verdict lineage, committed manifest scope и remote branch identity;
- продолжать exact release transaction с первого отсутствующего шага;
- сделать routing и wrong-state rejection наблюдаемыми regression coverage;
- повторить полный release floor и fresh xhigh final review на одном successor
  tree до любой publication mutation.

**Non-Goals:**

- создавать новый release payload, tag, asset format или hosted provider;
- менять manifest/verdict schema ids, execution target или credential model;
- разрешать force/rebase/reset/stash, replacement objects или новую authority;
- переоткрывать два completed predecessor changes либо публиковать в этом
  change;
- запускать clean-HEAD LLM review после payload commit.

## Decisions

### Один linked-rescue change и единый successor manifest

Routing, committed scope proof и release-resume requirements образуют одну
fail-closed boundary: ни одна часть не имеет самостоятельного полезного
результата без остальных. Поэтому card содержит один implementation-sized
change `enable-post-commit-release-resume-entry`, а не копии predecessor
distribution/release changes.

После implementation `changerail-do` выводит новый manifest для successor
card. Его `committable_paths` MUST поглотить весь сохраненный predecessor dirty
payload, новую card, archived successor change, synced specs, skill/docs/helper
и regression paths. Predecessor archives входят как уже существующие changed
paths, но не создаются повторно. Manifest и evidence остаются ignored runtime
state; tracked artifacts содержат только contract и concise targets.

### Явный ранний split normal/resume

`$changerail-pub <card>` сохраняет default normal mode.
`$changerail-pub <card> --resume-release` выбирает resume mode до общей Review
Gate и до working-tree scope-check. `$changerail-deliver <card>
--resume-release` после bounded card/branch discovery напрямую передает тот же
mode в publish contract и не запускает `ff`, `do`, новую review phase или
normal publish entry.

| Gate | Normal entry | `--resume-release` entry |
|---|---|---|
| Deterministic preflight текущего payload | MUST | MUST NOT |
| Verdict `--check-fresh` на working tree | MUST | MUST NOT |
| Full verification перед первым staging | MUST | MUST NOT повторять как post-commit freshness |
| Manifest `working-tree` и `staged` parity | MUST | MUST NOT |
| Clean workspace/card at payload commit | после commit | MUST до любой mutation |
| Verdict schema/result без current freshness | часть fresh gate | MUST |
| Payload parent/tree lineage | после commit | MUST |
| Manifest `committed` parity | final handoff proof | MUST |
| Remote feature branch == payload commit | после push | MUST |
| Exact tag/release/assets identity | перед каждым release step | MUST |

Resume несовместим с `--no-push`, `--message`, `--docs-only` и любым mode,
который предлагает staging/commit или расширяет scope. Неизвестная или
противоречивая комбинация flags останавливается без mutation.

### Normal entry остается pre-commit gate

Normal path выполняет ранний admission, затем полный project verification. На
неизмененных после verification bytes непосредственно перед explicit staging
он повторно выполняет deterministic preflight без normalization, valid
successor `GO` с `--check-fresh` и working-tree manifest parity; staged parity
остается после staging. Любая same-path byte mutation между ранним gate и этим
повтором останавливает commit/push. После commit parent MUST равняться reviewed
`head_commit`, а commit tree MUST равняться reviewed `tree_sha`.

Создание clean commit не является новым review state. Если payload push не
подтвержден, release continuation не начинается; post-commit resume допускает
только уже удаленно достижимый safe handoff.

### Resume admission доказывает commit вместо working tree freshness

Resume читает successor verdict и manifest, но не вычисляет новый
working-tree fingerprint. До любой external mutation он последовательно:

1. До object reads отвергает любые local `refs/replace/` и non-empty common
   Git `info/grafts`; commit identity/parent/tree/diff/archive reads выполняет
   с replacement processing disabled.
2. Валидирует verdict по существующей schema без `--check-fresh` и отдельно
   требует `result: go`, полный `workspace.head_commit` и
   `workspace.tree_sha`.
3. Валидирует manifest по существующей schema и требует recorded
   `publish.payload_commit`, authorized credential-free remote/branch и
   успешный pushed handoff.
4. Требует пустой `git status --porcelain` без staged, unstaged или untracked
   paths; target successor card из payload commit MUST быть единственным live
   card path и иметь `Status: 3.inprogress`.
5. Требует ровно одного raw parent у payload commit, равного verdict
   `head_commit`, и tree payload commit, равного verdict `tree_sha`.
6. Сравнивает exact raw `parent..payload` diff operations с manifest
   `committable_paths`, включая add/modify/delete/rename и exclusions.
7. Разрешает upstream через current branch/manifest identity, выполняет
   read-only remote query и требует, чтобы authorized feature branch указывала
   ровно на payload commit, а не только содержала его в истории.

Любое отсутствующее поле, merge commit, иной card status/path, dirty byte,
лишний/пропущенный/mismatched manifest path, wrong remote/upstream или
недоказуемый ref является hard stop. Resume не исправляет состояние через
stash, reset, rebase, force или новый commit.

### Existing manifest helper получает committed target без новой schema

`bin/changerail-delivery-manifest scope-check` является текущим source of
truth для working-tree/staged parity. Он расширяется read-only формой:

```text
bin/changerail-delivery-manifest scope-check <manifest> \
  --target committed --commit <payload-commit> --json
```

`committed` разрешает exact commit, fail-closed отвергает replacement refs и
graft state, затем с replacement processing disabled требует ровно одного raw
parent и строит raw machine-readable name-status diff `parent..commit`,
нормализованный теми же operation rules, что existing targets. `--commit`
обязателен только для
`committed` и запрещен для других targets. Existing manifest JSON не получает
новых полей и сохраняет schema id; это дополнительная read-only проверка
имеющихся данных, а не новый wire protocol.

Reference contract в
`skills/changerail-do/references/changerail-delivery-manifest.md` документирует
новый target. Focused manifest smoke покрывает exact match, missing/extra,
operation mismatch, wrong commit, merge/no-parent и adversarial
replacement/graft rejection без подмены lineage.

### Release continuation является idempotent state machine

После admission workflow каждый раз заново получает read-only identity и
продолжает только с первого отсутствующего шага:

1. remote branch exact payload уже доказан;
2. annotated `v1.0.0` отсутствует либо exact object/type/target/annotation
   совпадают; отсутствующий tag создается/push-ится без force;
3. assets строятся в новом ignored directory из dereferenced tag commit;
4. public release отсутствует либо exact tag/title/full notes/state совпадают;
5. каждый present asset имеет уникальный contracted basename и byte-match с
   fresh local build; загружаются только доказанно отсутствующие basenames;
6. final read-only query/download доказывает полный exact set, после чего
   выполняется отдельная deterministic card-only finalization.

Safe interruptions после payload push, tag creation, release creation и
partial upload повторно входят через тот же admission и продолжаются с шага
2, 3, 4 или 5 соответственно. Unexpected/duplicate/mismatched object никогда
не заменяется. Exact contract остается: annotation и title
`ChangeRail 1.0.0`, notes — полный tracked `docs/releases/1.0.0.md`, assets —
три basenames из distribution contract.

### Source of truth и regression observation

Canonical behavior живет в `skills/changerail-pub/SKILL.md`; orchestration
route — в `skills/changerail-deliver/SKILL.md`. Main requirements синхронно
обновляются в `changerail-skill-surface` и `changerail-release-discipline`, а
`docs/release-discipline.md` объясняет operator handoff. Archived predecessor
design сохраняет history, но stale слова `повторного freshness/full-gate`
заменяются точным parent/tree/manifest/remote resume proof.

Existing core `scripts/smoke-wiring-discovery.py` извлекает реальные Markdown
sections и bash commands, проверяет normal placement/order до и после staging,
resume admission order и forbidden cross-route commands. Controlled fixtures
удаляют late freshness, добавляют resume staging, меняют dirty/lineage/scope/
remote states и проверяют explicit zero-mutation hard stop; interruption table
фиксирует первый отсутствующий шаг. Committed и source-distribution smokes
создают реальные replacement/graft fixtures и доказывают rejection без
подмены lineage/source bytes. Core `23` и extended `12` inventories не
перемещаются и не дублируются.

## Risks / Trade-offs

- **Prose skill routing может снова стать противоречивым** → отдельные
  machine-checked sections и negative fixtures наблюдают drift обоих modes.
- **Manifest может описывать старый dirty payload, но не commit** → committed
  target сравнивает exact parent diff и запрещает inferred/multi-parent state.
- **Local replacement/graft скрывает raw lineage/source bytes** → admission и
  оба Git readers reject overrides, а object reads отключают replacement.
- **Clean workspace скрывает wrong branch/card** → clean check дополняется
  exact card status/path и remote feature-branch equality.
- **Idempotent resume может принять чужой release object** → каждый object и
  present asset сравнивается с полным reviewed identity до mutation.
- **Повтор heavy qualification дорог** → predecessor counts служат только
  floor; successor все равно повторяет core, затем extended и fresh xhigh
  review на одном exact tree.

## Migration Plan

1. Реализовать committed manifest target и focused RED/GREEN regression.
2. Разделить pub normal/resume entry и добавить direct deliver routing.
3. Синхронизировать specs/docs и исправить stale archived design wording.
4. Обновить единый successor manifest, включив существующий release payload и
   все linked-rescue paths; sync/archive только новый change.
5. На одном frozen successor tree выполнить original qualification floor и
   fresh independent xhigh final review.
6. Только после successor `GO` normal publish может создать/push payload;
   дальнейшая safe interruption возобновляется `--resume-release`.

Rollback до publication удаляет только новый uncommitted implementation через
обычный reviewed fix flow; destructive recovery не используется. После
создания любого remote release object rollback его не переписывает и требует
того же identity-bound resume либо отдельного corrective release decision.

## Open Questions

Нет. Provider, wire schema и новая external authority не требуются; если
implementation discovery опровергнет это, delivery MUST остановиться как
`investigation-required`, а не расширять эту карточку.
