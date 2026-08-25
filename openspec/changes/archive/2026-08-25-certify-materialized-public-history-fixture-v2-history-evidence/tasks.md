## 1. Tracked Evidence Policy

- [x] 1.1 Add the `changerail-release-ci` one-shot certification requirement and
  align the board/OpenSpec policy with exact capture id, 1200-second timeout,
  output oracle, terminal no-retry rule and one-way source continuation.
- [x] 1.2 Pin the full source review fingerprint, fixture fingerprint,
  authority digest and seven authority-path hashes; retain the old
  `public-history-final` 300-second empty-output timeout as separate non-PASS
  evidence.
- [x] 1.3 Confirm scoped changes are only board/OpenSpec/main-spec
  documentation and ignored evidence/manifest state, with zero added
  production/test/runtime LOC and no source-card or authority-path edit.

## 2. Pre-Capture Finalization

- [x] 2.1 Finalize the tracked policy before capture, sync/archive the change,
  move the card to review-pending state and retain the exact policy fingerprint
  in the ignored delivery manifest without claiming prior review or publish.
- [x] 2.2 Prove the certification lineage has no existing
  `public-history-certification` attempt, prove the source fingerprint and all
  seven hashes equal their pins, and stop without executing if any precondition
  fails.
- [x] 2.3 Retain the fixed command, cwd identity, timeout, complete JSON oracle,
  exit/findings rules and before/after hash procedure before execution; after
  command start, permit no outcome-dependent policy edit or replacement id.

## 3. Terminal Certification Capture

- [x] 3.1 After tracked policy finalization only, execute exactly one retained
  `public-history-certification` capture of
  `python3 scripts/public-surface-scan.py --history --json` in the exact source
  worktree with timeout `1200`, then record post-capture source and seven-path
  hashes without editing or copying source files.
- [x] 3.2 Validate the `changerail.evidence-index.v1` entry and ignored manifest:
  PASS requires exit 0, no timeout, one complete
  `changerail.public-surface-scan.v1` report, `history: true`, status `pass`,
  zero findings and unchanged pre/post identities; otherwise retain terminal
  FAIL/TIMEOUT and stop without retry, repair, review or publish.

## 4. Documentation Verification And Handoff

- [x] 4.1 Run `bin/openspec validate
  certify-materialized-public-history-fixture-v2-history-evidence --strict` and
  `bin/openspec validate --all --strict` before archive, then strict all again
  after sync/archive.
- [x] 4.2 Run `python3 -m json.tool .mcp.json`, parse
  `.codex/config.toml` with `tomllib`, and run current-only
  `python3 scripts/public-surface-scan.py` without `--history` for this docs
  payload.
- [x] 4.3 Run
  `bin/changerail-source-classification --workspace . --json check`, verify
  zero added production/test/runtime LOC, and cover tracked plus every untracked
  file with `git diff --check` and explicit no-index whitespace checks.
- [x] 4.4 Derive and scope-check the ignored delivery manifest, validate the
  retained evidence index and run normalized deterministic preflight on the
  final tracked fingerprint; do not run fixture materialization, candidate
  benchmark or full release baseline.
- [x] 4.5 On certification PASS only, hand off to one fresh independent
  critical Sol/`xhigh` final-certification review with milestone audit disabled;
  publish only after GO, then allow exactly one fresh unchanged-source cycle-2
  Sol/`xhigh` review with no source scan/edit and no repair after NO-GO.
