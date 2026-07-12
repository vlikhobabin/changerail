# add-bootstrap-workflow-guidance-smoke

## Why

The previous review manually rendered a temporary project to confirm that
generated `AGENTS.md` and board README included current workflow guidance.
That should be stable smoke coverage.

## What Changes

- Extend bootstrap smoke to check generated workflow guidance.
- Verify generated `AGENTS.md` and `openspec/board/README.md` contain lifecycle,
  role model, fresh review gate and board finalization guidance.

## Impact

- Affects bootstrap smoke and generated-template verification.
- Updates `changerail-project-bootstrap`, `changerail-project-templates` and
  `changerail-release-ci` specifications.
