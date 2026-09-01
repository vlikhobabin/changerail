# Включить post-commit resume entry для публикации release

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- none

## Series Index
- none

## Source
- Linked replacement для
  `openspec/board/3.inprogress/prepare-1-0-0-stable-release.md` после
  исчерпания допустимых same-card rescue.
- Последняя безопасная опубликованная база:
  `origin/main@aabfb2d8d7ba98e727766f2cb0299a607389b6d9`.
- Final `NO-GO` cycle 3 относится к exact predecessor tree
  `284d05faa41b13defc0b995cba223ae0600e8edd` и diff fingerprint
  `sha256:ab12bb20f5449b1aeda0d354c990fb4bf8626d07ea8cf9f35fa56d1180971835`.
  Same-card rescue использованы `2/2`, осталось `0`; продолжать predecessor
  в той же карточке нельзя.

## Summary
Сделать обещанный fail-closed post-commit release resume достижимым через
явный `--resume-release` entry mode в `$changerail-pub` и детерминированный
маршрут из `$changerail-deliver`. Обычный первый publish сохраняет все
pre-staging freshness и working-tree scope gates; resume принимает только
чистый, уже закоммиченный и удаленно достижимый exact payload и продолжает с
первого отсутствующего release-шага после полной проверки lineage, manifest,
remote и release identity.

## Review
- Risk tier: `critical`
- Milestone audit: `yes`
- New authority or wire protocol: `no`
- Credential or mutation authority: `yes`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `yes`
- Published investigation authorization: `{"authorization_card":"openspec/board/4.done/authorize-bounded-post-commit-release-resume-entry-payload.md","authorization_id":"authorize-bounded-post-commit-release-resume-entry-payload"}`

Review rationale: risk tier `critical` требует `xhigh` independent review;
credential or mutation authority — только унаследованная явно разрешенная
оператором transaction публикации ChangeRail `1.0.0`; repeated defect class —
`no`, потому что это первая linked replacement в lineage, а не второй
replacement с повторенным blocker class.

`--resume-release` является mode существующих lifecycle skill invocations: он
не добавляет provider, endpoint, credential type, сериализованную
`changerail.*` schema или новую mutation authority. Он только выбирает
fail-closed набор проверок для уже разрешенной transaction. Любое расширение
внешней authority, замена execution target или новый provider/wire contract
остаются вне scope и требуют отдельного решения.

## Depends On
- `investigate-post-commit-release-resume-entry-boundary`
- Существующий dirty release payload и archived changes predecessor должны
  быть сохранены как единое целое; завершение predecessor card не является
  precondition, потому что эта карточка заменяет исчерпанный rescue route.
- `openspec/changes/archive/2026-09-01-define-first-stable-distribution-contract/`
- `openspec/changes/archive/2026-09-01-prepare-changerail-1-0-0-release/`

## Attempts And Evidence Summary
- Cycle 1: `NO-GO`, два blocker и два major; добавлены authoritative release
  continuation, exact-candidate evidence, dirty-tracked archive oracle и
  согласованное metadata-sidecar wording.
- Cycle 2 после rescue 1: `NO-GO`, два blocker; исправлены post-commit
  parent/tree handoff и exact tag annotation, release title/notes и
  partial-asset identity.
- Cycle 3 после rescue 2: `NO-GO`, один blocker: новая invocation
  `$changerail-pub` безусловно применяет current-worktree freshness и dirty
  working-tree manifest scope к clean payload commit, а
  `$changerail-deliver` повторяет ту же недостижимую ветку.
- Последняя qualification predecessor прошла core `23/23`, затем строго
  последовательно extended `12/12`, release-CI `27/27`, current/history public
  scans `1326/0` каждый, trusted npm SRI `4/4`, action pins `2/2`, exact archive
  layout `1410/1410`; qualified archive SHA-256:
  `7ee9b964a2f946d2e0190282db1213f6b4bf98617b1f0ac0a942bfda9dfbc00e`.
  Эти результаты являются predecessor evidence, а не сертификацией будущего
  successor tree.
- Successor independent review cycle 1 вернул `NO-GO` для exact starting
  payload `0a77fd52...` / tree `3203ce9e...` / fingerprint
  `sha256:b4e1f339...`: R1 stale exact-tree evidence, R2 late freshness
  placement, R3 replacement/graft boundary и R4 disconnected marker oracle.
- Same-card rescue attempt 1 получил RED на всех R2-R4 boundaries, затем GREEN
  focused wiring `51/51`, committed manifest и source-distribution `25/25`;
  normalized preflight вернул `ready-for-llm-review`, exact authorization и
  production LOC `397/400` без новой authority/wire schema.
- Release commit, push, tag и GitHub Release отсутствуют.

## Acceptance
- `$changerail-pub <card> --resume-release` имеет явный отдельный entry route,
  а `$changerail-deliver <card> --resume-release` детерминированно передает
  управление в тот же publish route без повторного `ff/do/review` и без
  подмены его normal-entry gates.
- Обычный первый publish после final verification непосредственно перед первым
  staging повторяет deterministic preflight, current-worktree verdict
  `--check-fresh` и working-tree scope; staged scope остается после staging, а
  intervening same-path byte mutation останавливает commit/push.
- Resume mode недостижим из dirty или pre-commit состояния, не вызывает
  current-worktree `--check-fresh`, working-tree/staged dirty-scope gates или
  дополнительный clean-HEAD LLM review и не создает новый payload commit.
- До любой resume mutation workflow проверяет существующий verdict schema и
  `result: go`, затем доказывает: parent payload commit равен
  `verdict.workspace.head_commit`; tree payload commit равен
  `verdict.workspace.tree_sha`; workspace чист; successor card остается в
  ожидаемом post-commit `3.inprogress`; committed diff payload commit в
  точности соответствует единому successor manifest; authorized remote
  feature branch указывает ровно на payload commit.
- Local replacement refs и graft state отклоняются до resume mutation;
  commit identity/parent/tree/diff/archive reads используют raw-object
  semantics с replacement processing disabled.
- Единый successor manifest поглощает весь сохраненный predecessor dirty
  release payload, новую linked replacement card, новый archived change после
  delivery и все новые routing/spec/docs/test paths; два predecessor archived
  changes не дублируются и не переоткрываются.
- После lineage/scope/remote proof resume выполняет exact identity checks для
  annotated `v1.0.0`, annotation `ChangeRail 1.0.0`, public release title
  `ChangeRail 1.0.0`, полного notes body из `docs/releases/1.0.0.md` и трех
  contracted assets; transaction продолжается с первого доказанно
  отсутствующего шага.
- Missing lineage/evidence, invalid/negative verdict, wrong parent/tree/card,
  dirty workspace, replacement/graft state, manifest diff mismatch, wrong or divergent remote branch,
  unexpected tag/release state, duplicate/unexpected/mismatched asset или
  иная недоказуемая identity останавливают route до mutation.
- Никакие force/rebase/reset/stash, replacement tag/assets, broadened
  mutation authority, provider substitution или дополнительный clean-HEAD LLM
  review не допускаются.
- Regression coverage извлекает реальные normal/resume sections и commands:
  normal вызывает late pre-staging freshness/scope, resume запрещает normal
  commands и требует raw committed lineage/scope/remote proofs. Interrupted scenarios
  после payload push, tag creation, release creation и partial asset upload
  продолжаются с первого отсутствующего шага; adversarial wrong-state cases
  fail closed без mutation.
- Stale фраза archived release design о повторном post-commit
  `freshness/full-gate` исправлена без переписывания или дублирования
  predecessor change history.
- После implementation весь исходный qualification floor повторно проходит
  на одном exact successor tree, затем отдельная fresh-context xhigh final
  review возвращает `GO` для того же tree до любой publication mutation.

## Change Set
- `enable-post-commit-release-resume-entry`

## Verify
- `python3 scripts/smoke-delivery-manifest-derive.py` или эквивалентный focused
  regression доказывает exact committed-diff/manifest parity и rejection
  wrong commit lineage.
- Focused lifecycle routing regression наблюдает разные gate traces для normal
  и `--resume-release`, interrupted safe handoffs и adversarial wrong states.
- `python3 scripts/run-release-baseline.py` на exact successor tree: core
  `23/23`.
- Только после core: `python3 scripts/run-release-baseline.py --suite extended`
  с полным expected inventory.
- `python3 scripts/smoke-release-ci.py`.
- `python3 scripts/public-surface-scan.py`.
- `python3 scripts/public-surface-scan.py --history`.
- Trusted npm SRI `4/4` и action-pin checks `2/2` из
  `docs/release-discipline.md`.
- Reproducible source distribution: exact layout `1410/1410` или полный
  successor tracked-file count, byte-identical rebuild, checksum/metadata и
  fresh successor archive SHA-256 в ignored evidence.
- `python3 -m json.tool .mcp.json`, TOML parse `.codex/config.toml`,
  `bin/openspec validate --all --strict` и `git diff --check`.

## Verification Result
- Cycle-1 core/extended/distribution claims на `0c30cf...` / `5eb237...`
  superseded и не являются final evidence для rescue payload.
- RED retained outputs: section-aware routing `50/51`; committed replacement
  неожиданно `ok:true`; builder создал assets из replacement-aware source view.
- GREEN focused outputs: routing `51/51`; committed replacement/graft rejection
  и source-distribution `25/25`, включая no-output/no-mutation fixtures.
- До freeze normalized preflight: `ready-for-llm-review`, critical/xhigh,
  valid exact authorization, `397/400`, new authority/wire `false`.
- Полный floor и две distributions выполняются только после единственного
  tracked freeze на exact candidate; outcomes/source revision/tree и retained
  mandatory ids обновляются только в ignored manifest/evidence index.

## Archive
- `openspec/changes/archive/2026-09-01-enable-post-commit-release-resume-entry/`

## Related
- `openspec/board/3.inprogress/prepare-1-0-0-stable-release.md`
- `skills/changerail-pub/SKILL.md`
- `skills/changerail-deliver/SKILL.md`
- `openspec/specs/changerail-release-discipline/spec.md`
- `openspec/specs/changerail-skill-surface/spec.md`
- `docs/release-discipline.md`

## Result
Rescue implementation, spec sync и archive metadata завершены; exact-tree
qualification и cycle-2 handoff сохраняются только в ignored runtime после
tracked freeze. Commit payload, push, review cycle 2 и publish не выполнялись.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `enable-post-commit-release-resume-entry`

### Why
Predecessor определил корректный uninterrupted release transaction и exact
partial-publication identity, но новый publish/deliver entry неизбежно
останавливается на pre-commit gates после уже созданного payload commit.

### Goal
Разделить normal и post-commit resume entry так, чтобы первоначальная
публикация сохраняла строгие freshness/scope gates, а clean exact payload
handoff можно было безопасно и идемпотентно продолжить без нового review или
расширения authority.

### Scope
- Добавить явный `--resume-release` contract и взаимоисключающий gate routing
  в `changerail-pub` и `changerail-deliver`.
- Добавить committed-diff/manifest, payload lineage, clean card/workspace и
  remote branch proofs перед существующими exact release identity checks.
- Исправить stale archived design wording и синхронизировать normative release
  и skill-surface specs, durable docs и regression coverage.
- Сохранить все predecessor release changes как existing payload; не
  переоткрывать и не дублировать два archived changes.

### Acceptance
- Все card-level acceptance выполнены на одном successor payload и наблюдаемы
  focused regression tests и полным final-certification floor.

### Depends On
- `investigate-post-commit-release-resume-entry-boundary`
- Change работает поверх сохраненного predecessor payload и ссылается на его
  archives как lineage, а не создает их заново

### Related
- `openspec/changes/enable-post-commit-release-resume-entry/`

## Log
- 2026-09-01T08:56:18Z создано как deliver-ready linked replacement после
  final cycle 3 `NO-GO` и исчерпания predecessor same-card rescue `2/2`; в этой
  planning-only session запрещены implementation, archive, review и publish.
- 2026-09-01T09:05:40Z один implementation-sized change получил apply-ready
  proposal, две delta specs, design и tasks; successor handoff остается
  `$changerail-do`, а весь predecessor payload должен войти в единый новый
  manifest.
- 2026-09-01T16:36:26Z fresh verification-only recovery принят как
  external-CPU-contention evidence после независимой проверки exact HEAD/diff,
  `69/69` report, elapsed time и empty stderr; timeout и sharding contract не
  менялись повторно.
- 2026-09-01T16:36:26Z successor floor завершен на одном pinned candidate:
  core `23/23`, extended `12/12`, release-CI `27/27`, public scans без findings,
  npm `4/4`, action tags `2/2`, reproducible assets и strict static gates;
  active successor sync проверен idempotently и change архивирован.
- 2026-09-01T16:37:55Z deterministic preflight подтвердил archived change,
  exact manifest scope, valid `399/400` authorization и critical `xhigh` route;
  handoff подготовлен только на `$changerail-review`, без запуска review или
  publication.
- 2026-09-01T17:31:02Z independent review cycle 1 `NO-GO` принят без изменения
  canonical verdict/history; same-card rescue attempt 1 исправил R2-R4 с
  focused RED/GREEN и normalized preflight `397/400`. Cycle-1 exact-tree floor
  помечен superseded; следующий шаг — один tracked freeze, runtime-only полный
  floor и отдельный `$changerail-review ... --cycle 2` без review/publication в
  этой implementation session.
- 2026-09-01T19:35:13Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
