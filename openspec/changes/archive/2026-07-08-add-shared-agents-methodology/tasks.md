## 1. Dogfooding Skeleton

- [x] 1.1 Добавить `openspec/config.yaml` с OPSX-specific public rules.
- [x] 1.2 Добавить `openspec/board/` columns, board README и card template.
- [x] 1.3 Добавить первую `3.inprogress` board card для shared methodology.

## 2. Change Artifacts

- [x] 2.1 Добавить metadata и README для change `add-shared-agents-methodology`.
- [x] 2.2 Добавить proposal, design и spec delta для `opsx-agent-methodology`.
- [x] 2.3 Реализовать `AGENTS.shared.md`.
- [x] 2.4 Обновить root `AGENTS.md`, чтобы уточнить split между repo-specific и shared methodology.

## 3. Verification

- [x] 3.1 Выполнить `openspec validate --all --strict`.
- [x] 3.2 Выполнить parsing checks для `.mcp.json` и `.codex/config.toml`.
- [x] 3.3 Выполнить whitespace check, покрывающий tracked и untracked files.
- [x] 3.4 Выполнить `git status --short --ignored`.
- [x] 3.5 Выполнить public-surface scan для private names и machine-local paths, релевантных этому workspace.
