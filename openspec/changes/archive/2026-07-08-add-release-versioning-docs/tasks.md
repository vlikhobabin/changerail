## 1. Release Documentation

- [x] 1.1 Add root `VERSION` with the initial semver value.
- [x] 1.2 Add `CHANGELOG.md` with `Unreleased`, `0.1.0` and `BREAKING:`
  marker policy.
- [x] 1.3 Add `docs/release-discipline.md` describing semver and release
  checklist.
- [x] 1.4 Add `docs/compatibility.md` for Codex CLI, Claude Code and OpenSpec
  CLI.
- [x] 1.5 Add `docs/migration-guide.md` with initial migration notes.
- [x] 1.6 Update README and architecture docs to link the release docs.

## 2. Verification

- [x] 2.1 Run `openspec validate add-release-versioning-docs --strict`.
- [x] 2.2 Run `openspec validate --all --strict`.
- [x] 2.3 Run docs/config baseline checks from `AGENTS.md`.
- [x] 2.4 Run public-surface scan for private names/paths relevant to release
  docs.

## Evidence

- `openspec validate add-release-versioning-docs --strict` passed.
- `openspec validate --all --strict` passed with 11/11 items.
- `python3 -m json.tool .mcp.json` passed.
- TOML parse for `.codex/config.toml` passed and printed `TOML_OK`.
- `git diff --check` passed.
- `git status --short --ignored` showed only card-owned tracked/untracked
  changes plus ignored local runtime/cache paths.
- Public path scan found no non-generic `/opt` paths in release docs,
  artifacts or card.
