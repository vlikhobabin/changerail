## Why

Consumers need portable maintenance wiring only when they explicitly opt in.
Making maintenance mandatory during bootstrap or verification would change
existing consumer policy and conflict with the broader profile work owned by
card `050`.

## What Changes

- Add additive `bin/bootstrap-project --with-maintenance` opt-in wiring.
- Extend project templates with maintenance policy/config/helper/ignore
  skeletons only for opted-in consumers.
- Extend `verify-project` to treat tracked maintenance declarations as the
  opt-in signal.
- Verify complete helper, schema, config and ignore wiring for opted-in
  consumers.
- Keep consumers without maintenance artifacts valid and unchanged.
- Cover POSIX symlink wiring, native Windows generated-copy ownership and stale
  refresh behavior for maintenance helpers.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-project-bootstrap`: добавить explicit `--with-maintenance`
  bootstrap behavior.
- `changerail-project-templates`: добавить opt-in maintenance template surface
  and generated-copy ownership expectations.
- `changerail-project-verification`: добавить opt-in detection and verifier
  checks for maintenance wiring.

## Impact

- `bin/bootstrap-project`, `bin/verify-project`, templates and smoke fixtures
  gain optional maintenance wiring paths.
- Generated-copy manifests include maintenance helper ownership on Windows.
- Existing consumers and default bootstrap runs remain unchanged unless
  `--with-maintenance` is supplied.
