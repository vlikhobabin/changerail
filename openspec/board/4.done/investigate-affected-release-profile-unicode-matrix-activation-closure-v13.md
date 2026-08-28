# Исследовать Unicode-matrix и activation closure affected profile v13

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 32

## Source
- Latest safe published affected-profile reference: exact authorization v11
  commit `9f72764e4969be9dcaebe08cabf06c6bbc9f4934`.
- Terminal unpublished
  `investigate-affected-release-profile-unicode-matrix-activation-closure-v12`
  completed fresh review cycle 1 with `9/14` acceptance and three blockers,
  consumed its sole bounded same-card rescue, then completed fresh cycle 2
  with `12/14` acceptance, two blockers and rescue budget `1/1/0` exhausted.
- Only validated verdict summaries, counters and bounded conclusions in this
  Source cross the boundary. Terminal v12 card, OpenSpec payload, manifest,
  verdict files, logs and raw runtime evidence are forensic-only and MUST NOT
  be read, copied, cherry-picked or accepted by this clean lineage.

## Summary
Опубликовать clean docs-only investigation/design decision, который сохраняет
закрытые v12 Unicode/activation boundaries и устраняет два оставшихся proof
дефекта: exact contiguous missing-module exception line и независимо написанный
Unicode oracle, не выводимый из production table.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Lineage escalation: terminal v12 больше не исправляется и не публикуется;
  exhausted `1/1/0` требует отдельного clean docs-only investigation/design.
- Independent review: one fresh `gpt-5.6-sol`/`high`
- Same-card repair budget limit/used/remaining: `1/1/0`, exhausted `true`

## Depends On
- `authorize-bounded-affected-release-profile-v11`
- `investigate-affected-release-profile-runtime-root-scheduler-matrix-v11`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`

## Blocks
- `authorize-bounded-affected-release-profile-v13`
- `implement-bounded-affected-release-profile-v13`
- `certify-accelerated-release-loop-v1`

## Acceptance
- Decision создаётся и публикуется docs-only из exact safe authorization v11
  commit `9f72764e...`; remote v12 и v13 branches до mutation указывают ровно
  на этот SHA, terminal v12 payload/evidence не импортируются, а chronology
  сохраняет cycle 1 `9/14`, sole repair, cycle 2 `12/14` `NO-GO` и exhausted
  budget `1/1/0`.
- Decision объясняет exhausted-budget escalation: v12 больше не исправляется и
  не публикуется; до отдельной v13 authorization запрещены implementation card,
  focused test, production, CI и executable main-spec mutations.
- Retained RED handoff future v13 проверяет и сохраняет одну точную
  непрерывную строку
  `ModuleNotFoundError: No module named 'changerail_release_affected_profile'`;
  проверка двумя fragments/substrings, reconstructed prose или поздняя
  reproduction не удовлетворяет контракту.
- Future RED capture напрямую запускает `bin/changerail-evidence capture`;
  captured command сначала печатает fingerprint, затем запускает реально
  падающий focused test без `|| true`/exit-zero wrapper, а retained entry
  связывает `status: failed`, non-zero exit, exact contiguous exception line,
  `tree_sha` и `diff_fingerprint` с существующим saved tree до production,
  CI или main-spec mutation.
- Frozen Unicode contract использует Unicode 16.0.0 general categories
  `Cc|Cf`: ровно 23 ranges, 235 code points, digest
  `7fb5126f7973cc51a27f62c8712c11401ace15b9d40afdf02f1575945dc1da81`,
  при этом U+11F00 является стабильным nonmember. Digest preimage сортирует
  ranges по ascending start, кодирует каждый endpoint ровно шестью uppercase
  ASCII hex digits, каждую range как `START-END`, соединяет records одним ASCII
  `;` без whitespace, BOM, newline или trailing delimiter и вычисляет SHA-256
  этих ASCII/UTF-8 bytes.
- Unicode proof future v13 содержит нормативно отдельный independently
  authored oracle: его source dataset/expectations пишутся независимо, не
  generated, не copied и не derived из production table, production digest,
  production iterator или production helper; общий production-derived source
  не может self-certify table и test одновременно.
- Independent Unicode oracle отдельно доказывает exact membership и
  nonmembership, range ordering/non-overlap, count `23/235`, digest и U+11F00
  nonmember; missing/extra/split/merged/reordered boundary и category drift
  fail closed, даже если production table и его собственный digest согласованы.
- Activation contract future v13 требует в lexical body `profile.main` ровно
  один depth-one direct call к unaliased imported `run_plan`; `if False`,
  `if True`, conditional expression, loop/try/with/function/lambda wrapper,
  alias, attribute/indirect call и alternate activation call запрещены.
- Connected activation oracle загружает actual public runner/profile/scheduler
  chain и доказывает, что required call достижим через public entrypoint;
  missing, duplicate, nested, guarded, wrapped, alternate, replacement или
  disconnected call fail closed без replacement production functions.
- Decision сохраняет опубликованные v11 runtime-root/pre-reservation и
  independently complete scheduler-matrix boundaries без ослабления.
- Decision сохраняет accumulated affected floor: exact 35-ID digest и 35→30
  typed ownership, aggregate pre-mutation admission, effective
  `purelib`/`platlib` origins, strict committed/staged/unstaged/untracked NUL
  selection, typed scheduler-v1 sole activation, full-only authority, exact
  source-safe four-step CI, connected resolved-base guards и
  protocol-artifact non-authority.
- Decision определяет единственный дальнейший порядок: эта investigation,
  docs-only `authorize-bounded-affected-release-profile-v13`, clean
  `implement-bounded-affected-release-profile-v13`, затем certification;
  future authorization связывает exact successor и ceiling не выше 500 строк,
  future implementation добавляет не более 499 production LOC.
- Investigation добавляет production/test/runtime LOC `0`, изменяет только
  свою card, same-slug OpenSpec artifacts, synchronized release-CI spec и
  archive metadata; v13 authorization/implementation и certification остаются
  отсутствующими.
- History, real full baseline, affected execution/benchmark, live matrix и
  certification checks не запускаются и не принимаются.

## Change Set
- `investigate-affected-release-profile-unicode-matrix-activation-closure-v13`

## Verify
- Required: exact safe base/remote, terminal-v12 concise chronology and
  forensic boundary, exact contiguous exception-line contract, independent
  Unicode oracle, frozen Unicode table, depth-one activation closure,
  accumulated floor/future order, strict OpenSpec, JSON/TOML, source
  classification, current-only public scan, archive/main sync, whitespace,
  manifest scope and fresh ordinary/high review.
- RED: not applicable; this investigation is docs-only and adds no executable behavior.
- Prohibited: history, full baseline, affected execution/benchmark, live matrix,
  v13 authorization/implementation creation, certification and terminal v12 reuse.
- GREEN: exact local/remote base, concise lineage, exception-line,
  independently authored Unicode oracle, frozen Unicode and direct connected
  activation oracles passed; strict OpenSpec passed `24/24` before archive;
  JSON/TOML parsing, current-only public scan `1607/0`, exact delta/main sync,
  source classification and whitespace passed with production/test/runtime LOC
  `0`.
- RESCUE GREEN: exact six-uppercase-hex `START-END` semicolon-delimited digest
  preimage is normative and archive/main exact; strict OpenSpec `23/23`,
  JSON/TOML, current-only public scan `1607/0`, whitespace and manifest scope
  passed after the sole scoped cycle-1 fix.
- NOT RUN by contract: reachable history, real full/affected execution or
  benchmark, live matrix and certification checks.

## Archive
- `openspec/changes/archive/2026-08-28-investigate-affected-release-profile-unicode-matrix-activation-closure-v13/`

## Related
- `openspec/changes/archive/2026-08-28-investigate-affected-release-profile-unicode-matrix-activation-closure-v13/`
- `openspec/board/4.done/authorize-bounded-affected-release-profile-v11.md`
- `openspec/board/4.done/investigate-affected-release-profile-runtime-root-scheduler-matrix-v11.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
DO complete: one clean docs-only v13 investigation decision is synchronized and
archived with exact contiguous RED exception-line retention and an independently
authored Unicode scalar oracle. Production/test/runtime LOC remain `0`;
awaiting fresh ordinary/high review before publish.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `investigate-affected-release-profile-unicode-matrix-activation-closure-v13`

### Why
Terminal v12 review proved that fragmented exception matching and a Unicode
oracle derivable from production data cannot establish the required independent
RED chronology and table completeness.

### Goal
Publish one clean docs-only decision with exact exception-line retention and an
independently authored Unicode 16.0.0 oracle while preserving validated
Unicode/activation and accumulated affected-profile boundaries.

### Scope
- this card;
- same-slug OpenSpec artifacts;
- synchronized `changerail-release-ci` specification and archive metadata.

### Acceptance
- All card acceptance criteria above are observable and machine-checkable.

### Depends On
- `authorize-bounded-affected-release-profile-v11`
- `investigate-affected-release-profile-runtime-root-scheduler-matrix-v11`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`

### Related
- `openspec/changes/investigate-affected-release-profile-unicode-matrix-activation-closure-v13/`

## Log
- 2026-08-28 created in a clean worktree and remote branch from exact safe
  published authorization v11 after validated terminal v12 cycle-2 `NO-GO`;
  only concise findings/counters crossed the forensic boundary.
- 2026-08-28 FF created one apply-ready same-slug docs-only change with exact
  contiguous exception-line, independently authored Unicode oracle and direct
  connected activation contracts; strict target/all and whitespace checks
  passed while executable successors and prohibited evidence remained absent.
- 2026-08-28 DO synchronized five release-CI requirements and passed exact
  base/remote, delta/main, strict OpenSpec, JSON/TOML, source classification,
  current-only public-surface and whitespace checks with
  production/test/runtime LOC `0`; no prohibited release or certification
  execution ran.
- 2026-08-28 DO archived the same-slug change after explicit idempotent spec
  sync; active OpenSpec changes are empty and the card remains in
  `3.inprogress` for fresh review.
- 2026-08-28 fresh review cycle 1 returned `NO-GO`, acceptance `13/14`, one
  blocker and no unbacked claims: canonical Unicode digest byte serialization
  was not normative. The sole same-card rescue now fixes only that blocker by
  defining exact ordered uppercase-hex ASCII preimage bytes; budget is
  exhausted `1/1/0` pending fresh cycle 2.
- 2026-08-28T15:41:34Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
