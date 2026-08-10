## 1. Existing-Project Configure Mode

- [x] 1.1 Add an allowlisted preflight/plan model for existing-project auth and
  wiring actions without template rendering.
- [x] 1.2 Implement idempotent auth-link and lock-owned POSIX repair actions with
  ownership, scope and dirty-state gates.
- [x] 1.3 Reject configure/bootstrap flag mixing before mutation and preserve
  project-owned content on every failure path.

## 2. README And Git Handoff

- [x] 2.1 Convert the minimal README source into an explicit opt-in generated
  template with refuse-on-existing behavior.
- [x] 2.2 Add local `git init`, default branch and remote options with preflight,
  bounded rollback and no add/commit/push behavior.
- [x] 2.3 Make completion output distinguish initialization from operator-owned
  commit/publication actions.

## 3. Diagnostics And Regression Evidence

- [x] 3.1 Update missing-auth advisory to use the real ChangeRail runbook and a
  generic executable configure command without local auth paths.
- [x] 3.2 Add idempotency, real-file conflict, unrelated dirty state, credential
  redaction, README conflict and Git no-publish fixtures.
- [x] 3.3 Record regression evidence showing current post-bootstrap auth/README/Git
  gaps before implementation, then observe the new paths pass.

## 4. Docs And Verification

- [x] 4.1 Update consumer adoption, migration, wiring and bootstrap guidance.
- [x] 4.2 Run `python3 scripts/smoke-bootstrap-project.py` and
  `python3 scripts/smoke-verify-project.py` and observe all checks pass.
- [x] 4.3 Run `./bin/openspec validate --all --strict`, current/history
  public-surface scans and `git diff --check`.
