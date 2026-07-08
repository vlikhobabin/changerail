## 1. Planning Artifacts

- [x] 1.1 Add board card for wiring/discovery smoke planning.
- [x] 1.2 Add change metadata, proposal and design.
- [x] 1.3 Add `opsx-wiring-discovery` spec delta.

## 2. Implementation Plan

- [x] 2.1 Decide repo-local dogfooding wiring shape.
- [x] 2.2 Define consumer wiring smoke evidence format.
- [x] 2.3 Identify docs/scripts to implement in the delivery pass.
- [x] 2.4 Confirm public-surface scan patterns for wiring artifacts.

## 3. Implementation

- [x] 3.1 Add `docs/wiring-discovery.md`.
- [x] 3.2 Add `scripts/smoke-wiring-discovery.py`.
- [x] 3.3 Add repo-local relative symlink-и for Claude and Codex discovery.
- [x] 3.4 Generate ignored aggregate smoke report under `.runtime/`.
- [x] 3.5 Align OpenSpec/card lifecycle after implementation review.

## 4. Verification

- [x] 4.1 Run wiring smoke for repo-local and consumer-example surfaces.
- [x] 4.2 Run `openspec validate --all --strict`.
- [x] 4.3 Run `.mcp.json` and `.codex/config.toml` parsing checks.
- [x] 4.4 Run `git diff --check`.
- [x] 4.5 Run whitespace scan over changed and untracked text files.
- [x] 4.6 Run public-surface scan for private paths and workspace names.
