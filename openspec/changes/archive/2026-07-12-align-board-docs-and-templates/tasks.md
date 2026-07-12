## 1. Docs And Templates

- [x] 1.1 Update root board README to remove stale minimal-surface wording.
- [x] 1.2 Update consumer board README template with lifecycle and guide
  pointers.
- [x] 1.3 Keep examples generic and public-safe.

## 2. Verification

- [x] 2.1 Run `./bin/openspec validate "align-board-docs-and-templates" --strict`.
- [x] 2.2 Run `./bin/openspec validate --all --strict`.
- [x] 2.3 Run `git diff --check`.
- [x] 2.4 Run targeted public-surface scan for touched docs/templates.

## Verification Notes

- `./bin/openspec validate align-board-docs-and-templates --strict` passed.
- `./bin/openspec validate --all --strict` passed with 17 items.
- `git diff --check` passed.
- Targeted scan for private `/opt/*` paths returned no matches; reviewed
  pre-existing `opsx` hits are historical rename references.
