## 1. Schemas And Policy

- [x] 1.1 Add maintenance scan report and detector-result JSON Schemas with canonical schema ids.
- [x] 1.2 Extend the maintenance policy schema with optional scan configuration while keeping the minimal policy valid.
- [x] 1.3 Extend contract schema smoke coverage for the new schemas and invalid unknown-field cases.

## 2. Core Scan Implementation

- [x] 2.1 Add `scan` CLI argument parsing, JSON output and exit-code handling to `scripts/changerail_maintenance.py`.
- [x] 2.2 Implement read-only scan report construction and detector result helpers in `scripts/changerail_repository_knowledge.py`.
- [x] 2.3 Implement configured documentation universe coverage and orphan/missing-target detection.
- [x] 2.4 Implement Markdown local link/anchor validation with duplicate heading and encoded-fragment cases.
- [x] 2.5 Implement generated freshness and forbidden active-reference detectors without running arbitrary generator commands.

## 3. Fixtures And Docs

- [x] 3.1 Add focused repository fixtures for link drift, stale index, orphan record and forbidden active reference.
- [x] 3.2 Document scan policy, report schema ids, detectors and exit behavior in `docs/changerail-contracts.md`.

## 4. Verification

- [x] 4.1 Run focused repository knowledge smoke with scan fixtures.
- [x] 4.2 Run `python3 scripts/smoke-contract-schemas.py`.
- [x] 4.3 Run `bin/changerail-maintenance validate-catalog`.
- [x] 4.4 Run `bin/changerail-maintenance render-index --check`.
- [x] 4.5 Run `bin/changerail-maintenance scan --json`.
- [x] 4.6 Run `./bin/openspec validate add-deterministic-knowledge-integrity-scan --strict`.
- [x] 4.7 Run `./bin/openspec validate --all --strict`.
- [x] 4.8 Run `python3 scripts/public-surface-scan.py`.
- [x] 4.9 Run `git diff --check`.
