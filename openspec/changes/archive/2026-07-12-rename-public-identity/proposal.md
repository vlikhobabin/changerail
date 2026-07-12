## Why

OPSX collides with OpenSpec-related `opsx` terminology and makes installation
guidance ambiguous for users who need to understand both OpenSpec and this
workflow layer. Renaming the product to ChangeRail separates the workflow
toolchain from the OpenSpec artifact system it uses.

## What Changes

- **BREAKING**: Rename the public product identity from OPSX to ChangeRail.
- **BREAKING**: Change the documented source-of-truth path from `/opt/opsx` to
  `/opt/changerail`.
- Update durable public docs, root repository instructions and release notes to
  use `ChangeRail`, `changerail` and `/opt/changerail`.
- Preserve only explicit migration/history mentions of OPSX so consumers can
  understand the rename.
- Document the GitHub repository rename and local `origin` update as an
  operator step after the code/docs rename lands.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-agent-methodology`: rename the reusable methodology and generic examples
  to ChangeRail while preserving OpenSpec as the artifact workflow dependency.
- `changerail-release-discipline`: require release and migration notes for the
  product/path rename and GitHub repository rename.

## Impact

- `README.md`
- `AGENTS.md`
- `AGENTS.shared.md`
- `docs/**`
- `CHANGELOG.md`, `VERSION` references and release/migration docs
- OpenSpec main specs and board docs that describe the product identity
- Public-surface scans must prevent local/private project names from entering
  tracked rename docs.
