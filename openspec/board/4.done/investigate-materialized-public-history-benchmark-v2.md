# Исследовать materialized public history benchmark v2

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R2-I

## Source
- Published decisions `investigate-deterministic-release-baseline-acceleration`
  (`ccccb62562e1646b595119edd3326763860f14a7`) and
  `investigate-path-sensitive-public-history-scan-replacement`
  (`c2c145ce4d107a8dfcd30603f46e46641c2009c0`).
- Pre-review `NOT-VERIFIABLE` stop in unpublished
  `deliver-path-sensitive-public-history-scan-replacement`: v1 published only
  a digest and cardinalities, not an authoritative materializable preimage.
  The stopped payload is forensic-only and MUST NOT resume or publish.

## Summary
Определить publish-before-candidate contract для `history-fixture-v2`: canonical
recipe, deterministic generator, realization verifier/golden manifest,
benchmark harness и self-tests. v2 должен сохранить масштаб, семантику и
thresholds v1, но впервые сделать benchmark независимо воспроизводимым из
tracked источника.

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
- `investigate-path-sensitive-public-history-scan-replacement`

## Blocks
- `materialize-public-history-benchmark-fixture-v2`
- `authorize-bounded-public-history-scan-replacement-v2`
- `deliver-path-sensitive-public-history-scan-replacement-v2`
- `parallelize-isolated-release-smoke-cases`

## Acceptance
- Решение явно фиксирует, что v1 остаётся историческим, но не может
  подтверждать будущий GREEN: canonical preimage отсутствует, digest+counts не
  являются generator specification.
- Выбран `history-fixture-v2`, а не восстановленный v1. Сохраняются exact scale
  `48/1152/96/72`, semantic cases, cold `<=20%`, warm `<=5%`, trial order,
  unrounded CV rule и RSS bounds.
- v2 recipe задаёт ordered raw bytes, modes, paths, parents, refs и их
  add/delete order, fixed identities/timestamps/timezone, object format,
  sanitized Git environment и binary/non-UTF8 data без randomness.
- Две независимые fresh materializations дают identical canonical realization
  transcripts, object/ref/path ordering, counts, legacy output digest и fixture
  fingerprint.
- Recipe schema, recipe, generator, realization transcript, benchmark harness
  и self-tests имеют отдельные pinned digests без self-reference. Более поздний
  authorization source пинит exact fixture commit и detached authority digest;
  runtime evidence хранит samples/host data, но не определяет fixture bytes.
- Fixture authority публикуется до создания candidate; candidate не может
  менять recipe/generator/manifest/harness. Любое byte change требует v3 и
  новой investigation.
- Решение связывает ordered successors
  `materialize-public-history-benchmark-fixture-v2`,
  `authorize-bounded-public-history-scan-replacement-v2` и
  `deliver-path-sensitive-public-history-scan-replacement-v2`.
- Authorization публикует exact six-field object с ceiling `301` и
  `allow_new_authority_or_wire_protocol:false`; candidate ссылается exact
  two-field reference, а acceptance независимо ограничивает implementation
  `<=300` production LOC относительно `ccccb625`.
- Decision-only scope: 0 production/test/runtime LOC; history scan, benchmark и
  full baseline не запускаются и GREEN не заявляется.

## Change Set
- `decide-materialized-public-history-benchmark-v2`
- `openspec/changes/archive/2026-08-24-decide-materialized-public-history-benchmark-v2/`

## Verify
- `bin/openspec validate decide-materialized-public-history-benchmark-v2
  --strict` и `bin/openspec validate --all --strict`.
- JSON/TOML parse, current public scan, source classification,
  diff/whitespace including untracked, manifest/scope/preflight.
- No history scan, benchmark or full baseline for decision-only payload.

## Related
- `openspec/changes/archive/2026-08-24-decide-materialized-public-history-benchmark-v2/`
- `openspec/board/4.done/investigate-deterministic-release-baseline-acceleration.md`
- `openspec/board/4.done/investigate-path-sensitive-public-history-scan-replacement.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
Decision-only change synced and archived; independent review is pending.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-materialized-public-history-benchmark-v2`

### Why
Ни один разрешённый tracked source не материализует exact v1 fixture; SHA-256
preimage нельзя честно реконструировать или подобрать внутри candidate.

### Goal
Опубликовать точный independent fixture-authority design до нового scanner
candidate.

### Scope
- Decision-only board/OpenSpec/spec relationship documentation.
- Production/test/runtime additions: 0 LOC.

### Acceptance
- Старый stopped successor остаётся forensic-only.
- Fixture v2 получает самостоятельную публикацию и fresh review до
  authorization и implementation.
- Exact authorization имеет ceiling `301`, protocol allowance `false` и
  reciprocal tracked-`4.done` preflight binding; implementation остается
  `<=300` production LOC относительно `ccccb625`.
- Downstream parallelization блокируется до полного v2 replacement GREEN.

### Depends On
- `investigate-deterministic-release-baseline-acceleration`
- `investigate-path-sensitive-public-history-scan-replacement`

### Related
- `openspec/changes/decide-materialized-public-history-benchmark-v2/`
- `deliver-path-sensitive-public-history-scan-replacement`
- `materialize-public-history-benchmark-fixture-v2`
- `authorize-bounded-public-history-scan-replacement-v2`
- `deliver-path-sensitive-public-history-scan-replacement-v2`

## Log
- 2026-08-24T23:01:00Z mandatory investigation created after the clean v1
  successor stopped `NOT-VERIFIABLE`; no stopped payload was imported.
- 2026-08-24T23:13:07Z FF created exactly one apply-ready decision change with
  proposal, design, release-CI delta and tasks; no production/test/runtime LOC,
  successor card, history scan, benchmark, baseline, archive, review, commit or
  push was produced.
- 2026-08-24T23:14:57Z strict target/all validation passed `1/1` and `24/24`;
  JSON/TOML, current public scan `1318/0`, classification with `0` added
  production LOC and tracked plus six-file untracked whitespace passed.
  Manifest derive/scope passed; preflight stopped only on expected FF-state
  `2.todo`/active-not-archived gates and must be rerun after DO sync/archive.
- 2026-08-24T23:18:00Z DO synced exactly one added and one modified
  `changerail-release-ci` requirement, archived
  `2026-08-24-decide-materialized-public-history-benchmark-v2`, and moved the
  decision card to review-pending `3.inprogress`; no production/test/runtime
  LOC, fixture/successor card, history scan, benchmark, full baseline, review,
  commit or push was created or run.
- 2026-08-24T23:21:00Z DO verification passed: active change strict validation
  before archive, post-archive strict validation `23/23`, JSON/TOML parse,
  current public scan `1318/0`, valid source classification, and tracked plus
  six-file untracked whitespace checks. Retained runtime evidence records
  history scan, benchmark and full baseline as not applicable to this
  decision-only payload.
- 2026-08-24T23:29:28Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
