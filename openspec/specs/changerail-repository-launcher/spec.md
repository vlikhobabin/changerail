# changerail-repository-launcher Specification

## Purpose

Зафиксировать portable и fail-closed contract repo-local Codex launcher,
который ограничивает runtime фактическим ChangeRail checkout и не меняет
стабильный consumer path `/opt/changerail`.

## Requirements

### Requirement: Repo-local launcher scopes Codex to its checkout
ChangeRail repo-local launcher MUST вычислять canonical repository root из
собственного физического расположения и MUST использовать этот root как
`CODEX_WORKDIR`, Codex `-C` working root, trusted project key и последний
filesystem MCP scope argument. Ambient `CODEX_WORKDIR` MUST NOT перенаправлять
launcher на другой workspace. Dynamic fields MUST передаваться через
documented invocation-level TOML overrides без env interpolation в tracked
`config.toml`. Launcher MUST передавать полный tracked
`mcp_servers.filesystem` subtree с заменённым последним scope argument и MUST
повторять owned trust/filesystem overrides после user overrides в effective
`exec` layer. Tracked `approval_policy = "never"` и
`sandbox_mode = "danger-full-access"` MUST оставаться неизменными.

#### Scenario: Stable installation remains compatible
- **WHEN** `./bin/codex` запускается из canonical `/opt/changerail`
- **THEN** `CODEX_WORKDIR`, `-C`, trusted project key и filesystem MCP scope
  равны `/opt/changerail`
- **AND** tracked stable consumer config не требует migration

#### Scenario: Development checkout uses its own root
- **WHEN** launcher находится в другом абсолютном checkout и вызывается из
  произвольного current working directory
- **THEN** effective working root, project trust и filesystem MCP scope равны
  фактическому development checkout
- **AND** ни один dynamic scope override не указывает на `/opt/changerail`

#### Scenario: Ambient workdir cannot redirect the launcher
- **WHEN** environment содержит `CODEX_WORKDIR`, отличный от launcher root
- **THEN** launcher заменяет его фактическим repository root до запуска Codex

#### Scenario: User arguments cannot replace launcher scope
- **WHEN** user argv до option terminator содержит `-C`/`--cd` или
  `-c`/`--config` в поддерживаемой separate, assignment либо joined short form,
  которая изменяет launcher-owned project trust либо весь
  `mcp_servers.filesystem` subtree, включая любой ancestor, descendant, command,
  args, enabled, cwd, env, timeout, tools или иной sibling field
- **THEN** launcher завершается exit `1` с точной bounded диагностикой до
  dispatcher launch
- **AND** одинаково применяет policy к global и `exec` option positions

#### Scenario: Nested exec overrides cannot discard launcher scope
- **WHEN** `codex-cli 0.152.1` создаёт отдельный override layer из nested
  `exec -c` user arguments
- **THEN** launcher-owned trust и полный filesystem subtree следуют после них в
  том же effective layer
- **AND** effective filesystem scope остаётся фактическим checkout root

#### Scenario: Config source cannot bypass launcher contract
- **WHEN** user argv до действительного `--` содержит
  `exec --ignore-user-config`
- **THEN** launcher fail-closed отклоняет config-load bypass до dispatcher
  launch
- **AND** unrelated plain-name profile остаётся разрешённым только потому, что
  последующий owned full-subtree layer сохраняет effective contract

#### Scenario: Unrelated user arguments remain available
- **WHEN** user передаёт unrelated valid config override или другой Codex argv
- **THEN** launcher сохраняет исходные argv elements и их порядок
- **AND** args после `--` не интерпретируются launcher-ом как options

### Requirement: Launcher preserves supported path bytes through TOML overrides
Launcher MUST кодировать вычисленный root как валидные TOML basic strings для
quoted project key и filesystem args array. Paths с пробелами, одинарными и
двойными кавычками, обратной косой чертой и стандартными whitespace characters
MUST сохранять значение после TOML parsing. Неподдерживаемые control characters
MUST приводить к fail-closed завершению до Codex launch.

#### Scenario: Root contains spaces and quotes
- **WHEN** checkout root содержит пробелы и кавычки
- **THEN** shell передаёт каждый `-c` override одним argv element
- **AND** TOML parser восстанавливает точный исходный root в project key и
  filesystem MCP args

#### Scenario: Root contains internal or terminal standard whitespace
- **WHEN** checkout root содержит Unicode либо supported backspace, tab,
  newline, form-feed или carriage-return внутри или в конце pathname component
- **THEN** canonical root, environment и оба TOML values восстанавливаются
  byte-for-byte без command-substitution truncation

#### Scenario: Root cannot be represented safely
- **WHEN** checkout root содержит неподдерживаемый TOML control character
- **THEN** launcher завершается non-zero до вызова dispatcher
- **AND** не подставляет приблизительное или усечённое значение

### Requirement: Launcher resolves a non-recursive Codex dispatcher
Launcher MUST поддерживать явный `CHANGERAIL_CODEX_BIN` override и MUST без
override выбирать первый executable `codex` из `PATH`, canonical identity
которого отличается от самого launcher. Missing dispatcher, non-executable
override и self-reference MUST завершаться non-zero до `exec`.
Выбранный Linux dispatcher MUST быть открыт и проверен как regular executable,
а `exec` MUST использовать тот же inode через inherited `/proc/self/fd`, а не
повторно разрешать mutable candidate pathname. Launcher helpers MUST NOT
разрешаться через user-controlled `PATH`.

#### Scenario: Explicit dispatcher override is selected
- **WHEN** `CHANGERAIL_CODEX_BIN` указывает на executable fake или global Codex
  dispatcher
- **THEN** launcher вызывает именно этот dispatcher с scoped argv/env

#### Scenario: Repo bin precedes global dispatcher
- **WHEN** `PATH` сначала содержит каталог самого launcher, а затем каталог
  global `codex` dispatcher
- **THEN** launcher пропускает себя и вызывает следующий dispatcher ровно один
  раз

#### Scenario: PATH preserves every empty and relative component
- **WHEN** executable `codex` доступен через leading, middle, trailing,
  единственный empty или relative PATH component
- **THEN** каждый empty component означает current directory и первый
  non-self executable выбирается в исходном PATH order

#### Scenario: Dispatcher pathname changes after validation
- **WHEN** validated dispatcher pathname atomically заменяется другим inode до
  `exec`
- **THEN** launcher выполняет ранее открытый и проверенный inode
- **AND** replacement не выполняется и не может перенаправить launch

#### Scenario: Dispatcher would recurse
- **WHEN** explicit override или все `PATH` candidates canonicalize к самому
  launcher
- **THEN** launcher завершается non-zero с диагностикой до recursive exec

### Requirement: Launcher smoke is deterministic and credential-free
ChangeRail MUST иметь focused smoke, который использует temporary checkout и
fake Codex dispatcher, не требует credentials/network для обязательного pass и
проверяет stable-path regression contract, exact argv/env/TOML round-trip,
effective `exec` layer, полный protected filesystem subtree, config-load bypass,
full PATH/recursion matrix, helper hijack и descriptor-pinned pathname
replacement. Если внешний `codex-cli 0.152.1` доступен, smoke MUST также
выполнить credential-free temporary-config `mcp get`/`exec` probes для nested
override precedence, adversarial profile, effective filesystem scope и Node
wrapper `/proc/self/fd` execution.

#### Scenario: Focused launcher smoke runs
- **WHEN** maintainer запускает `python3 scripts/smoke-codex-launcher.py`
- **THEN** smoke детерминированно проверяет exact launcher argv/env,
  diagnostics/exit status, TOML/path-byte round-trip, effective-layer
  precedence, full-subtree policy и dispatcher identity
- **AND** temporary/runtime data удаляется без попадания в tracked surface
