# Исследовать structural proof для public history scan

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R3-I

## Source
- Published decisions `ccccb62562e1646b595119edd3326763860f14a7`,
  `c2c145ce4d107a8dfcd30603f46e46641c2009c0` and
  `f6b56f11593e56fddbd6a718f6abe5418ade9129`.
- Published evidence certification
  `3915f54f017e3bf7b9af785f62519a87b75f9b9c`.
- Exhausted unpublished fixture-v2 implementation and its two `NO-GO`
  verdicts are forensic-only and MUST NOT publish or be copied.

## Summary
Отказаться от synthetic fixture authority, persistent cross-run cache,
warm-ratio/CV threshold и недоказуемого descendant-RSS oracle. Выбрать
структурное доказательство: fresh reachability, constant Git child-launch
bound, invocation-local memoization, differential real-Git semantics и один
финальный real history/baseline run.

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
- `investigate-materialized-public-history-benchmark-v2`

## Blocks
- `authorize-bounded-structural-public-history-scan`
- `deliver-structurally-bounded-public-history-scan`
- `parallelize-isolated-release-smoke-cases`

## Acceptance
- Решение supersedes fixture-v2 только для future delivery; старые decisions,
  certification и forensic evidence остаются неизменными и не объявляются
  принятыми implementation evidence.
- Каждый history run заново выполняет `git rev-list --all`, запускает ровно один
  persistent `git cat-file --batch`, использует только invocation-local memo,
  не использует persistent cross-run cache/state и не меняет refs/worktree/index.
- Commit/tree object запрашивается не более одного раза per invocation;
  selected `(blob OID, exact path)` сканируется не более одного раза, затем
  findings детерминированно expand на все reachable commit occurrences.
- Strict raw Git object/batch/path parsing fail-closed для malformed/truncated/
  mistyped/missing/unsafe data до partial success.
- PATH-wrapped real Git connected test доказывает одинаковый exact child-launch
  count для small и enlarged histories; independent `rev-list` + `ls-tree`
  verifier сравнивает actual ordered `(commit,path,blob)` coverage.
- Connected independent oracle вне counted candidate `PATH` снимает до и после
  каждого successful/fault-injected run complete refs, exhaustive raw worktree
  mapping и exact raw Git index bytes; соответствующие snapshots идентичны.
- Small real Git repos подтверждают legacy parity для allowed/leak/redaction,
  rename/path identity, binary/non-UTF8 и fault cases без превращения fixture в
  tracked benchmark authority.
- Performance PASS не зависит от wall/RSS threshold. `/usr/bin/time -v` хранит
  observational timing/max-RSS; один final current-history и один full baseline
  на exact payload являются обязательными correctness evidence.
- CI public-history scan требует full checkout `fetch-depth: 0`; shallow history
  не может считаться полным `--all` proof.
- Решение связывает exact authorization
  `authorize-bounded-structural-public-history-scan` и successor
  `deliver-structurally-bounded-public-history-scan`, auth ceiling `301`, actual
  production ceiling `<=300` vs `ccccb625`, protocol `false`.
- Published authorization source обязан содержать exact
  `{"investigation_card":"openspec/board/4.done/investigate-structural-public-history-scan-proof.md","investigation_id":"investigate-structural-public-history-scan-proof","successor_card":"openspec/board/3.inprogress/deliver-structurally-bounded-public-history-scan.md","successor_id":"deliver-structurally-bounded-public-history-scan","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}`;
  successor использует только
  `{"authorization_card":"openspec/board/4.done/authorize-bounded-structural-public-history-scan.md","authorization_id":"authorize-bounded-structural-public-history-scan"}`.
- Decision-only scope: 0 production/test/runtime LOC; history/baseline не
  запускаются.

## Change Set
- `decide-structural-public-history-scan-proof`

## Verify
- Strict OpenSpec, JSON/TOML, current scan, classification,
  diff/whitespace, manifest/scope/preflight.
- No history scan, benchmark or full baseline.

## Related
- `openspec/changes/decide-structural-public-history-scan-proof/`
- `openspec/board/4.done/investigate-deterministic-release-baseline-acceleration.md`
- `openspec/board/4.done/investigate-path-sensitive-public-history-scan-replacement.md`
- `openspec/board/4.done/investigate-materialized-public-history-benchmark-v2.md`
- `openspec/board/4.done/certify-materialized-public-history-fixture-v2-history-evidence.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
Decision `decide-structural-public-history-scan-proof` is synced to
`changerail-release-ci` and archived at
`openspec/changes/archive/2026-08-25-decide-structural-public-history-scan-proof/`.
Production/test/runtime additions remain `0` LOC; no successor, history scan,
benchmark or full baseline was created or run. The payload is ready for an
independent ordinary review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-structural-public-history-scan-proof`

### Why
Две bounded fixture попытки показали, что synthetic recipe/transcript/RSS
authority сложнее проверяемого production change и создаёт новые defect classes.

### Goal
Опубликовать минимальный structural proof contract для чистого scanner
successor без benchmark gaming и cross-run state.

### Scope
- Decision-only board/OpenSpec/release-CI contract docs.
- Production/test/runtime additions: 0 LOC.

### Acceptance
- Fixture-v2 lineage остаётся forensic-only.
- Authorization и implementation создаются только после published GO.
- Future scanner использует fresh `rev-list --all`, exact one persistent
  `cat-file --batch`, только invocation-local memo без persistent cross-run
  state и strict fail-closed parsing; он не изменяет refs/worktree/index.
- PATH-wrapped count, independent actual tuple enumeration и small real-Git
  parity/fault tests вместе с independent before/after refs/worktree/index
  oracle являются correctness proof; timing/RSS остаются observational.
- После implementation публикуется smoke parallelization, затем возобновляется
  phase-routed runner series.

### Depends On
- `investigate-materialized-public-history-benchmark-v2`

### Related
- `openspec/changes/decide-structural-public-history-scan-proof/`
- `openspec/specs/changerail-release-ci/spec.md`

## Log
- 2026-08-25T01:44:00Z structural simplification investigation created from
  published certification commit; no forensic payload imported.
- 2026-08-25T02:01:31Z FF created exactly one apply-ready decision change with
  proposal, design, release-CI delta and tasks; no production/test/runtime LOC,
  successor, history scan, benchmark, baseline, archive, review, commit or push
  was created or run.
- 2026-08-25T02:04:57Z FF verification passed strict target and strict all
  `24/24`, JSON/TOML parse, current-only public scan `1330/0`, source
  classification `0` blockers/`0` advisories, tracked plus six-file untracked
  whitespace and manifest derive/scope. Normalized preflight confirmed
  `ordinary`/`high`, added production LOC `0` and no new authority/protocol; it
  blocked only on expected FF-state `2.todo` and active-not-archived gates.
- 2026-08-25T02:11:00Z DO synced the exact release-CI delta, completed all
  decision-only checks and archived the sole change. Strict change/capability/all
  validation passed (`24/24` all); JSON/TOML, current-only public scan `1330/0`,
  source classification `0/0`, tracked and untracked whitespace, manifest scope
  and normalized preflight passed. No history scan, benchmark or full baseline
  was run; payload is in `3.inprogress` for independent review.
- 2026-08-25T02:27:38Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
