## Why

Финальная native Windows support claim должна опираться не только на
детерминированные fixture-smokes, но и на live clean-clone proof на обоих
Windows hosts. Без такого proof ChangeRail рискует заявить поддержку, которую
не прошли bootstrap, generated-copy wiring, `.cmd` entrypoints, verification,
refresh и scoped delivery safety вместе.

## What Changes

- Добавить public-safe live proof harness для disposable clean clone lifecycle
  на `windows-host-a` и `windows-host-b`.
- Проверять в clean clone native `.cmd` helper entrypoints, generated-copy
  bootstrap, `verify-project`, skill/command discovery, refresh/update
  semantics и explicit no-push staging safety fixture.
- Встроить proof в aggregate Windows smoke matrix как explicit live item, не
  делая Windows inventory или raw host output частью tracked surface.
- Записать retained sanitized evidence under ignored `.runtime/changerail/`
  и ссылаться на него из карточки/manifest без private host details.
- Добавить недостающий native `.cmd` wrapper для `bootstrap-project`, чтобы
  clean-clone bootstrap path имел native Windows command entrypoint.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-windows-runtime-entrypoints`: supported `.cmd` helper inventory
  includes the bootstrap helper used by the clean-clone lifecycle.
- `changerail-windows-smoke-matrix`: live matrix includes a clean-clone
  consumer lifecycle proof with sanitized two-host evidence.
- `changerail-windows-native-architecture`: final implementation verification
  requires the clean-clone lifecycle proof or an explicit support blocker.

## Impact

- `bin/bootstrap-project.cmd`
- `scripts/smoke-windows-entrypoints.py`
- `scripts/smoke-windows-matrix.py`
- new Windows lifecycle proof helper under `scripts/`
- Windows compatibility/release/migration docs
- Windows-related OpenSpec specs and this board card evidence
