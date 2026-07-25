# Design: consumer auth setup smoke coverage

## Context

The auth setup contract spans documentation, bootstrap, verification and runner
preflight. Existing smoke already covers runner auth pass/fail and stale
symlink behavior, but it does not cover the new bootstrap opt-in and verify
advisory surfaces as one release-facing regression boundary.

## Goals / Non-Goals

**Goals:**
- Ensure release baseline runs focused smoke for bootstrap auth link,
  verification advisory and runner auth diagnostics.
- Use only fake temporary credential files under `.runtime` or temporary test
  directories.
- Assert that tests never print credential contents.

**Non-Goals:**
- Do not require live Codex authentication or network auth validation.
- Do not store raw runtime logs in tracked files.

## Decisions

- Extend existing smoke scripts instead of adding a new top-level smoke command.
  Release baseline already invokes bootstrap, verify and delivery runner smoke.
- Add release-ci smoke assertions only if required command inventory changes;
  otherwise the existing inventory remains the release contract.
- Use sentinel fake contents in temporary auth files and assert the sentinel is
  absent from stdout/status payloads.

## Risks / Trade-offs

- [Risk] Smoke tests become brittle if they assert full diagnostic prose.
  → Mitigation: assert stable tokens such as `CODEX auth`, `CODEX_HOME` and
  `docs/consumer-adoption-runbook.md#codex-auth-for-delivery-runner`.
