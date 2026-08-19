## 1. Resume Validation

- [ ] 1.1 Extend single-card `resume` prior-status validation to recognize `terminal_reason: investigation_required`.
- [ ] 1.2 Validate prior status schema, source run id, source status path, card path/id, workspace root and retained-payload identity before launching any continuation.
- [ ] 1.3 Compare current `HEAD`, reviewed tree SHA and diff fingerprint against retained identity and fail closed on payload drift.

## 2. Authorization And Continuation

- [ ] 2.1 Verify published investigation and authorization cards are tracked under `openspec/board/4.done/` and clean at `HEAD`.
- [ ] 2.2 Reuse the published investigation authorization relation checks and ceiling/protocol allowance for retained-payload resume.
- [ ] 2.3 Continue at the review/publish boundary for the retained working-tree payload without re-running implementation.
- [ ] 2.4 Reject WIP commits, stash names, branch names and prose assertions as retained-payload proof.

## 3. Verification

- [ ] 3.1 Add focused `scripts/smoke-delivery-runner.py` coverage for successful retained-payload single-card resume.
- [ ] 3.2 Add adversarial smoke cases for wrong card, wrong workspace, stale authorization, relation mismatch, over-ceiling authorization and fingerprint drift.
- [ ] 3.3 Run `./bin/openspec validate resume-investigation-required-single-card --strict`.
- [ ] 3.4 Run `python3 scripts/smoke-delivery-runner.py`.
- [ ] 3.5 Run `git diff --check`.
- [ ] 3.6 Run `python3 scripts/public-surface-scan.py`.
