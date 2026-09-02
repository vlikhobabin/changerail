## Why

Текущий repo-local launcher вычисляет свой каталог, но committed Codex config
по-прежнему доверяет и передаёт filesystem MCP только `/opt/changerail`. Поэтому
development checkout из другого абсолютного пути может незаметно запустить
Codex с trust и MCP scope стабильной consumer-установки вместо фактического
checkout.

## What Changes

- Launcher вычисляет canonical repository root и принудительно использует его
  как `CODEX_WORKDIR` и Codex working root.
- Launcher передаёт документированные invocation-level TOML overrides для
  project trust и filesystem MCP scope, не полагаясь на env interpolation в
  `config.toml`.
- Добавляется безопасный `CHANGERAIL_CODEX_BIN` override и выбор следующего
  global `codex` dispatcher без рекурсивного повторного запуска launcher.
- Launcher fail-closed отклоняет пользовательские `-C`/`--cd` и только те
  `-c`/`--config` overrides, которые могут изменить launcher-owned project
  trust или filesystem MCP scope; остальные пользовательские аргументы
  сохраняются без перестановки или reinterpretation.
- Launcher-owned trust и полный filesystem server contract помещаются в
  effective `exec` layer после user overrides; config-load bypass отклоняется,
  а profiles проверяются против того же last-owned-layer contract.
- Linux dispatcher открывается, проверяется и запускается через унаследованный
  `/proc/self/fd` descriptor, а launcher helpers выбираются по фиксированным
  системным путям; это связывает validation и exec с одним inode.
- PATH resolution сохраняет POSIX empty-component semantics, включая leading,
  middle, trailing и полностью пустой `PATH`, а canonical root сохраняется
  losslessly для всех поддерживаемых standard whitespace characters.
- Добавляется детерминированный smoke с fake dispatcher для стандартного
  `/opt/changerail` контракта, arbitrary roots/whitespace, полной dispatcher и
  PATH matrix, protected-argument policy, helper hijack и pinned-inode TOCTOU;
  настоящий Codex и credentials не требуются для обязательного pass.
- Обновляются только source-of-truth compatibility/operation docs и release
  verification inventory; stable consumer path `/opt/changerail`, версии и
  package pins не меняются.

## Capabilities

### New Capabilities

- `changerail-repository-launcher`: observable contract repo-local Codex
  launcher для portable development checkout, безопасного dispatcher
  resolution и детерминированной regression-проверки.

### Modified Capabilities

- `changerail-release-ci`: focused launcher smoke входит в точный `core`
  release baseline inventory.

## Impact

Изменение затрагивает `bin/codex`, repo-local `.codex/config.toml` semantics,
`AGENTS.md`, `docs/compatibility.md`, новый focused smoke и точные release
baseline/spec inventories. Consumer projects не получают новые generated
файлы и продолжают считать `/opt/changerail` стабильным source-of-truth path.
Public surface остаётся generic: вычисленный локальный путь существует только
в runtime argv/env и не записывается в tracked файлы.
