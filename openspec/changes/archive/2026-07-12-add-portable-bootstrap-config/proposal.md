## Why

Bootstrap-generated consumer files are intended to be reviewed and committed,
but current templates render machine-local absolute paths such as the consumer
project root and ChangeRail checkout into tracked files.

## What Changes

- Make portable tracked config the default bootstrap output.
- Keep machine-local absolute values out of generated tracked docs/config unless
  the operator explicitly opts into local config mode.
- Teach `verify-project` to validate portable config scope.
- Add smoke coverage proving default generated files avoid private absolute
  paths while local mode warns before suggested staging.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-project-bootstrap`: bootstrap exposes a public-safe config mode
  and explicit local opt-in.
- `changerail-project-templates`: tracked templates avoid machine-local
  absolute paths by default.
- `changerail-project-verification`: verifier accepts and validates the
  portable config model.

## Impact

- `bin/bootstrap-project`
- `bin/verify-project`
- `templates/project/`
- `scripts/smoke-bootstrap-project.py`
- `scripts/smoke-verify-project.py`
- `docs/consumer-adoption-runbook.md`
