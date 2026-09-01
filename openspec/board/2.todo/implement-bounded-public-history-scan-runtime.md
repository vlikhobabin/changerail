# Реализовать bounded public history scan runtime

## Status
2.todo

## Owner
ChangeRail maintainers

## OpenSpec Stage
not-started

## Series
- none

## Series Index
- none

## Source
- `investigate-bounded-public-history-scan-runtime`
- Decision archive:
  `openspec/changes/archive/2026-08-31-decide-bounded-public-history-scan-runtime/`

## Summary
Заменить per-commit/per-path Git process fan-out history scanner на bounded
unique-blob stream для одного полного release `HEAD`, сохранив public-safety
rules, secret redaction и commit/path attribution.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Production-counted additions ограничены 300 LOC. Investigation не разрешает
новую authority, report schema или release-ref CLI. Отдельная authorization
card не нужна; превышение границы требует split или нового investigation.

## Depends On
- `investigate-bounded-public-history-scan-runtime`

## Blocks
- `stabilize-first-stable-release-scope`
- `prepare-1-0-0-stable-release`

## Acceptance
- `--history` разрешает один полный `HEAD^{commit}`, не зависит от unrelated
  local refs и fail closed для missing/unborn `HEAD` или shallow history.
- Один raw-history process с exact
  `--format=tformat:%x1e%H --raw -z --no-abbrev` framing перечисляет reachable
  public blob occurrences; один persistent `cat-file --batch` читает каждый
  уникальный blob не более одного раза, максимум history phase — три Git
  process launches.
- Finding сохраняет existing structured commit/path attribution; malformed или
  truncated raw/size framing, process failure и timeout дают redacted non-zero
  result в unchanged `changerail.public-surface-scan.v1` без raw content
  leakage.
- Focused public-safe fixture покрывает минимум 250 commits, 20 paths, reused
  blobs, deletion, rename, merge resolution, binary/invalid UTF-8, multi-path
  finding, excluded root и unrelated ref; scan укладывается в 30 секунд.
- Полный clean-checkout release baseline укладывается в 300 секунд, а current
  self-test, history detection и secret redaction остаются зелёными.

## Change Set
- `implement-bounded-public-history-scan-runtime`

## Verify
- `python3 scripts/public-surface-scan.py --self-test`
- `timeout 30s python3 scripts/smoke-public-surface-history.py`
- `timeout 300s python3 scripts/run-release-baseline.py`
- `bin/openspec validate --all --strict`
- `python3 scripts/public-surface-scan.py`
- `git diff --check`

## Archive
- not started

## Related
- `openspec/changes/archive/2026-08-31-decide-bounded-public-history-scan-runtime/`
- `scripts/public-surface-scan.py`
- `scripts/run-release-baseline.py`

## Result
pending

## Next
- `$changerail-deliver openspec/board/2.todo/implement-bounded-public-history-scan-runtime.md`

## Change 1: `implement-bounded-public-history-scan-runtime`

### Why
Текущий `1 + commits + commit/path occurrences` process fan-out делает
обязательный release history gate unbounded.

### Goal
Реализовать опубликованное bounded stream decision без расширения public
authority или report schema.

### Scope
- `scripts/public-surface-scan.py` history enumeration и batch-object reader;
- один focused public-safe semantic/process-count/benchmark smoke;
- `changerail-release-ci` implementation sync и card evidence;
- не более 300 added production-counted LOC.

### Acceptance
- Полное release-reachable unique-blob coverage, attribution, strict framing,
  process count и time ceilings доказаны focused и release baseline checks.

### Depends On
- `decide-bounded-public-history-scan-runtime`

### Related
- `openspec/changes/implement-bounded-public-history-scan-runtime/`

## Log
- 2026-08-31T00:00:00Z создано из опубликованной bounded decision; отдельная
  authorization не требуется при сохранении ordinary 300 LOC boundary.
