# Изолировать mutable Codex home delivery runner

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
- RPW delivery safety stop, 2026-08-21

## Summary
Delivery runner не должен использовать tracked project `.codex/config.toml` как
mutable user-level Codex config. Иначе Codex может автоматически записать туда
абсолютный trust-путь checkout, загрязнить card payload и остановить независимый
review после успешной реализации.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `yes`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Acceptance
- При отсутствии explicit `CODEX_HOME` runner использует ignored mutable runtime
  home и не меняет tracked `<workspace>/.codex/config.toml`, даже если Codex
  сохраняет absolute project trust во время child startup.
- Runtime home содержит exact trust binding для выбранного workspace, получает
  auth только через ignored marker/supported environment и не копирует secret
  contents.
- Preflight по-прежнему fail-closed проверяет automation authority, auth и stale
  symlinks, включая project-local skill links; explicit operator `CODEX_HOME`
  остаётся поддержанным.
- Smoke tests воспроизводят прежнюю auto-persistence mutation и доказывают, что
  tracked project config остаётся byte-identical и git-clean.
- Operator docs описывают разделение project config и mutable runtime home,
  remediation и explicit override boundary.

## Change Set
- `isolate-delivery-runner-codex-home`

## Verify
- `python3 scripts/smoke-delivery-runner.py` — PASS; the persistence fixture
  appends trust to child `CODEX_HOME` and would fail if tracked project config
  changed or generated state became committable; the negative directory-alias
  fixture also proves preflight blocks before config mutation or child launch.
- `python3 scripts/run-release-baseline.py` — PASS, 36/36 release steps; Windows
  live two-host smoke was not requested and remains explicitly not-run.
- `bin/openspec validate --all --strict` — PASS, 23 specs after archive.
- `python3 scripts/public-surface-scan.py` — PASS, 1095 files and 0 findings.
- `git diff --check` plus untracked whitespace scan — PASS.

## Archive
- `openspec/changes/archive/2026-08-21-isolate-delivery-runner-codex-home/`

## Related
- `openspec/changes/archive/2026-08-21-isolate-delivery-runner-codex-home/`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/board/2.todo/investigate-delivery-runner-child-environment-preflight-parity.md`

## Result
implemented, synced, archived and ready for independent review

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `isolate-delivery-runner-codex-home`

### Why
Tracked project configuration and mutable Codex user state currently share one
path, so an otherwise successful unattended delivery can create an unrelated,
machine-specific tracked diff before review.

### Goal
Separate the runner-owned mutable Codex home from tracked project configuration
without weakening workspace scoping, auth checks or unattended authority gates.

### Scope
- Default runtime-home preparation and child environment wiring.
- Preflight authority/auth/symlink checks for the separated layers.
- Regression smoke coverage and operator documentation.

### Acceptance
- The card-level acceptance criteria above pass with one bounded implementation.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-08-21-isolate-delivery-runner-codex-home/`

## Log
- 2026-08-21T00:00:00Z card created after deterministic reproduction of tracked config mutation
- 2026-08-21T00:05:00Z one apply-ready OpenSpec change planned and validated
- 2026-08-21T07:35:00Z implementation verified with focused smoke, OpenSpec
  validation, public-surface scan and whitespace checks; OpenSpec change synced
  and archived for independent review.
- 2026-08-21T07:40:00Z release baseline passed all 36 steps; retained evidence
  and scoped delivery manifest prepared for independent review.
- 2026-08-21T07:40:00Z linked follow-up todo card for child-environment
  preflight parity is included as planning scope only; no implementation is
  included for that follow-up.
- 2026-08-21T07:59:30Z independent review cycle 1 returned `no-go`: reject a
  symlinked runner-owned runtime-home directory before any tracked config can
  change; same-card rescue attempt 1 started.
- 2026-08-21T08:35:29Z rescue rejected symlinks throughout the runner-owned
  directory chain; RED reproduced tracked config mutation, GREEN runner smoke
  passed, and retained release baseline passed 36/36 steps.
- 2026-08-21T08:44:49Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
