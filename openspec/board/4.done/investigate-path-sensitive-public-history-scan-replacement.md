# Исследовать bounded replacement path-sensitive public history scan

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R-I

## Source
- Published decision `investigate-deterministic-release-baseline-acceleration`,
  commit `ccccb62562e1646b595119edd3326763860f14a7`.
- Exhausted unpublished implementation
  `accelerate-path-sensitive-public-history-scan`, reviewed at fingerprint
  `sha256:2904deabe2cc8c6ce6d1dfa2410cf2e1f513c5673409f700898286b53e47d116`.
- Independent review cycles: `NO-GO`, `NO-GO`; same-card rescue budget `1/1`
  exhausted. The retained payload is forensic input only and MUST NOT publish.

## Summary
Зафиксировать decision-only replacement boundary после повторившегося
fail-closed framing defect и стабильного нарушения frozen warm-performance
threshold. Выбрать один bounded design, который разрешает чистый successor без
повторного использования или публикации исчерпанного payload.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Depends On
- `investigate-deterministic-release-baseline-acceleration`

## Blocks
- `deliver-path-sensitive-public-history-scan-replacement`
- `parallelize-isolated-release-smoke-cases`

## Acceptance
- Решение сохраняет оба cycle-2 blocker и явно классифицирует malformed
  `ls-tree -z` framing как повторившийся unresolved invariant.
- Valid empty tree определяется только как `b""`; любой non-empty stream обязан
  завершаться ровно одним terminal NUL. Missing terminal NUL, interior empty
  records, malformed headers/OIDs/types и undecodable/unsafe paths должны
  fail-closed до успешного history result или cache reuse.
- `raw_name` в raw-tree framing определяется ровно как один non-empty
  strict-UTF-8 Git tree path component: round-trip bytes без NUL, slash,
  control/DEL или backslash и не `.`/`..`; до prefixing запрещены split и
  normalization. Connected successor negative fixture доказывает fail-closed
  для slash-bearing entry до output или cache.
- Решение выбирает одну bounded implementation hypothesis: fresh raw Git tree
  traversal через persistent `git cat-file --batch`, без production
  process-per-commit `ls-tree`; она должна пройти warm `<=5%` без изменения
  `history-fixture-v1`, legacy oracle, timed boundaries, workload, rounding или
  threshold и без выбора удачного rerun.
- Exact successor `deliver-path-sensitive-public-history-scan-replacement`
  получает полный production ceiling `<=300` LOC относительно
  `ccccb62562e1646b595119edd3326763860f14a7`, весь unpublished capability,
  полный verification floor и same-card repair/rescue limit/used/remaining
  `0/0/0`.
- Frozen policy сохраняет fixture fingerprint
  `sha256:4575cd8b42082d57c25cf474427579c3559aa8a5b3989413a91c40a876c5cf28`,
  scale `48/1152/96/72`, safe-parent legacy blob, sample order, two discarded
  warmups, five measured trials, unrounded ratios, CV rule и memory bounds.
- Решение меняет только board/OpenSpec/spec relationship documentation и не
  меняет production scripts, tests, schemas, runtime, CLI или baseline runner.
- Investigation не заявляет benchmark/baseline GREEN и не объявляет
  исчерпанный payload принятым задним числом.
- `parallelize-isolated-release-smoke-cases` остаётся заблокирован до
  опубликованного replacement с полным GREEN floor и fresh independent `GO`.

## Change Set
- `decide-path-sensitive-public-history-scan-replacement`
- `openspec/changes/decide-path-sensitive-public-history-scan-replacement/`

## Verify
- `bin/openspec validate decide-path-sensitive-public-history-scan-replacement
  --strict` и `bin/openspec validate --all --strict`.
- JSON/TOML parse, `python3 scripts/public-surface-scan.py`, source
  classification и diff/whitespace checks, включая untracked files.
- Scope/classification, delivery manifest и deterministic review preflight
  выполняются на exact decision payload до independent review.
- Полный history scan, frozen benchmark и release baseline не запускаются для
  decision-only payload.

## Archive
- `openspec/changes/archive/2026-08-24-decide-path-sensitive-public-history-scan-replacement/`
- Exactly one delta requirement synced to
  `openspec/specs/changerail-release-ci/spec.md`.

## Related
- `openspec/board/4.done/investigate-deterministic-release-baseline-acceleration.md`
- `openspec/changes/decide-path-sensitive-public-history-scan-replacement/`
- `openspec/specs/changerail-release-ci/spec.md`
- `scripts/public-surface-scan.py`
- `scripts/run-release-baseline.py`

## Result
Archived decision фиксирует exact framing, один persistent raw-tree batch
design, immutable benchmark и clean successor lineage. Production
implementation, benchmark/history/baseline evidence и acceptance claim не
созданы. Документационный payload прошёл strict validation, current public
scan, JSON/TOML parse, source classification, manifest/scope и deterministic
preflight; history scan, benchmark и release baseline не запускались.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-path-sensitive-public-history-scan-replacement`

### Why
Same-card review rescue исчерпан, а malformed `ls-tree -z` framing повторил
прежний fail-closed/fault-matrix defect class. Новый implementation rescue без
опубликованного решения нарушил бы investigation-required guard.

### Goal
Опубликовать один точный bounded design и lineage contract для чистого
replacement от последней безопасной опубликованной ревизии.

### Scope
- Decision-only OpenSpec и contract documentation.
- Exact `ls-tree -z`/raw-tree framing, one performance hypothesis, immutable
  benchmark, successor binding и verification protocol.
- Production additions: `0` LOC.

### Acceptance
- Исчерпанная карточка остаётся forensic-only и никогда не публикуется как
  успешная implementation.
- Successor создаётся в новом clean worktree от exact safe commit и владеет
  всей unpublished capability, а не только двумя последними findings.
- Successor получает production ceiling `<=300` LOC vs exact `ccccb625`, zero
  same-card repair/rescue budget и indivisible
  focused/history/benchmark/baseline floor.
- Downstream smoke parallelization зависит от опубликованного replacement.

### Depends On
- `investigate-deterministic-release-baseline-acceleration`

### Related
- `openspec/changes/decide-path-sensitive-public-history-scan-replacement/`
- `openspec/board/4.done/investigate-deterministic-release-baseline-acceleration.md`

## Log
- 2026-08-24T21:45:00Z escalation created the mandatory decision-only
  investigation after cycle-2 `NO-GO`; no exhausted payload was copied,
  committed or published.
- 2026-08-24T21:59:07Z FF preserved both forensic blockers, selected one clean
  persistent raw-tree batch hypothesis and made proposal, design, delta spec
  and tasks apply-ready; no implementation, evidence, archive or publish action
  was performed.
- 2026-08-24T22:01:03Z strict target/all validation passed `1/1` and `24/24`;
  JSON/TOML parse, current public scan `1312/0`, scoped production `0` LOC and
  tracked plus six-file untracked whitespace checks passed. History, benchmark,
  full baseline, review and publish were not run.
- 2026-08-24T22:06:08Z DO synced exactly one delta requirement, archived exactly
  one decision change, and moved the card to `3.inprogress` for normalized
  preflight and fresh independent review. No production/test/schema/runner/CLI
  or runtime change, history scan, benchmark, full baseline, verdict, commit,
  push or publish was performed.
- 2026-08-24T22:06:34Z normalized preflight passed with archived change scope,
  source-classification production delta `0`, strict all validation `23/23`,
  current public scan `1312/0` and no scope discrepancy. Tasks are complete;
  fresh independent review remains required.
- 2026-08-24T22:16:11Z same-card rescue `1/1` repaired review finding `R1`:
  `raw_name` now has one exact slash-free Git tree-component contract and a
  connected slash-bearing negative fixture before output/cache. The retained
  review verdict and review history were not edited; fresh independent re-review
  is required.
- 2026-08-24T22:25:38Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
