## 1. Focused Coverage

- [x] 1.1 Add a smoke fixture proving single-card `preflight --write-status`
  records `terminal_reason: publish_target_preflight_failed` for remote-push
  publish-target failure and retains sanitized failure evidence.
- [x] 1.2 Add a smoke fixture proving delivery-plan admission blocks before
  workspace lock creation and delivery child launch when child-equivalent
  publish-target preflight fails.
- [x] 1.3 Add a smoke fixture proving `run-plan` / `resume-plan`
  dispatch-time revalidation catches later environment drift while previously
  delivered cards remain skipped and pending cards stay dependency ordered.
- [x] 1.4 Add or preserve a smoke assertion that explicit `--no-push` keeps
  local-only semantics and is not selected implicitly after remote failure.

## 2. Runner Implementation

- [x] 2.1 Reuse the existing single-card `preflight --write-status` child
  command as the delivery-plan child-equivalent receipt.
- [x] 2.2 Map failed child `publish target` checks to
  `terminal_reason: publish_target_preflight_failed` in single-card and
  aggregate status.
- [x] 2.3 Re-run child-equivalent preflight immediately before dispatching each
  unresolved card and before creating the workspace lock.
- [x] 2.4 Preserve existing retry taxonomy, sanitized diagnostics,
  `run_status_path` references, Windows/custom-launcher support and explicit
  `--no-push` behavior.

## 3. Docs And Specs

- [x] 3.1 Sync the delta spec into
  `openspec/specs/changerail-delivery-runner/spec.md`.
- [x] 3.2 Update durable runner contract docs if the operator-visible terminal
  reason or queue behavior changes.
- [x] 3.3 Update the board card result, archive path and delivery manifest with
  concise verification evidence.

## 4. Verification

- [x] 4.1 Record RED evidence for the new focused smoke fixtures before the
  implementation fix.
- [x] 4.2 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 4.3 Run `bin/openspec validate add-delivery-runner-child-equivalent-preflight --strict`.
- [x] 4.4 Run `bin/openspec validate --all --strict`.
- [x] 4.5 Run `git diff --check`.
- [x] 4.6 Run `python3 scripts/public-surface-scan.py`.
- [x] 4.7 Run `python3 scripts/run-release-baseline.py`.
