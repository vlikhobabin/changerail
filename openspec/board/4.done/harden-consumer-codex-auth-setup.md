# Harden consumer Codex auth setup for delivery runner

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Consumer adoption feedback from a ChangeRail delivery-plan setup on
  2026-07-23.
- `docs/how-it-works.md`
- `docs/changerail-contracts.md`
- `docs/consumer-adoption-runbook.md`
- `bin/bootstrap-project`
- `bin/verify-project`
- `bin/changerail-delivery-runner`

## Summary
ChangeRail delivery runner already documents and enforces an effective
`CODEX_HOME` contract: if the operator does not set `CODEX_HOME`, runner
preflight uses `<workspace>/.codex` and fails when no supported Codex auth
marker or auth environment variable is present. This is correct fail-closed
behavior for unattended `run-plan`.

The consumer setup path is weaker: bootstrap and verify wiring can pass while
the repository still lacks a project-local Codex auth marker. The first
`preflight-plan` then fails with `CODEX auth: fail`, even though the consumer
appears fully installed from `verify-project`.

Tighten the consumer installation/runbook so operators know that delivery-plan
automation requires one of:

- a project-local ignored auth marker such as `.codex/auth.json`, usually a
  symlink to the user's existing Codex auth;
- an explicit `CODEX_HOME` pointing at an authenticated Codex home;
- a supported auth environment variable.

Do this without committing credentials, copying secrets by default, or making
machine-local auth state part of the public ChangeRail repository surface.

## Acceptance
- Consumer adoption docs explicitly describe the Codex auth prerequisite for
  `changerail-delivery-runner run`, `preflight-plan`, `run-plan` and
  `resume-plan`.
- Docs provide safe remediation examples using generic paths only, including a
  symlink-based project-local marker and an explicit `CODEX_HOME` invocation.
- Bootstrap guidance states that `.codex/auth.json` must remain ignored and
  untracked, and explains why ChangeRail must not silently copy credentials by
  default.
- Either `bin/bootstrap-project` gains an explicit opt-in local setup mode
  such as `--link-codex-auth`, or docs clearly state the post-bootstrap manual
  command and when to use it.
- `verify-project` and/or bootstrap output gives a clear advisory for delivery
  runner readiness without requiring a real auth marker for public CI,
  unauthenticated template smoke tests or non-runner consumers.
- Runner preflight diagnostics remain fail-closed for missing auth and stale
  symlinks, and the error text points operators to the new remediation section.
- Smoke coverage proves that authenticated marker, explicit `CODEX_HOME` and
  missing-auth cases produce the intended diagnostics without reading or
  printing credential contents.
- Public-surface scans pass without real consumer names, private paths,
  tokens, runtime logs or machine-local auth state in tracked files.

## Change Set
- `document-consumer-codex-auth-setup`
- `bootstrap-opt-in-auth-link`
- `verify-project-delivery-readiness-advisory`
- `runner-auth-remediation-diagnostics`
- `consumer-auth-setup-smoke-coverage`

## Verify
- `./bin/openspec validate "document-consumer-codex-auth-setup" --strict` - passed.
- `./bin/openspec validate "bootstrap-opt-in-auth-link" --strict` - passed.
- `./bin/openspec validate "verify-project-delivery-readiness-advisory" --strict` - passed.
- `./bin/openspec validate "runner-auth-remediation-diagnostics" --strict` - passed.
- `./bin/openspec validate "consumer-auth-setup-smoke-coverage" --strict` - passed.
- `python3 scripts/smoke-bootstrap-project.py` - passed with 8/8 checks.
- `python3 scripts/smoke-verify-project.py` - passed with 11/11 checks.
- `python3 scripts/smoke-delivery-runner.py` - passed.
- `python3 -m py_compile bin/bootstrap-project bin/verify-project bin/changerail-delivery-runner scripts/smoke-bootstrap-project.py scripts/smoke-verify-project.py scripts/smoke-delivery-runner.py` - passed through focused py_compile runs.
- `python3 scripts/public-surface-scan.py` - passed with 517 files scanned and 0 findings.
- `python3 scripts/run-release-baseline.py` - passed with 25/25 steps on rerun after one transient `smoke-openspec-archive-diagnostics.py` timeout; standalone smoke passed before rerun.
- `./bin/openspec validate --all --strict` - passed after archive with 13 specs.
- `git diff --check` - passed.
- Review cycle 1 returned `NO-GO` for blocker `R1`: supported auth marker
  `.codex/auth.toml` was not rejected when force-tracked.
- R1 rescue changed `bin/verify-project`, `templates/project/gitignore.tpl`,
  consumer docs, synced specs and `scripts/smoke-verify-project.py` so
  `.codex/auth.toml` is ignored, forbidden when tracked and covered by smoke.
- R1 rescue verification:
  `python3 scripts/smoke-verify-project.py` - passed with 12/12 checks;
  `python3 scripts/smoke-bootstrap-project.py` - passed with 8/8 checks;
  `python3 scripts/smoke-delivery-runner.py` - passed;
  `python3 -m py_compile bin/verify-project scripts/smoke-verify-project.py` - passed;
  `./bin/openspec validate --all --strict` - passed with 13 specs;
  `python3 scripts/public-surface-scan.py` - passed with 517 files scanned and 0 findings;
  `python3 scripts/run-release-baseline.py` - passed with 25/25 steps;
  `git diff --check` - passed.

## Archive
- `openspec/changes/archive/2026-07-24-document-consumer-codex-auth-setup/`
- `openspec/changes/archive/2026-07-24-bootstrap-opt-in-auth-link/`
- `openspec/changes/archive/2026-07-24-verify-project-delivery-readiness-advisory/`
- `openspec/changes/archive/2026-07-24-runner-auth-remediation-diagnostics/`
- `openspec/changes/archive/2026-07-24-consumer-auth-setup-smoke-coverage/`

## Related
- `docs/how-it-works.md`
- `docs/changerail-contracts.md`
- `docs/consumer-adoption-runbook.md`
- `docs/compatibility.md`
- `bin/bootstrap-project`
- `bin/verify-project`
- `bin/changerail-delivery-runner`
- `scripts/smoke-bootstrap-project.py`
- `scripts/smoke-verify-project.py`
- `scripts/smoke-delivery-runner.py`
- `templates/project/gitignore.tpl`
- `openspec/specs/changerail-project-bootstrap/spec.md`
- `openspec/specs/changerail-project-verification/spec.md`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-release-ci/spec.md`
- `openspec/changes/archive/2026-07-24-document-consumer-codex-auth-setup/`
- `openspec/changes/archive/2026-07-24-bootstrap-opt-in-auth-link/`
- `openspec/changes/archive/2026-07-24-verify-project-delivery-readiness-advisory/`
- `openspec/changes/archive/2026-07-24-runner-auth-remediation-diagnostics/`
- `openspec/changes/archive/2026-07-24-consumer-auth-setup-smoke-coverage/`

## Result
planned changes implemented, verified, specs synced and archived; consumer docs
now describe Codex auth setup, bootstrap supports explicit auth symlink setup,
`verify-project` emits non-fatal delivery auth readiness advisories, runner
preflight diagnostics point to remediation and focused smoke/release baseline
cover the auth setup contract; review cycle 1 blocker `R1` was fixed and
verified, making the previous `NO-GO` verdict stale and requiring fresh
re-review

Published reviewed payload as `d4cb2565f0d4d856e0d0e6ff4e8ce0bd759d8927`; push status `pending` on `main`/`origin`.

## Next
- done

## Change 1: `document-consumer-codex-auth-setup`

### Why
Operators should not discover the auth requirement only after a queue
`preflight-plan` fails.

### Goal
Update consumer adoption and delivery runner docs with a concise, public-safe
setup section and remediation examples.

### Acceptance
- Docs explain effective `CODEX_HOME`, accepted auth marker/env forms and why
  auth must stay ignored.
- Examples use `/opt/example-project` and `$HOME`, not real consumer paths.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-24-document-consumer-codex-auth-setup/`

## Change 2: `bootstrap-opt-in-auth-link`

### Why
The common local fix is safe when explicit, but should not happen silently.

### Goal
Add an optional bootstrap mode or documented post-bootstrap command to create
an ignored symlink from project `.codex/auth.json` to a user-selected auth
source.

### Acceptance
- Default bootstrap still does not copy credentials.
- Opt-in path refuses missing auth source and does not print credential
  contents.

### Depends On
- `document-consumer-codex-auth-setup`

### Related
- `openspec/changes/archive/2026-07-24-bootstrap-opt-in-auth-link/`

## Change 3: `verify-project-delivery-readiness-advisory`

### Why
`verify-project` can be green for wiring while delivery automation is not ready.

### Goal
Add a non-fatal advisory or explicit optional check that reports whether the
consumer has runner auth readiness, without making auth mandatory for all
consumer projects.

### Acceptance
- Public CI/template smoke can still pass without local auth.
- Operators get a clear next command when delivery runner auth is absent.

### Depends On
- `document-consumer-codex-auth-setup`

### Related
- `openspec/changes/archive/2026-07-24-verify-project-delivery-readiness-advisory/`

## Change 4: `runner-auth-remediation-diagnostics`

### Why
Preflight already catches missing auth, but the diagnostic should point to the
new canonical fix.

### Goal
Improve preflight output or docs-linked messaging for `CODEX auth: fail` and
stale auth symlink cases.

### Acceptance
- Missing auth remains `BLOCKED`.
- Diagnostics do not reveal token paths beyond generic/sanitized marker paths
  already safe to show.

### Depends On
- `document-consumer-codex-auth-setup`

### Related
- `openspec/changes/archive/2026-07-24-runner-auth-remediation-diagnostics/`

## Change 5: `consumer-auth-setup-smoke-coverage`

### Why
This is an install-time contract, so regressions should be caught in generic
smoke tests.

### Goal
Extend bootstrap, verify-project or delivery-runner smoke coverage for symlink
auth marker, explicit `CODEX_HOME` and missing-auth cases.

### Acceptance
- Existing release baseline stays green.
- Tests never read, embed or print real credential file contents.

### Depends On
- `bootstrap-opt-in-auth-link`
- `verify-project-delivery-readiness-advisory`
- `runner-auth-remediation-diagnostics`

### Related
- `openspec/changes/archive/2026-07-24-consumer-auth-setup-smoke-coverage/`

## Log
- 2026-07-23T18:48:25Z card created from consumer delivery-plan setup feedback.
- 2026-07-24T00:00:00Z fast-forward planning created five apply-ready
  OpenSpec changes.
- 2026-07-24T12:57:22Z delivery implemented all five changes, synced specs,
  archived OpenSpec changes and left the review-gated card in `3.inprogress`.
- 2026-07-25T05:38:42Z review cycle 1 returned `NO-GO` for tracked
  `.codex/auth.toml` not being forbidden; scoped R1 rescue fixed verifier
  policy, generated ignore policy, docs/specs and smoke coverage, then passed
  full release baseline.
- 2026-07-25T05:51:41Z publish finalized card into `4.done` with commit `d4cb2565f0d4d856e0d0e6ff4e8ce0bd759d8927` and push status `pending`.
