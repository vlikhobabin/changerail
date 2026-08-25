# Сертифицировать history evidence для materialized fixture v2

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R2-FE

## Source
- Published investigation `investigate-materialized-public-history-benchmark-v2`,
  commit `f6b56f11593e56fddbd6a718f6abe5418ade9129`.
- Unpublished source card `materialize-public-history-benchmark-fixture-v2`,
  cycle-1 `NO-GO`, repaired exact source review fingerprint
  `sha256:ac7a7dad192e227a734f7ef715f8e57b1369f21a54b890e1bbf323c27ebcf88d`,
  fixture fingerprint
  `sha256:59f686b634dd16a443894995e6a05c6630688263f3335b24c3c116fdf5e0d128`,
  exact `authority.json` SHA-256
  `6b02ffd9f6af7f4d18afb18ff11a34ac88add48bba41b66e5cc990725a0bbe79`,
  selftest `red_cases=94`.
- Retained source capture `public-history-final`: terminal `timeout` after
  `300.119` seconds under the fixed 300-second limit, zero output bytes, no
  exit code, not verifiable and never retried.

## Summary
Зафиксировать в tracked policy и выполнить ровно один separate public-history
certification capture для неизменного repaired fixture payload. Отличить
детерминированный public-safety scan от performance benchmark selection,
сохранить первый timeout и разрешить source card только review-only
continuation без source edits.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `yes`
- Published investigation authorization: `none`
- Same-card repair/rescue budget limit/used/remaining: `0/0/0`, exhausted
  `true`

## Depends On
- `investigate-materialized-public-history-benchmark-v2`

## Blocks
- `materialize-public-history-benchmark-fixture-v2`

## Acceptance
- Старый `public-history-final` 300-second timeout сохраняется отдельно и
  никогда не заменяется или объявляется PASS; его empty output и absent exit
  code остаются authentic evidence.
- До capture tracked board/OpenSpec/spec policy bytes finalized и
  precommitted: они уже фиксируют exact source identity, command, timeout,
  output oracle и terminal no-retry rule. Это не является claim, что policy
  reviewed или published: fresh final-certification review и publish выполняются
  только после terminal capture evidence.
- Ровно один canonical capture id `public-history-certification` выполняет
  `python3 scripts/public-surface-scan.py --history --json` на exact source
  worktree с заранее фиксированным timeout `1200` seconds. Перед запуском id
  обязан отсутствовать. Prior authentic duration `627.163` seconds используется
  только как outcome-independent calibration.
- Capture не повторяется при PASS, FAIL или TIMEOUT; casual diagnostic scan не
  может быть promoted, renamed, copied или upserted в evidence. Performance
  benchmark warmup/sample/CV rules к этому public-safety gate неприменимы.
- До и после capture source review fingerprint остаётся exact
  `sha256:ac7a7dad192e227a734f7ef715f8e57b1369f21a54b890e1bbf323c27ebcf88d`,
  fixture fingerprint exact
  `sha256:59f686b634dd16a443894995e6a05c6630688263f3335b24c3c116fdf5e0d128`,
  `authority.json` SHA-256 exact
  `6b02ffd9f6af7f4d18afb18ff11a34ac88add48bba41b66e5cc990725a0bbe79`,
  а все семь authority paths имеют predeclared identical before/after hashes.
  Certification не редактирует и не копирует fixture paths, source card,
  scanner candidate или stopped implementation.
- PASS требует completion до timeout, exit 0, `timed_out: false`, ровно один
  complete JSON object schema `changerail.public-surface-scan.v1`,
  `history: true`, `summary.status: pass`, `summary.findings: 0`, `findings: []`
  и unchanged before/after identities. Exit 1/findings, other nonzero exit,
  malformed/incomplete output, timeout или drift являются terminal и не
  разрешают source review/publish.
- Card scope содержит только board/OpenSpec/spec evidence-policy docs и ignored
  evidence/manifest. Production/test/runtime LOC 0; candidate benchmark и full
  baseline не запускаются.
- После capture PASS certification получает ровно один fresh independent
  critical Sol/`xhigh` final-certification review с milestone audit disabled и
  публикуется только после GO.
- После remote-reachable certification PASS original source получает ровно
  один fresh cycle-2 Sol/`xhigh` re-review без нового source edit/scan и без
  reciprocal tracked link. Source GO может перейти к publish; любой source
  `NO-GO` завершает original без repair.

## Change Set
- `certify-materialized-public-history-fixture-v2-history-evidence`
- `openspec/changes/certify-materialized-public-history-fixture-v2-history-evidence/`

## Verify
- Strict target/all OpenSpec, JSON/TOML, current-only public scan, source
  classification, zero production/test/runtime LOC, tracked plus untracked
  diff/whitespace, manifest/scope/preflight.
- One retained `public-history-certification` capture at timeout 1200 seconds,
  with exact before/after fingerprints and seven path hashes.
- Fresh critical Sol/`xhigh` final-certification review; milestone audit `no`,
  no fixture materialization, candidate benchmark or full baseline.

## Result
The sole certification capture passed its closed oracle with unchanged source
identity. Documentation verification and normalized critical preflight passed;
fresh independent critical review and publication remain pending and are not
claimed.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Related
- `openspec/changes/certify-materialized-public-history-fixture-v2-history-evidence/`
- `openspec/board/3.inprogress/materialize-public-history-benchmark-fixture-v2.md`
- `fixtures/public-history-v2/authority.json`
- `openspec/specs/changerail-release-ci/spec.md`

## Next
- done

## Change 1: `certify-materialized-public-history-fixture-v2-history-evidence`

### Why
Source card exhausted its single card-owned history capture on an
outcome-free local timeout; repeating it on the same capture lineage would
select evidence after observing the outcome.

### Goal
Создать отдельную predeclared one-shot certification lineage для deterministic
public history safety result без изменения fixture authority.

### Scope
- Evidence-policy board/OpenSpec/spec documentation only.
- Ignored evidence/manifest state.
- Added production/test/runtime LOC: 0.
- One-way certification-to-source reference; no tracked or runtime source
  mutation.

### Acceptance
- Capture policy finalized и precommitted в tracked payload до выполнения
  command, но не объявляется reviewed/published до post-capture final review.
- Результат принимается terminally и связывает exact source/fixture/authority
  fingerprints и семь immutable before/after path hashes.
- Source continuation остаётся review-only, без scan/edit/retry/repair.

### Depends On
- `investigate-materialized-public-history-benchmark-v2`

### Related
- `openspec/changes/certify-materialized-public-history-fixture-v2-history-evidence/`
- `openspec/board/3.inprogress/materialize-public-history-benchmark-fixture-v2.md`
- `fixtures/public-history-v2/authority.json`

## Log
- 2026-08-25T00:40:00Z certification card created after retained 300-second
  timeout; no replacement capture has run yet.
- 2026-08-25T00:53:00Z FF created exactly one apply-ready documentation and
  evidence-policy change with proposal, design, release-CI delta and tasks;
  production/test/runtime LOC is zero, and no capture, reachable-history scan,
  fixture materialization, benchmark, full baseline, archive, review, commit or
  push ran.
- 2026-08-25T00:54:21Z FF verification passed strict target `1/1`, strict all
  `24/24`, JSON/TOML parse, current-only public scan `1324/0`, source
  classification with zero blockers/advisories, six-file untracked whitespace
  and manifest scope. Preflight confirmed `critical`/`xhigh`, final
  certification `yes`, milestone audit `no` and zero added production LOC; it
  blocked only on expected FF state `2.todo` and active-not-archived change.
- 2026-08-25T01:xx:xxZ DO synced the exact `changerail-release-ci` delta,
  finalized the predeclared policy and moved this review-gated card to
  `3.inprogress`; archive and one-shot capture evidence remain pending at this
  log point. This does not claim review, publication or a capture result.
- 2026-08-25T01:01:40Z-01:13:50Z DO executed the only
  `public-history-certification` capture with timeout `1200`: exit `0`,
  `timed_out: false`, duration `729.566` seconds, one complete
  `changerail.public-surface-scan.v1` history report with `pass`, zero findings
  and `findings: []`. Before/after source review fingerprint
  `sha256:ac7a7dad192e227a734f7ef715f8e57b1369f21a54b890e1bbf323c27ebcf88d`,
  tree `d83870bb9de7d5bbaea1a1b6b9bdc6e62ac5549a`, fixture fingerprint
  `sha256:59f686b634dd16a443894995e6a05c6630688263f3335b24c3c116fdf5e0d128`,
  authority SHA-256 `6b02ffd9f6af7f4d18afb18ff11a34ac88add48bba41b66e5cc990725a0bbe79`
  and all seven pinned path hashes remained exact. Raw stdout/stderr, state and
  evidence index are retained only under ignored certification runtime state;
  no retry occurred. Fresh independent critical review remains required.
- 2026-08-25T01:15:50Z post-capture documentation verification passed:
  `changerail-release-ci` strict target and strict all `23/23`, JSON/TOML,
  current-only public scan `1324/0`, source classification `0/0`, tracked and
  untracked whitespace, evidence-index validation and manifest scope. Normalized
  preflight is `ready-for-llm-review` at `critical`/`xhigh`, milestone audit
  disabled, final certification enabled and added production LOC `0`.
- 2026-08-25T01:28:20Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
