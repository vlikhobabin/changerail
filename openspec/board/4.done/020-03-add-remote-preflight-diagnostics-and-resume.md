# Добавить remote preflight diagnostics и resume

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`020-one-command-delivery-experience`

## Series Index
`03`

## Source
- Consumer runner дважды остановился на execution-surface-dependent remote
  preflight, после чего тот же publish target оказался доступен.

## Summary
Классифицировать remote-push preflight failures, сохранять sanitized evidence
и поддержать explicit resume после transient failure с обязательным fresh
повторным proof.

## Acceptance
- Failure classes различают SSH config, DNS, auth, missing branch, timeout и
  unknown remote failure.
- Status использует canonical `changerail.delivery-run.v1` fields и не вводит
  дублирующие top-level `id/status/started_at` aliases.
- Structured preflight evidence содержит sanitized command/result/detail.
- Ограниченный retry/backoff применяется только к transient classes.
- Explicit resume принимает prior status, повторяет полный fresh preflight и
  продолжает только при доказанном publish target.
- Auth/branch uncertainty остается fail-closed.
- Smokes воспроизводят failure classes и later-success resume без сети.

## Scope
- Single-card и queue runner preflight/status/resume contracts.
- Operator diagnostics и migration docs.

## Non-Goals
- Автоматический бесконечный retry.
- Credential storage или обход SSH policy.

## Depends On
- `020-02-add-retained-delivery-evidence`
- `010-03-fix-publish-finalization-ledger`

## Implementation Notes
- Сохранять raw stderr только в ignored evidence; compact status должен быть
  bounded и secret-free.
- Fallback `ssh -F /dev/null` допустим только как явно документированный probe,
  а не скрытая замена approved operator config.

## Change Set
- `add-remote-preflight-diagnostics-and-resume` (archived:
  `openspec/changes/archive/2026-08-01-add-remote-preflight-diagnostics-and-resume/`)

## Change 1: `add-remote-preflight-diagnostics-and-resume`

### Why
Remote-push preflight failures can be transient, but current runner status does
not preserve enough sanitized evidence or resume semantics to continue safely
without manual reconstruction.

### Goal
Classify remote preflight failures, retain sanitized evidence, and make resume
repeat a full fresh publish-target proof before continuing.

### Scope
- Single-card and queue runner preflight/status/resume contracts.
- Operator diagnostics and migration docs.

### Acceptance
- Failure classes различают SSH config, DNS, auth, missing branch, timeout и
  unknown remote failure.
- Status использует canonical `changerail.delivery-run.v1` fields и не вводит
  дублирующие top-level `id/status/started_at` aliases.
- Structured preflight evidence содержит sanitized command/result/detail.
- Ограниченный retry/backoff применяется только к transient classes.
- Explicit resume принимает prior status, повторяет полный fresh preflight и
  продолжает только при доказанном publish target.
- Auth/branch uncertainty остается fail-closed.
- Smokes воспроизводят failure classes и later-success resume без сети.

### Depends On
- `add-retained-delivery-evidence`
- `fix-publish-finalization-ledger`

### Related
- `openspec/changes/archive/2026-08-01-add-remote-preflight-diagnostics-and-resume/`

## Verify
- `python3 scripts/smoke-delivery-runner.py` -> passed; covers SSH config, DNS,
  auth, missing branch, timeout and unknown remote failure classes, bounded
  transient retry, later-success single-card resume and queue remote failure
  propagation without network.
- `python3 scripts/smoke-contract-schemas.py` -> passed; covers remote
  preflight evidence fields and rejects duplicate top-level status aliases.
- `python3 scripts/smoke-delivery-manifest.py` -> passed.
- `./bin/openspec validate add-remote-preflight-diagnostics-and-resume --strict`
  -> passed before archive.
- `./bin/openspec validate changerail-delivery-runner --strict` -> passed after
  spec sync.
- `./bin/openspec validate changerail-contracts --strict` -> passed after spec
  sync.
- `./bin/openspec validate --all --strict` -> passed before archive: 15 items.
- `git diff --check` -> passed.
- Untracked artifact whitespace scan -> passed before archive.
- `python3 scripts/public-surface-scan.py` -> passed, 633 files scanned,
  0 findings.
- `python3 scripts/run-release-baseline.py` -> passed, 27/27 steps.
- Test adequacy: fake `git` fixtures intercept only `ls-remote`, assert exact
  `failure_class`, `retryable`, attempt count and sanitized evidence, and would
  fail if auth/branch classes retried, transient classes skipped retry, raw
  remote URLs leaked, resume skipped fresh preflight or queue status inlined
  child logs. Separate RED output was not retained; existing generic failure
  behavior was confirmed by source inspection before adding regression smokes.

## Archive
- `openspec/changes/archive/2026-08-01-add-remote-preflight-diagnostics-and-resume/`

## Related
- `openspec/board/1.backlog/020-00-one-command-delivery-experience-epic.md`
- `bin/changerail-delivery-runner`
- `schemas/changerail-delivery-run.schema.json`
- `docs/changerail-contracts.md`

## Result
Implemented classified remote-push preflight diagnostics, sanitized structured
preflight evidence, bounded transient retry, explicit single-card resume with
fresh publish-target proof, queue propagation of child remote failure class,
schema/docs updates and offline smoke coverage. Specs synced and OpenSpec
change archived and fresh independent review returned `go`.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-01T15:07:29Z карточка нормализована из E1 runner feedback.
- 2026-08-01T21:24:05Z readiness pass после серии `010`: карточка переведена
  в `2.todo`, добавлен ordered Change 1 для package runner.
- 2026-08-01T23:02:36Z ff: созданы apply-ready artifacts для
  `add-remote-preflight-diagnostics-and-resume`, карточка переведена в
  `3.inprogress`.
- 2026-08-01T23:19:06Z do: реализованы remote preflight diagnostics/resume,
  specs синхронизированы, change archived, release baseline passed 27/27.
- 2026-08-01T23:26:18Z independent review cycle 1 returned `go` with no
  findings.
- 2026-08-01T23:34:29Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
