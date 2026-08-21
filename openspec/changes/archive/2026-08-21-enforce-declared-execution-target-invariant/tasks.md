## 1. Declaration contracts

- [x] 1.1 Add RED schema fixtures for valid declaration, unknown fields,
  endpoint/credential fields, unsafe symlink, bounded values and absent legacy
  declaration.
- [x] 1.2 Add `changerail.execution-target.v1` and optional target identity
  references to manifest, delivery-run, plan-status and evidence contracts.
- [x] 1.3 Add the public-safe optional project template/example and schema
  inventory wiring without platform-specific defaults.

## 2. Shared loading and project verification

- [x] 2.1 Implement one shared declaration loader/projection that rejects
  unsafe paths, schema errors and content-bearing fields without executing
  project/provider commands.
- [x] 2.2 Wire `verify-project` to the shared loader and add RED/GREEN fixtures
  for valid, absent, invalid and unsafe declarations.
- [x] 2.3 Reuse the projection in delivery manifest derivation and fingerprint
  target identity without storing physical endpoint or credentials.

## 3. Delivery and review enforcement

- [x] 3.1 Capture target identity at single-card/plan attempt start and retain
  it in status, blocker and recovery lineage using existing fingerprint paths.
- [x] 3.2 Fail closed before child launch, review or publish on missing,
  multiple, mismatched or drifted target identity and preserve compatibility
  when declaration is absent.
- [x] 3.3 Require exact retained identity for external/investigation resume and
  prove changed declaration requires a new clean attempt.
- [x] 3.4 Extend deterministic review preflight to compare current declaration,
  manifest and applicable evidence identity without reading raw proof contents.
- [x] 3.5 Add adversarial runner/review fixtures for substitution, target drift,
  multiple evidence targets, blocker resume and explicit clean rebind.

## 4. Methodology and verification

- [x] 4.1 Update canonical lifecycle skills, shared methodology and operator
  docs to prohibit provision/rebind/substitution as blocker recovery.
- [x] 4.2 Run contract, manifest, verify-project, runner and review-preflight
  smoke suites and record concise green evidence.
- [x] 4.3 Run `bin/openspec validate --all --strict`, `git diff --check` and
  `python3 scripts/public-surface-scan.py`.
- [x] 4.4 Run deterministic review preflight/fingerprint evidence and prove the
  exact payload adds no more than 500 production-counted LOC; otherwise stop
  and split before independent review.
