# Авторизовать bounded post-commit release resume entry payload

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
- `openspec/board/4.done/investigate-post-commit-release-resume-entry-boundary.md`
  — exact published normative decision source.
- `openspec/board/4.done/fix-review-preflight-exact-authorization-cardinality.md`
  — published generic prerequisite, который закрывает cycle 1 blocker R1 на
  exact authorization/reference cardinality и relation matching.

## Summary
Опубликовать отдельный docs/OpenSpec-only authorization source, который
связывает exact investigation с exact post-commit release resume successor и
разрешает cumulative production-counted LOC только в установленной bounded
границе без новой authority или wire protocol.

## Review
- Risk tier: `critical`
- Milestone audit: `yes`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Authorization-card является release-critical docs/OpenSpec source, но сама не
выполняет release mutation, не реализует successor и не меняет runtime policy.

## Depends On
- `investigate-post-commit-release-resume-entry-boundary`

## Authorization
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/investigate-post-commit-release-resume-entry-boundary.md","investigation_id":"investigate-post-commit-release-resume-entry-boundary","successor_card":"openspec/board/3.inprogress/enable-post-commit-release-resume-entry.md","successor_id":"enable-post-commit-release-resume-entry","production_loc_ceiling":400,"allow_new_authority_or_wire_protocol":false}`

## Acceptance
- Card содержит ровно один machine-readable six-field authorization object;
  набор ключей, типы и значения совпадают с нормативным investigation без
  дополнительных полей, другого successor или переиспользуемого waiver.
- Exact published investigation-card является единственным нормативным
  источником решения, а эта card объявляет
  `Depends On: investigate-post-commit-release-resume-entry-boundary`.
- Authorization связывает только successor id
  `enable-post-commit-release-resume-entry` с exact path
  `openspec/board/3.inprogress/enable-post-commit-release-resume-entry.md`.
- Cumulative hard ceiling равен `400`; deterministic preflight при `401+`
  fail closed до semantic review и требует split или нового investigation.
- Measured predecessor baseline остаётся `299`, exact successor forecast —
  `359..399`, а planned increment — не более `100` production-counted строк;
  ceiling не разрешает расширять исследованную implementation boundary.
- `allow_new_authority_or_wire_protocol` строго равен `false`: authorization
  не разрешает новую schema, provider, credential, workflow или mutation
  authority.
- Exact successor после публикации этой card должен отдельно объявить тот же
  investigation id в `Depends On` и exact two-field published authorization
  reference. Canonical deterministic preflight проверяет обе reciprocal
  investigation dependency edges, exact successor identity/path и exact
  six-field object и fail closed при missing, unpublished, extra или mismatched
  данных.
- Delivery этой card изменяет только card/OpenSpec docs. Successor card,
  production/runtime/test implementation, release-card, tag, GitHub Release,
  assets и любая release mutation остаются вне scope.

## Change Set
- `authorize-bounded-post-commit-release-resume-entry-payload`

## Verify
- Planning: `bin/openspec validate
  "authorize-bounded-post-commit-release-resume-entry-payload" --strict` —
  valid.
- Planning: `bin/openspec validate --all --strict` — `24 passed, 0 failed`.
- Planning: exact authorization semantic check —
  `AUTHORIZATION_CARD_SEMANTICS_OK`; exact object встречается на card ровно
  один раз.
- Planning: `git diff --check` — exit `0`; отдельный whitespace scan —
  `NEW_UNTRACKED_WHITESPACE_OK files=6`.
- Planning: `python3 -m json.tool .mcp.json` — exit `0`; TOML parse
  `.codex/config.toml` — `TOML_OK`.
- Delivery: `bin/openspec validate
  "authorize-bounded-post-commit-release-resume-entry-payload" --strict` —
  valid до sync/archive.
- Delivery: semantic parse exact authorization object —
  `AUTHORIZATION_CARD_SEMANTICS_OK`; один object, шесть exact keys/values,
  integer ceiling `400`, boolean allowance `false`.
- Delivery: `bin/openspec validate "changerail-release-discipline" --strict` —
  valid после sync/archive; `bin/openspec validate --all --strict` —
  `23 passed, 0 failed` после archive.
- Delivery: `python3 scripts/smoke-review-preflight.py` —
  `review preflight smoke: PASS` без изменения fixtures.
- Delivery: `python3 scripts/public-surface-scan.py` и тот же command с
  `--history` — каждый `1325 files scanned, 0 findings`.
- Delivery: `python3 -m json.tool .mcp.json` — exit `0`; TOML parse
  `.codex/config.toml` — `TOML_OK`; `git diff --check` — exit `0`; отдельный
  scan шести новых files — `NEW_UNTRACKED_WHITESPACE_OK files=6`.
- Delivery manifest: `bin/changerail-delivery-manifest scope-check ...
  --target working-tree --json` — `ok: true`, без missing, extra или
  mismatched paths.
- RED evidence: `N/A`, поскольку payload меняет только card/OpenSpec docs и не
  изменяет production/runtime/test behavior.
- Cycle 2 repair: SSH fetch и `git merge --ff-only origin/main` — fast-forward
  `1acbe60bfbfdc42d91f08bb7734024e470e01b63..e14c56db582c75bf4000ddff4c64be687fccd730`;
  prerequisite/payload path intersection — `0`, manifest scope остался `7`.
- Cycle 2 repair: exact semantic parse —
  `AUTHORIZATION_CARD_SEMANTICS_OK objects=1 fields=6 dependency=1`;
  published prerequisite — `PREREQUISITE_HEAD_OK=e14c56d...`.
- Cycle 2 repair: `taskset -c 0,1 python3 scripts/smoke-review-preflight.py` —
  `review preflight smoke: PASS` на обновлённой duplicate/extra adversarial
  matrix.
- Cycle 2 repair: release-discipline strict — valid; OpenSpec all —
  `23 passed, 0 failed`; current/history public scans — каждый
  `1331 files scanned, 0 findings`; JSON/TOML, diff и whitespace — clean.
- Cycle 2 handoff: canonical normalized review preflight после final metadata —
  `ready-for-llm-review`; exact tree/fingerprint сохранены только в ignored
  runtime preflight evidence.

## Archive
- `openspec/changes/archive/2026-09-01-authorize-bounded-post-commit-release-resume-entry-payload/`

## Related
- `openspec/board/4.done/investigate-post-commit-release-resume-entry-boundary.md`
- `openspec/board/4.done/fix-review-preflight-exact-authorization-cardinality.md`
- `openspec/changes/archive/2026-09-01-authorize-bounded-post-commit-release-resume-entry-payload/`

## Result
Docs/OpenSpec-only authorization source доставлен без изменения exact
six-field object. Единственный delta requirement синхронизирован в
`changerail-release-discipline`, change архивирован, successor/release/runtime
surfaces не изменялись. Card оставлена в `3.inprogress` для independent review;
publication authority, release objects и release mutation отсутствуют.
После cycle 1 `NO-GO` generic prerequisite `e14c56d...` опубликован и
fast-forward интегрирован; R1 adversarial matrix теперь проходит, а exact
7-path authorization payload подготовлен к fresh critical review cycle 2.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-bounded-post-commit-release-resume-entry-payload`

### Why
Published investigation зафиксировало, что exact successor с cumulative
forecast выше ordinary 300 LOC требует отдельного clean tracked authorization
source; inline/free-form decision или ссылка только из successor не являются
допустимой authorization.

### Goal
Подготовить и отдельно опубликовать единственный bounded authorization source
для exact investigation/successor chain с ceiling `400` и protocol allowance
`false`.

### Scope
- Зафиксировать ровно один exact six-field authorization object на card.
- Нормативно потребовать обе reciprocal investigation dependencies, exact
  successor identity/path и fail-closed deterministic consumption.
- Синхронизировать только authorization-source requirement в существующую
  release-discipline capability во время последующей apply phase.
- Не изменять successor card и не добавлять в неё authorization reference до
  публикации этой authorization-card.
- Не изменять production/runtime/test implementation, schemas, providers,
  credentials, workflows, release-card, tag, GitHub Release или assets.

### Acceptance
- Все card-level bounded authorization invariants отражены в proposal, design,
  delta spec и tasks без изменения значений exact object.
- Delivery остаётся docs/OpenSpec-only и сохраняет successor/release surfaces
  неизменными.
- После публикации canonical preflight сможет принять только exact reciprocal
  chain и fail closed при любом missing, extra или mismatched relation.

### Depends On
- `investigate-post-commit-release-resume-entry-boundary`

### Related
- `openspec/changes/authorize-bounded-post-commit-release-resume-entry-payload/`

## Log
- 2026-09-01T11:31:12Z card создана для отдельного planning-only
  `$changerail-ff`; implementation/apply/archive/review/commit/push и release
  mutation в этой сессии запрещены.
- 2026-09-01T11:31:12Z один docs/OpenSpec-only change подготовлен до
  apply-ready artifacts; successor и release surfaces не изменялись.
- 2026-09-01T11:36:24Z planning verification завершена: strict OpenSpec,
  semantic authorization, config parse, diff и whitespace checks прошли;
  card оставлена в `2.todo` для отдельного `$changerail-do`.
- 2026-09-01T11:46:22Z docs/OpenSpec-only delivery синхронизировала один
  requirement, прошла declared verification floor и архивировала change;
  card оставлена в `3.inprogress` для independent review без commit/push или
  release mutation.
- 2026-09-01T13:15:23Z independent review cycle 1 вернул `NO-GO` R1; published
  prerequisite `e14c56db582c75bf4000ddff4c64be687fccd730` интегрирован обычным
  fast-forward merge с disjointness `0/7`, authorization payload сохранён без
  расширения и подготовлен к fresh cycle 2 verification.
- 2026-09-01T13:18:55Z exact authorization semantics, обновлённый adversarial
  preflight smoke, strict OpenSpec, public/config/diff/whitespace и 7-path
  scope checks прошли; payload передан на normalized preflight и fresh review
  cycle 2 без commit/push/publish.
- 2026-09-01T13:55:33Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
