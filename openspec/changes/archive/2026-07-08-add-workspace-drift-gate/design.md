## Context

Phase 2 added `bin/verify-project`, which is the authoritative red/green gate
for one consumer project. Phase 3 needs a workspace-level smoke that can scan
configured roots, classify each discovered project, and return CI-friendly JSON
without committing machine-local inventory.

The new drift gate lives in OPSX core because it validates OPSX adoption state,
but it must not assume any private workspace layout. Operators provide
inventory through an explicit config path, normally under ignored `internal/`,
or through CLI flags during local/CI runs.

## Goals / Non-Goals

**Goals:**
- Add `scripts/smoke-drift.py` as a deterministic exit-code gate.
- Compose the existing `bin/verify-project` checks for candidate OPSX projects.
- Produce a JSON report with schema `opsx.drift-gate.v1`.
- Classify projects as `opsx_source`, `legacy_source`, `broken_wiring`,
  `disconnected` or `explicitly_excluded`.
- Support include/exclude inventory without tracking real project names or
  machine-local workspace paths.

**Non-Goals:**
- Do not migrate projects or rewrite symlink-и.
- Do not discover the whole filesystem implicitly.
- Do not commit inventory, runtime reports or local migration context.
- Do not replace `bin/verify-project`; drift remains a workspace-level wrapper
  around that per-project gate.

## Decisions

- **Inventory source:** The script accepts `--config`, repeated
  `--workspace-root`, repeated `--project` and repeated `--exclude`. The config
  format is JSON so CI can generate it without a Python dependency. Supported
  keys are `workspace_roots`, `projects`, `exclude` and `legacy_roots`.
- **Root scanning:** A configured workspace root contributes its immediate
  child directories. This keeps runtime predictable and avoids accidental deep
  traversal through unrelated repositories, caches or dependency trees.
- **Explicit projects:** `projects` entries are always included in addition to
  root children. This lets CI check a precise project set even when workspace
  roots are too broad.
- **Exclude handling:** Excludes are matched by resolved path. An excluded
  project is reported as `explicitly_excluded`, includes the operator-provided
  reason when present, and does not run `verify-project`.
- **OPSX classification:** For non-excluded directories, the gate runs
  `bin/verify-project <project> --opsx-root <opsx-root> --json`. A zero exit
  classifies as `opsx_source`.
- **Legacy classification:** If verification fails but configured symlink-и
  resolve under one of `legacy_roots`, the project is `legacy_source`. This is a
  red result because it still requires migration.
- **Broken versus disconnected:** If verification fails and OPSX-like files are
  present (`AGENTS.md`, `openspec/`, `.claude/`, `.codex/` or `bin/openspec`),
  the project is `broken_wiring`; otherwise it is `disconnected`.
- **Exit code:** The command exits `0` only when every classified entry is
  `opsx_source` or `explicitly_excluded`. Any legacy, broken, disconnected or
  config/read error returns non-zero.
- **Report location:** By default reports are written under
  `.runtime/opsx/drift-smoke/<run-id>/report.json`. Operators may pass
  `--report` for CI. Runtime reports are ignored state and may contain local
  project paths; tracked docs/specs only use generic examples.

## Risks / Trade-offs

- Broad workspace roots can include unrelated directories -> limit scanning to
  immediate children and support explicit `projects` for precise CI runs.
- `verify-project` can be expensive across many projects -> run it once per
  non-excluded candidate and include summaries in the report instead of raw
  full logs.
- Legacy source detection depends on configured `legacy_roots` -> keep
  `legacy_source` explicit and classify other OPSX-like failures as
  `broken_wiring`.
- Runtime reports include local paths by design -> keep the default location
  under ignored `.runtime` and require inventory config outside tracked files.

## Migration Plan

1. Add `scripts/smoke-drift.py`.
2. Add smoke fixtures under ignored `.runtime` during verification.
3. Run the script against generic fixture projects and record the ignored
   report path in the card.
4. Sync `opsx-drift-gate` into main specs and archive the change.
5. Future migration cards can create real `internal/` inventory and act on the
   report classes.

## Open Questions

- Whether future CI should allow `legacy_source` as warning-only during staged
  migration windows. The initial gate fails closed.
