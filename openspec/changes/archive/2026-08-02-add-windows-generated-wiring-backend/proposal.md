## Why

После `030-03` Windows wiring default должен работать без Developer Mode,
administrator elevation и symlink privileges. Текущий bootstrap/adoption
контракт остается symlink-centric, поэтому native Windows support не может
безопасно перейти от `.cmd` entrypoints к project-local wiring.

## What Changes

- Добавить generated-copy backend для command, skill и helper wiring в
  bootstrap/adoption surfaces.
- Выбирать generated-copy backend детерминированно на native Windows по
  platform и tracked project policy.
- Записывать generated ownership metadata с source identity, digest и refresh
  semantics для каждого generated artifact.
- Классифицировать file wiring и directory wiring отдельно, не смешивая их с
  link modes.
- Расширить dry-run output выбранным backend, generated ownership plan и
  fallback reasons.
- Сохранить существующий POSIX symlink wiring как default вне native Windows.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-project-bootstrap`: native Windows bootstrap/adoption generated-copy
  backend, platform policy selection and dry-run reporting.
- `changerail-wiring-discovery`: generated command, skill and helper wiring
  discovery contract for Windows consumers.
- `changerail-windows-native-architecture`: concrete generated ownership
  backend semantics for the selected Windows default.

## Impact

- `bin/bootstrap-project` and related bootstrap/adoption helpers.
- Generated consumer templates or project policy files that record wiring
  ownership.
- `docs/wiring-discovery.md` and compatibility guidance for generated-copy
  Windows wiring.
- Focused bootstrap/wiring smoke fixtures for native Windows generated default
  and POSIX regression coverage.
