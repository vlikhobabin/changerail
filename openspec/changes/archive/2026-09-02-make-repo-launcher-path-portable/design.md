## Context

`bin/codex` уже вычисляет root относительно собственного расположения, однако
`.codex/config.toml` намеренно содержит стабильный consumer contract path
`/opt/changerail`. При запуске development checkout из другого каталога `-C`
указывает на checkout, а trust table и filesystem MCP args остаются привязаны
к стабильной установке. Env interpolation для этих TOML полей не описана в
официальной документации Codex.

Решение затрагивает launcher, operational/compatibility docs, focused smoke и
точный release baseline inventory. Templates и consumer wiring не меняются:
они продолжают использовать `/opt/changerail` как stable source of truth.

## Goals / Non-Goals

**Goals:**

- вычислять canonical root фактического checkout независимо от текущего cwd;
- согласовать с root значения `CODEX_WORKDIR`, `-C`, project trust и filesystem
  MCP scope через документированные CLI configuration overrides;
- корректно кодировать paths с пробелами, одинарными/двойными кавычками и
  обратной косой чертой как TOML values/quoted keys;
- разрешить явный `CHANGERAIL_CODEX_BIN` и найти global dispatcher при наличии
  repo-local `codex` раньше него в `PATH`, не допуская self-recursion;
- доказать argv/env contract fake dispatcher-ом без Codex authentication,
  network и runtime state.

**Non-Goals:**

- переносить stable consumer installation с `/opt/changerail`;
- менять `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`,
  version или dependency pins;
- вводить undocumented env interpolation или записывать вычисленный local path
  в tracked config;
- изменять generated consumer launchers или delivery-runner semantics.

## Decisions

### Canonical root принадлежит launcher

Launcher разрешает физический путь собственного файла и берёт его родителя над
`bin/` как repository root. Он всегда экспортирует этот root в
`CODEX_WORKDIR` и передаёт его через документированный `-C`; ambient
`CODEX_WORKDIR` не может перенаправить repo-local launcher в другой workspace.

Альтернатива — оставить `${CODEX_WORKDIR:-...}` — отвергнута, потому что она не
гарантирует scope фактического checkout.

### Dynamic scope передаётся invocation-level TOML overrides

Launcher кодирует root как TOML basic string и передаёт:

- `projects.<quoted-root>.trust_level="trusted"`;
- полный inline-table `mcp_servers.filesystem`, прочитанный из tracked config,
  с root последним `args` argument.

Это использует документированные precedence и TOML parsing для `-c` и не
изменяет `.codex/config.toml`: статический `/opt/changerail` остаётся понятным
stable default и regression oracle. Полный subtree делает transport, command,
args, cwd, env, timeouts, tools и будущие sibling fields единым launcher-owned
contract. Для `exec` оба overrides повторяются после user overrides в effective
subcommand layer: это учитывает реальную precedence-модель `codex-cli 0.152.1`,
где nested `exec -c` отбрасывает global override layer.

### Dispatcher выбирается по canonical executable identity

Явный `CHANGERAIL_CODEX_BIN` имеет приоритет. Без него launcher перебирает
executable `codex` из `PATH`, canonicalizes каждый candidate и пропускает
собственный файл; отсутствие внешнего dispatcher или явный self-reference
завершаются до `exec` с понятной ошибкой. Это развивает generic идею
сохранённого локального patch, но закрывает recursion case.

### Protected invocation arguments проверяются fail-closed

Launcher сканирует user argv до первого `--` с grammar, подтверждённой для
Codex CLI 0.152.1: separate, assignment и joined short forms `-c`/`--config`,
а также `-C`/`--cd`, принимаются как global options и внутри `exec`. Любой
user working-root option отклоняется. Config override отклоняется только если
его TOML dotted key равен, является предком или потомком launcher-owned
`mcp_servers.filesystem` subtree либо project trust key текущего root.
`--ignore-user-config` отклоняется как реальный config-load bypass. Plain-name
`--profile` остаётся доступным: actual config и `exec` probes доказывают, что
более поздний owned full-subtree layer сохраняет contract. Валидные unrelated
overrides и все остальные user arguments передаются без изменений.
Неоднозначный config override отклоняется, потому что launcher не может
доказать отсутствие protected-key mutation.

### Linux descriptor связывает dispatcher validation и exec

Launcher использует фиксированные `/usr/bin/readlink` и `/usr/bin/python3`, а
также fixed `/bin/bash` shebang, поэтому его helpers не выбираются из user
`PATH`. Выбранный dispatcher открывается один раз, regular/executable inode
проверяется через `/proc/self/fd/<n>`, и именно этот descriptor path передаётся
в `exec`. Direct ELF, script и symlink dispatchers сохраняют обычное Linux
поведение, а rename/replacement candidate pathname после проверки не меняет
запускаемый inode. Сравнение device/inode descriptor-а с launcher закрывает
direct, symlink и hardlink recursion identities.

### Canonical root и PATH разбираются без потери байтов

`readlink -f` output извлекается с terminal sentinel, после чего удаляется
ровно helper newline и sentinel; command substitution больше не удаляет
terminal newlines самого значения. Root вычисляется string-wise из physical
launcher path без дополнительной command substitution. PATH разбирается
итеративно, чтобы каждый empty component, включая единственный component
`PATH=""`, означал current directory; relative components не canonicalize-ятся
до открытия candidate.

### Focused smoke проверяет границу и effective Codex layer

`scripts/smoke-codex-launcher.py` создаёт isolated launcher copies и fake
dispatchers. Он проверяет standard contract config `/opt/changerail`, exact
argv/env/TOML round-trip для Unicode и supported whitespace, explicit path и
bare-name dispatch, direct/symlink/hardlink recursion, все empty/relative PATH
формы, protected и unrelated user options, helper hijack, descriptor-pinned
replacement race, exact failure diagnostics и обычные script/symlink/ELF
dispatchers. Deterministic oracle моделирует потерю global overrides при nested
`exec -c` и требует owned overrides в effective layer. При доступном local
`codex-cli 0.152.1` credential/network-independent temporary config probes
проверяют `mcp get`, adversarial profile, реальный `exec` MCP argv и Node
wrapper через `/proc/self/fd`; отсутствие global Codex не меняет deterministic
обязательный pass. Smoke входит в `core` release suite, а exact inventory
обновляется в runner, oracle и spec.

## Risks / Trade-offs

- [Codex изменит названия documented config keys или CLI parsing] → exact fake
  smoke ловит наш argv contract, а compatibility pin/ручная проверка официальной
  документации остаются prerequisite при обновлении Codex.
- [Необычный path содержит управляющие символы вне TOML basic-string escapes] →
  launcher fail-closed отклоняет такой root; пробелы, кавычки, backslash и
  стандартные whitespace escapes поддерживаются явно.
- [`readlink -f` и `/proc/self/fd` недоступны вне Linux] → текущий stable
  admission уже Linux-focused; native Windows не объявляется поддержанным этой
  задачей.
- [Operator override указывает на launcher] → canonical identity check
  завершает запуск до recursion.

## Migration Plan

После merge существующий `/opt/changerail` продолжает получать тот же root и
тот же effective trust/MCP scope; development clones автоматически получают
свой root. Rollback состоит в возврате launcher/docs/smoke changes; tracked
consumer artifacts и runtime state мигрировать не требуется.

## Open Questions

Нет. Поддерживаемые semantics основаны на официально документированных `-C`,
`-c`, `projects.<path>.trust_level`, `mcp_servers.<id>.args` и CLI precedence.
