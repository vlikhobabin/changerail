## 1. Documentation

- [x] 1.1 Update runner and adoption docs to explain the queue launcher chain.
- [x] 1.2 Clarify effective `CODEX_WORKDIR` and `CODEX_HOME` resolution for
      plan children.
- [x] 1.3 Remove or qualify wording that implies every consumer needs a tracked
      repo-local `bin/codex`.

## 2. Verification

- [x] 2.1 Add or update smoke/docs checks for the expected launcher wording.
- [x] 2.2 Run `./bin/openspec validate document-queue-launcher-semantics --strict`.
- [x] 2.3 Run `./bin/openspec validate --all --strict`.
- [x] 2.4 Run `git diff --check`.
