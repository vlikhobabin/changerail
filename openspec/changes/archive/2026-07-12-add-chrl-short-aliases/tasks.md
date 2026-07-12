## 1. Alias Source Surface

- [x] 1.1 Add thin Codex alias skill directories `skills/chrl-explore`,
  `skills/chrl-ff`, `skills/chrl-do`, `skills/chrl-review`,
  `skills/chrl-pub` and `skills/chrl-deliver`.
- [x] 1.2 Add thin Claude alias wrappers under `claude/commands/chrl/` for
  `explore`, `ff`, `do`, `review`, `pub` and `deliver`.
- [x] 1.3 Add repo-local `.codex/skills/chrl-*` symlinks to the tracked alias
  skill directories.

## 2. Generated Consumer Wiring

- [x] 2.1 Update bootstrap/template wiring so new consumers receive both
  canonical `changerail-*` and short `chrl-*` Codex skills.
- [x] 2.2 Update bootstrap/template wiring so new consumers receive both
  `/changerail:*` and `/chrl:*` Claude command directories.
- [x] 2.3 Update `verify-project` to fail when required `chrl-*` Codex or
  `/chrl:*` Claude alias wiring is missing.

## 3. Smoke Coverage And Docs

- [x] 3.1 Update wiring discovery and generated-consumer smoke coverage to
  validate the short aliases.
- [x] 3.2 Update public docs and shared methodology to present `chrl-*` as the
  recommended daily shorthand while preserving `changerail-*` as canonical.
- [x] 3.3 Sync the delta specs into `openspec/specs/` before archiving.

## 4. Verification

- [x] 4.1 Run `./bin/openspec status --change add-chrl-short-aliases --json`
  and `./bin/openspec instructions apply --change add-chrl-short-aliases --json`.
- [x] 4.2 Run `./bin/openspec validate add-chrl-short-aliases --strict` and
  `./bin/openspec validate --all --strict`.
- [x] 4.3 Run `python3 -m json.tool .mcp.json`, the `.codex/config.toml`
  `tomllib` parse check from `AGENTS.md`, and `git diff --check`.
- [x] 4.4 Run focused smoke checks:
  `python3 scripts/smoke-verify-project.py`,
  `python3 scripts/smoke-wiring-discovery.py` and
  `python3 scripts/smoke-bootstrap-project.py`.
- [x] 4.5 Run a public-surface scan for private/local names relevant to the
  changed files and confirm ignored runtime artifacts stay untracked.
