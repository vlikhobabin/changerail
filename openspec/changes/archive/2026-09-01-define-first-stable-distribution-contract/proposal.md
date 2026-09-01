## Why

Первый stable release уже разрешен clean-core scope, но ChangeRail пока не
определяет минимальный воспроизводимый distribution bundle, который можно
однозначно связать с reviewed commit и проверить независимо от локальной
машины. Без такого contract tag или GitHub Release не дают достаточного
source-revision и checksum evidence.

## What Changes

- Определить generic source distribution как воспроизводимый `tar.gz`,
  построенный из exact Git commit без language-specific package registry.
- Добавить публикуемый рядом с source archive metadata sidecar: version,
  license path и автоматически подставленный Git source revision; сам archive
  остается exact tracked tree выбранного commit.
- Добавить deterministic builder и smoke-проверку archive layout,
  reproducibility, metadata и SHA-256 sidecar.
- Документировать asset naming, build/verify commands и fail-closed границы
  между reviewed payload, annotated tag и public GitHub Release.
- Не менять runtime behavior и существующие dependency pins.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-discipline`: дополнить release discipline нормативным
  generic source distribution, reproducibility, checksum, license, version и
  source-revision contract.

## Impact

Затрагиваются release documentation, root distribution metadata, отдельный
release build helper, его smoke coverage и release baseline inventory.
Consumer runtime, bootstrap behavior, MCP pins и language package managers не
изменяются.
