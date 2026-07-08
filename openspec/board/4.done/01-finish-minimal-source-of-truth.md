# Завершить минимальный source of truth (Фаза 1)

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived

## Source
- OPSX roadmap, раздел 12, Фаза 1 (`docs/opsx-source-of-truth-architecture.md`).
- Path-neutrality и контрактный namespace (раздел 7).

## Summary
Довести Фазу 1 до состояния, когда OPSX может быть полноценным источником
symlink-ов: перенести оставшиеся generic lifecycle skills, `openspec-*` skills,
wrapper `bin/openspec`, review-verdict helper и контрактные `schemas/` в
namespace `opsx.*`. Каждый переносимый skill должен быть path-neutral и без
упоминаний workspace-specific источников.

## Acceptance
- `skills/opsx-do`, `skills/opsx-review`, `skills/opsx-pub`, `skills/opsx-deliver`
  существуют, path-neutral, описывают generic lifecycle без domain-specific
  provider/trace политики.
- `openspec-*` lifecycle skills присутствуют; зафиксированы источник, лицензия и
  политика синка с развитием OpenSpec CLI.
- `bin/openspec` wrapper присутствует, pin версии CLI + compatibility notes.
- `schemas/` содержит review-verdict, delivery-manifest и evidence-index в
  namespace `opsx.*`; validate/fingerprint helper-ы достижимы.
- review-verdict helper присутствует и генерирует контрактный verdict.
- Все перенесенные skills path-neutral (нет machine-specific fallback-путей и
  workspace-specific имен); контрактные id используют только `opsx.*`.
- OpenSpec validation и public-surface scans проходят.

## Change Set
- `add-generic-opsx-lifecycle-surface`
- `add-openspec-lifecycle-surface`
- `add-opsx-contract-schemas-and-helper`

## Verify
- passed: `openspec validate add-generic-opsx-lifecycle-surface --strict`
- passed: `openspec validate add-openspec-lifecycle-surface --strict`
- passed: `openspec validate add-opsx-contract-schemas-and-helper --strict`
- passed: `openspec validate opsx-skill-surface --strict`
- passed: `openspec validate opsx-wiring-discovery --strict`
- passed: `openspec validate opsx-openspec-lifecycle --strict`
- passed: `openspec validate opsx-contracts --strict`
- passed: `openspec validate --all --strict`
- passed: `python3 scripts/smoke-wiring-discovery.py` -> 118/118 checks,
  report `.runtime/opsx/wiring-smoke/20260708T144032Z-e2eac078/report.json`
- passed: `/opt/opsx/bin/openspec --version` -> `1.3.0`
- passed: `python3 -m json.tool .mcp.json` and all
  `schemas/opsx-*.schema.json`
- passed: `.codex/config.toml` parsed with Python `tomllib`
- passed: `python3 scripts/opsx_review_verdict.py fingerprint --workspace .`
- passed: canonical runtime verdict sample validated with
  `python3 scripts/opsx_review_verdict.py validate --check-fresh --json`
- passed: targeted public-path scan for private/machine-local paths
- passed: `git diff --check`
- passed: text whitespace scan over modified and untracked files
- passed: `python3 -m json.tool .runtime/opsx/delivery-manifests/01-finish-minimal-source-of-truth.json`
- passed: R1 fix `openspec validate --all --strict` -> 5 passed, 0 failed
- passed: R1 fix `python3 scripts/smoke-wiring-discovery.py` -> 118/118
  checks, report `.runtime/opsx/wiring-smoke/20260708T152430Z-3f367874/report.json`
- passed: R1 fix private namespace scans with `rg` and `git grep` returned no
  matches

## Archive
- `openspec/changes/archive/2026-07-08-add-generic-opsx-lifecycle-surface/`
- `openspec/changes/archive/2026-07-08-add-openspec-lifecycle-surface/`
- `openspec/changes/archive/2026-07-08-add-opsx-contract-schemas-and-helper/`

## Related
- `docs/opsx-source-of-truth-architecture.md`
- `AGENTS.shared.md`
- `skills/opsx-explore/SKILL.md`
- `skills/opsx-ff/SKILL.md`
- `docs/wiring-discovery.md`
- `docs/openspec-lifecycle.md`
- `docs/opsx-contracts.md`
- `openspec/changes/archive/2026-07-08-add-generic-opsx-lifecycle-surface/`
- `openspec/changes/archive/2026-07-08-add-openspec-lifecycle-surface/`
- `openspec/changes/archive/2026-07-08-add-opsx-contract-schemas-and-helper/`
- `openspec/specs/opsx-skill-surface/spec.md`
- `openspec/specs/opsx-wiring-discovery/spec.md`
- `openspec/specs/opsx-openspec-lifecycle/spec.md`
- `openspec/specs/opsx-contracts/spec.md`

## Result
Implemented and archived all planned changes for the minimal source-of-truth
surface. External review cycle 2 returned a fresh `go` verdict, and publish
proceeds with ignored runtime artifacts excluded.

## Next
- Track verdict freshness hardening for untracked-file content as a follow-up
  outside this card if prioritized.

## Change 1: `add-generic-opsx-lifecycle-surface`

### Why
OPSX has planning skills, but not the generic delivery, review, publish and
deliver phases required for the full lifecycle.

### Goal
Add path-neutral OPSX lifecycle skills and Claude wrappers for `do`, `review`,
`pub` and `deliver`.

### Scope
- Add `skills/opsx-do/`, `skills/opsx-review/`, `skills/opsx-pub/` and
  `skills/opsx-deliver/`.
- Add Claude wrappers for `/opsx:do`, `/opsx:review`, `/opsx:pub` and
  `/opsx:deliver`.
- Update public docs and the `opsx-skill-surface` spec.
- Exclude domain-specific provider, trace and verification policy from the
  generic OPSX core.

### Acceptance
- Lifecycle skills are present and path-neutral.
- Claude wrappers load matching skills through skill discovery.
- Review and publish keep fail-closed review-gate semantics.

### Depends On
- `add-minimal-opsx-skills`

### Related
- `openspec/changes/archive/2026-07-08-add-generic-opsx-lifecycle-surface/`

## Change 2: `add-openspec-lifecycle-surface`

### Why
OPSX delivery skills depend on OpenSpec action skills and a stable OpenSpec CLI
route, but those are not yet part of the OPSX source surface.

### Goal
Add `openspec-*` lifecycle skills, a pinned `bin/openspec` wrapper and
compatibility/sync-policy documentation.

### Scope
- Add tracked `skills/openspec-*` lifecycle skill directories.
- Add `bin/openspec` pinned to OpenSpec CLI `1.3.0`.
- Document OpenSpec skill provenance, MIT license and sync policy.
- Update wiring docs for `openspec-*` skills and `bin/openspec`.

### Acceptance
- OpenSpec lifecycle skills are present with provenance metadata.
- `bin/openspec` executes the pinned CLI and supports `OPENSPEC_VERSION`.
- Compatibility notes describe how the skill source is synced.

### Depends On
- `add-generic-opsx-lifecycle-surface`

### Related
- `openspec/changes/archive/2026-07-08-add-openspec-lifecycle-surface/`

## Change 3: `add-opsx-contract-schemas-and-helper`

### Why
Review and publish gates need canonical OPSX wire contracts and a helper that
can validate review verdicts and freshness fingerprints.

### Goal
Add `opsx.*` schemas for review verdict, delivery manifest and evidence index,
plus the review-verdict helper and wrapper.

### Scope
- Add `schemas/opsx-review-verdict.schema.json`,
  `schemas/opsx-delivery-manifest.schema.json` and
  `schemas/opsx-evidence-index.schema.json`.
- Add `scripts/opsx_review_verdict.py` and `bin/opsx-review-verdict`.
- Document canonical `opsx.*` ids and helper usage.

### Acceptance
- Schemas use canonical `opsx.*` ids.
- Helper can compute fingerprints and validate canonical verdict samples.
- Runtime verdicts/manifests remain ignored state.

### Depends On
- `add-generic-opsx-lifecycle-surface`

### Related
- `openspec/changes/archive/2026-07-08-add-opsx-contract-schemas-and-helper/`

## Log
- 2026-07-08T14:05:27Z card created from roadmap phase 1 remaining scope.
- 2026-07-08T14:20:00Z card decomposed into three apply-ready OpenSpec changes
  and moved to `3.inprogress`.
- 2026-07-08T14:40:32Z implementation verification passed; wiring smoke
  recorded 118/118 passing checks.
- 2026-07-08T14:45:00Z all three changes archived with specs synced manually
  before archive (`--skip-specs` used to avoid duplicate spec application).
- 2026-07-08T14:46:00Z safety stop: awaiting external review per supervisor
  instruction; no self-review, reviewer launch, publish, commit or push was
  performed.
- 2026-07-08T15:24:50Z external review returned no-go R1; removed
  non-canonical verdict schema acceptance and stopped for external re-review;
  no self-review, publish, commit or push was performed.
- 2026-07-08T15:28:28Z external review cycle 2 returned `go`; verdict
  validated fresh against HEAD `1ae67d93c27140707db5217cf26789f083d608b0`
  with fingerprint
  `sha256:75bec50e2282bed282f38d3570e9a722d937ab91efd5e0c28fd67c665155590f`.
- 2026-07-08T15:31:28Z card moved to `4.done` for scoped publish; runtime
  review verdict and delivery evidence remain excluded from commit.
