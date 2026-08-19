## 1. Queue Recovery Contract

- [x] 1.1 Extend `schemas/changerail-delivery-plan-status.schema.json` with bounded retained recovery metadata for `investigation_required` sources.
- [x] 1.2 Represent recovery kind, source run status path, source terminal reason and retained-payload fingerprint summary without embedding raw child logs or raw source payload.
- [x] 1.3 Add schema coverage for valid retained recovery metadata and duplicate recovery rejection.

## 2. Queue Resume Behavior

- [x] 2.1 Teach `resume-plan` to classify prior child `terminal_reason: investigation_required` as recoverable only with schema-valid retained-payload identity.
- [x] 2.2 Launch original-card single-card `resume --status-path <prior-child-status>` when the plan fingerprint is unchanged and retained identity matches.
- [x] 2.3 Accept at most one same-workspace, same-wave `recovery_for` replacement card when the plan changes only by a valid recovery augmentation.
- [x] 2.4 Keep downstream cards blocked until the original retained payload or replacement recovery publishes successfully.

## 3. Verification

- [x] 3.1 Add focused `scripts/smoke-delivery-runner.py` queue coverage for successful retained recovery.
- [x] 3.2 Add adversarial queue smoke cases for dirty state, stale authorization, wrong card, wrong workspace, fingerprint drift and duplicate recovery path.
- [x] 3.3 Run `./bin/openspec validate support-investigation-required-queue-recovery --strict`.
- [x] 3.4 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 3.5 Run `git diff --check`.
- [x] 3.6 Run `python3 scripts/public-surface-scan.py`.
