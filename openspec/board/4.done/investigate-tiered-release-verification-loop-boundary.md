# Исследовать tiered release verification loop boundary

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R5-I

## Source
- Published acceleration decision
  `investigate-deterministic-release-baseline-acceleration`, commit `ccccb625`.
- Published Git-header rescue decision
  `rescue-git-commit-header-compatibility-decision`, commit `b7bd6f7`.
- Published Git-compatible scanner authorization
  `authorize-bounded-git-commit-header-compatible-history-scan`, commit
  `45a2de9`.
- Terminal unpublished successor
  `deliver-git-compatible-structural-public-history-scan-replacement` is
  forensic-only: final history PASS `1.8 s`, but its only baseline stopped at
  step 10 because worktree-local `ruff` was not admitted before expensive
  Windows checks. Its code/diff/evidence is not reusable.

## Summary
Зафиксировать новый verification authority boundary: cheap affected inner loop
без publish authority и frozen full-release profile с fail-fast toolchain
admission, exactly-once semantic coverage и bounded concurrent Windows cases.
Решение явно заменяет прежний process-invocation non-goal, но не ослабляет
обязательный release coverage.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Planning: fresh `gpt-5.6-sol`/`high`
- Implementation: fresh `gpt-5.6-terra`/`high`
- Independent review: fresh `gpt-5.6-sol`/`xhigh`
- Same-card repair: at most one fresh `gpt-5.6-terra`/`high`
- Re-review: fresh `gpt-5.6-sol`/`xhigh`
- Same-card repair/rescue budget limit/used/remaining: `1/1/0`, exhausted
  `true`

Этот decision-only payload описывает и связывает будущую authority, но не
изменяет executable authority или wire behavior. Terminal repeated defects
являются входом simplification investigation; forensic implementation в этот
payload не переносится.

## Depends On
- `investigate-deterministic-release-baseline-acceleration`
- `rescue-git-commit-header-compatibility-decision`
- `authorize-bounded-git-commit-header-compatible-history-scan`

## Blocks
- `authorize-bounded-tiered-release-verification-loop`
- `implement-tiered-release-verification-loop`
- `authorize-bounded-parallel-verify-project-cases`
- `parallelize-isolated-verify-project-cases`
- `authorize-clean-git-compatible-structural-history-scan-v2`
- `deliver-clean-git-compatible-structural-history-scan-v2`
- `parallelize-isolated-release-smoke-cases`

## Acceptance
- Decision заменяет mandatory process invocation на frozen semantic check ID:
  full-release inventory сохраняет полный набор проверок, exact one owner на ID,
  deterministic order/report и fail-closed unknown/missing/duplicate ownership.
- Frozen inventory содержит ровно 35 ordered leaf IDs; canonical newline-list
  SHA-256 равен
  `7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`.
- Startup admission до первого semantic child проверяет exact usable release
  toolchain, включая pinned `ruff`, Python modules, Git и OpenSpec/npm path;
  missing/mismatched dependency завершает run до дорогих tests.
- Шесть local Windows cases получают isolated temp/report roots, bounded jobs
  `1..8`, default `min(4,cpu)`, stable registry-order aggregation, timeout/crash/
  oversized-output cleanup и jobs-1/default semantic parity.
- Четыре доказанных duplicate standalone invocations (`entrypoints`, wiring Git
  safety, bootstrap, verify-project) удаляются только как процессы: каждый
  semantic ID остаётся exactly once внутри authoritative matrix.
- Existing local/live split сохраняется: default local не читает inventory и не
  контактирует с hosts; explicit `--live` остаётся отдельным operator gate.
- `--profile affected --base <ref>` является non-authoritative inner loop.
  Bounded path map покрывает add/modify/delete/rename/untracked/multi-area;
  unknown, ambiguity или selector/self-change расширяются до full inventory.
- Только frozen `--profile full-release` принимается review/pub/CI. Affected
  receipt не может удовлетворить publish gate; CI вызывает canonical full
  runner. Каждый executable successor выполняет ровно один predeclared
  terminal full baseline capture без retry после focused GREEN.
- Decision разделяет implementation на три authorization lineages: tiered
  orchestration `<=499` executable LOC vs `45a2de9`, then isolated
  `verify-project` cases `<=500` executable LOC vs published orchestration
  HEAD, and an independent clean structural scanner v2 `<=300` LOC vs that
  same tiered HEAD. Existing `parallelize-isolated-release-smoke-cases`
  remains the separate review/delivery-smoke successor.
- Docs-only decision: production/test/runtime LOC `0`; history scan и baseline
  не запускаются.

## Change Set
- `decide-tiered-release-verification-loop-boundary`

## Verify
- Strict target/capability/all OpenSpec validation and exact scenario ownership.
- JSON/TOML, current-only public scan, classification, diff/whitespace,
  manifest/scope and normalized critical/xhigh preflight.
- No history scan, benchmark or full baseline.

## Result
Cycle-1 R1 repair complete; fresh independent re-review is pending. Exactly
one archived docs-only decision change fixes toolchain admission, frozen
semantic ownership, Windows concurrency, local/live isolation, affected/full
authority and three ordered authorization boundaries. The repair replaces the
three divergent canonical MODIFIED requirement blocks with their complete
archived delta versions; production/test/runtime files, successor artifacts,
history scan and full baseline remain untouched.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Related
- `openspec/changes/decide-tiered-release-verification-loop-boundary/`
- `openspec/specs/changerail-release-ci/spec.md`
- `scripts/run-release-baseline.py`
- `scripts/smoke-windows-matrix.py`
- `.github/workflows/changerail-ci.yml`

## Change 1: `decide-tiered-release-verification-loop-boundary`

### Why
History acceleration exposed orchestration as the dominant cost and allowed an
expensive matrix to start before required release tooling was available.

### Goal
Define a fast non-authoritative inner loop and a complete, deterministic,
fail-fast full-release authority without duplicated semantic execution.

### Scope
- Decision/card and `changerail-release-ci` contract only.
- Exact three future authorization and implementation boundaries.
- Production/test/runtime LOC: 0.

### Acceptance
- Toolchain admission, semantic-ID ownership, Windows bounded concurrency,
  local/live separation and affected/full authority rules are deterministic.
- Full semantic coverage is preserved while duplicate process executions are
  removed.
- Exact future tiered authorization uses ceiling `500`, protocol allowance
  `true` and `<=499` production LOC against
  `45a2de98924c61bb9e944767013ea09918bba4b0`; scanner v2 uses a separate
  post-tiered ceiling `301`, protocol allowance `false` and `<=300` LOC against
  exact published tiered HEAD. The post-tiered `verify-project` authorization
  uses ceiling `501`, protocol allowance `false` and `<=500` LOC against exact
  published tiered HEAD; it fixes a frozen static registry for all current
  approximately 73 assertions and 45 run paths, immutable fixture/copy
  isolation, bounded jobs, exact CLI sentinels and no cache.
- Terminal unpublished scanner artifacts remain forensic-only and absent.

### Depends On
- `investigate-deterministic-release-baseline-acceleration`
- `rescue-git-commit-header-compatibility-decision`
- `authorize-bounded-git-commit-header-compatible-history-scan`

### Related
- `openspec/changes/decide-tiered-release-verification-loop-boundary/`

## Log
- 2026-08-25T06:05:00Z decision card created after terminal missing-toolchain
  outcome and user-directed expansion to a radically shorter inner loop.
- 2026-08-25T06:10:00Z FF prepared exactly one apply-ready docs-only decision
  change with 35 frozen semantic IDs, pre-child toolchain admission, bounded
  six-case Windows ownership, non-authoritative affected selection and two
  ordered authorization scopes. No successor, implementation, main-spec sync,
  history scan, baseline, archive, review, commit or push was created.
- 2026-08-25T06:18:00Z DO synced `changerail-release-ci`, archived the sole
  decision change, completed docs-only strict/current scans and moved this card
  to independent critical review. History scan, benchmark and full baseline
  remain intentionally not-run.
- 2026-08-25T06:25:00Z Scope expanded before final DO handoff: a separately
  authorized, post-tiered `verify-project` parallelization successor retains a
  frozen completeness oracle, isolated fixtures and exact CLI ownership. No
  successor artifact, executable change, history scan or baseline was created.
- 2026-08-25T06:30:00Z Pre-review deterministic metadata correction records
  this payload as decision-only `no/no`; future executable authority remains
  gated by its separate exact authorization.
- 2026-08-25T06:33:00Z Cycle-1 R1 bounded Terra/high repair consumed the sole
  same-card repair budget. It replaced exactly the three divergent canonical
  MODIFIED requirement blocks with their complete archived-delta versions;
  the fourth MODIFIED block and all unrelated main-spec content/order remain
  unchanged. Fresh strict/ownership/scope/preflight evidence is pending a
  fresh independent Sol/xhigh re-review; the cycle-1 verdict/history remain
  preserved as forensic runtime evidence.
- 2026-08-25T06:42:58Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
