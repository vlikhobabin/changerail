# Исследовать границу post-commit release resume entry

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
- Decision-only investigation для release-card
  `prepare-1-0-0-stable-release` и exact successor
  `enable-post-commit-release-resume-entry`.
- Последняя безопасная опубликованная база predecessor:
  `origin/main@aabfb2d8d7ba98e727766f2cb0299a607389b6d9`.
- Final `NO-GO` cycle 3 относится к exact reviewed tree
  `284d05faa41b13defc0b995cba223ae0600e8edd` и diff fingerprint
  `sha256:ab12bb20f5449b1aeda0d354c990fb4bf8626d07ea8cf9f35fa56d1180971835`.
  Same-card rescue использованы `2/2`; release commit, tag и hosted release не
  создавались.

## Summary
Зафиксировать минимальную fail-closed implementation boundary, cumulative
production-counted LOC budget и verification floor для exact successor,
который делает post-commit publication resume достижимым. Investigation не
выдает waiver: превышение обычных 300 LOC может разрешить только отдельная
опубликованная authorization-card, связанная с этим investigation и exact
successor, с потолком не выше 400 LOC.

## Review
- Risk tier: `critical`
- Milestone audit: `yes`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Investigation является docs/OpenSpec-only decision. Оно не разрешает release
mutation, не меняет source classification и не заменяет отдельный clean
tracked `4.done` authorization source.

## Blocks
- `enable-post-commit-release-resume-entry`

## Depends On
- none; predecessor payload и successor artifacts используются только как
  public-safe read-only decision input

## Acceptance
- Причина final `NO-GO` сформулирована как несовместимость состояний: normal
  entry безусловно требует current-worktree freshness и dirty working-tree
  scope, тогда как post-commit resume начинается с clean exact payload commit.
- Минимальная successor boundary ограничена существующими lifecycle skills,
  read-only `committed` target существующего manifest helper, двумя focused
  regression surfaces, синхронизацией двух существующих capabilities и
  release discipline docs; новая schema, provider, credential, workflow или
  mutation authority не вводятся.
- Зафиксирован measured predecessor baseline `299` added production-counted
  LOC и forecast `359..399`: не более `100` новых counted строк поверх
  baseline. Hard successor ceiling выбран равным `400`; `401+` требует split
  или нового investigation, а не ослабления classification/tests.
- Выбран отдельный future authorization id
  `authorize-bounded-post-commit-release-resume-entry-payload`, который после
  собственной delivery/review/publish связывает published investigation с
  exact successor и устанавливает `production_loc_ceiling: 400` и
  `allow_new_authority_or_wire_protocol: false`.
- Future authorization-card и exact successor MUST обе объявить в `Depends On`
  exact investigation id `investigate-post-commit-release-resume-entry-boundary`;
  canonical deterministic preflight MUST проверить обе reciprocal dependency
  edges вместе с six-field authorization object и two-field successor reference.
- Verification floor включает focused RED/GREEN committed-manifest и routing
  probes, core `23/23`, затем extended `12/12`, release-CI `27/27`, current и
  history public scans, trusted npm SRI `4/4`, action pins `2/2`, byte-identical
  source distribution, JSON/TOML/OpenSpec/diff checks и fresh xhigh review на
  одном exact successor tree.
- Tracked diff этого investigation содержит только card и apply-ready OpenSpec
  artifacts. Successor implementation, authorization-card, release workflow,
  tag, hosted release и publication mutation отсутствуют.

## Change Set
- `decide-post-commit-release-resume-entry-boundary`

## Verify
- `bin/openspec validate "decide-post-commit-release-resume-entry-boundary" --strict` — valid до sync/archive.
- `bin/openspec validate "changerail-release-discipline" --strict` — valid после sync/archive.
- `bin/openspec validate --all --strict` — `23 passed, 0 failed` после archive.
- `python3 scripts/public-surface-scan.py` — `1319 files scanned, 0 findings`.
- `python3 scripts/public-surface-scan.py --history` — `1319 files scanned, 0 findings`.
- `python3 scripts/smoke-review-preflight.py` — `review preflight smoke: PASS`;
  positive authorization fixture проверяет обе reciprocal `Depends On` edges.
- `python3 -m json.tool .mcp.json` — exit `0`; TOML parse `.codex/config.toml` — `TOML_OK`.
- `git diff --check` — exit `0`; отдельный whitespace scan новых artifacts — `NEW_ARTIFACT_WHITESPACE_OK`.

## Archive
- `openspec/changes/archive/2026-09-01-decide-post-commit-release-resume-entry-boundary/`

## Related
- `openspec/board/3.inprogress/prepare-1-0-0-stable-release.md`
- `openspec/board/2.todo/enable-post-commit-release-resume-entry.md`
- `openspec/specs/changerail-release-discipline/spec.md`
- `openspec/changes/archive/2026-09-01-decide-post-commit-release-resume-entry-boundary/`

## Result
Decision-only investigation завершено: exact post-commit entry mismatch,
минимальная successor boundary, cumulative forecast `359..399`, hard ceiling
`400` и отдельный future authorization source зафиксированы. Единственный
delta requirement синхронизирован; change архивирован. RED evidence
неприменим, поскольку production/runtime/test behavior не изменялись.
Same-card rescue attempt 1 устраняет R1: future authorization-card и exact
successor теперь нормативно обязаны объявить `Depends On` exact investigation
id, а canonical preflight — проверить обе связи fail closed.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-post-commit-release-resume-entry-boundary`

### Why
После payload commit current-worktree freshness и dirty working-tree scope уже
не могут доказать pre-commit reviewed state. Final review нашел, что publish и
deliver применяют эти normal-entry gates безусловно и поэтому не достигают
обещанной partial-publication continuation.

### Goal
Опубликовать одно decision-only решение, которое связывает exact blocker с
минимальной successor boundary, bounded cumulative LOC ceiling, отдельным
authorization source и полным наблюдаемым verification floor.

### Scope
- Выбрать state-specific normal/resume routing и read-only committed manifest
  proof как минимальную implementation boundary.
- Зафиксировать exact successor/authorization identities, paths и ceiling 400
  без выдачи authorization в этом change.
- Потребовать exact investigation id в `Depends On` future authorization-card
  и successor и их fail-closed проверку canonical deterministic preflight.
- Зафиксировать measured baseline, forecast, hard-stop и verification matrix.
- Синхронизировать только investigation requirement в существующую release
  discipline capability во время последующей apply phase.

### Acceptance
- Все card-level acceptance отражены в proposal, design, delta spec и tasks.
- Future authorization-card и successor обязаны ссылаться на exact
  investigation id через `Depends On` до проверки authorization preflight.
- Delivery этого change остается docs/OpenSpec-only и не реализует successor.

### Depends On
- none

### Related
- `openspec/changes/decide-post-commit-release-resume-entry-boundary/`

## Log
- 2026-09-01T09:41:54Z создано как planning-only investigation после final
  cycle 3 `NO-GO`; implementation, review, commit, push и publish в этой
  сессии запрещены.
- 2026-09-01T09:50:15Z decision синхронизирован в release-discipline spec,
  change архивирован и docs/OpenSpec verification floor прошел; карточка
  оставлена в `3.inprogress` для independent review.
- 2026-09-01T10:16:18Z independent review cycle 1 вернул `NO-GO` R1;
  same-card rescue attempt 1 / fix cycle 1 добавил обе обязательные reciprocal
  `Depends On` edges и их canonical preflight verification, сохранив ceiling
  `400`, protocol allowance `false` и исходный verification floor.
- 2026-09-01T11:22:55Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
