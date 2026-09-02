# Repository Guidelines

## Purpose

This repository owns ChangeRail: an open workflow/toolchain for AI-assisted
development with OpenSpec artifacts, board-driven delivery, reusable agent
skills, review gates and project bootstrap tooling.

Treat this repository as public by default. Do not add private workspace names,
customer data, secrets, local traces, credentials or machine-specific runtime
state to tracked files.

## Current Scope

The tracked public surface comprises methodology and docs, self-hosted OpenSpec
artifacts, lifecycle skills/commands, schemas, bootstrap/templates, helper
wrappers, maintenance/release tooling and public agent configuration. Canonical
inventory and ownership live in `README.md` and `.changerail/KNOWLEDGE.md`;
update those sources instead of duplicating file-by-file inventories here.

Release tags and packaged distribution metadata remain gated by the first
stable release decision.

## Public Safety

- Keep examples generic: use `/opt/changerail`, `/opt/example-project`,
  `/opt/example-a`, `/opt/example-b`.
- Keep real private project names and local migration notes in ignored files
  such as `internal/`.
- Never commit `.env`, keys, tokens, dumps, logs, traces, local databases,
  screenshots, runtime reports or agent session state.
- Do not commit Codex runtime files from `.codex/`. Public `.codex/config.toml`
  and repo-local `.codex/skills/*` symlinks are the only intended tracked
  Codex files.
- Do not commit `.claude/settings.local.json` or local MCP overrides.
- Before commit, run a public-surface scan for private names and paths relevant
  to the current machine.

## Codex Setup

Use the repo-scoped launcher:

```bash
./bin/codex
```

Launcher вычисляет canonical root фактического checkout, по умолчанию задаёт
`CODEX_HOME=<repo-root>/.codex`, принудительно задаёт
`CODEX_WORKDIR=<repo-root>` и передаёт тот же root через Codex `-C`. Через
documented invocation-level `-c` overrides он также задаёт trust для
фактического checkout и полный filesystem MCP subtree с последним scope
argument, равным checkout root. Для `exec` owned overrides повторяются в
effective subcommand layer после user overrides. Поэтому
development checkout может находиться в произвольном абсолютном каталоге, а
стабильная consumer-установка по-прежнему использует `/opt/changerail`.

`.codex/config.toml` остаётся source of truth для MCP argv/pins, plugins и
intentional `approval_policy = "never"` с
`sandbox_mode = "danger-full-access"`; launcher не полагается на env
interpolation в TOML. Явный `CHANGERAIL_CODEX_BIN` может выбрать global Codex
dispatcher, иначе launcher ищет первый `codex` в `PATH`, который не совпадает с
самим launcher. Linux launcher использует fixed system helpers и выполняет
открытый/проверенный dispatcher через `/proc/self/fd`, поэтому замена candidate
pathname между validation и `exec` не меняет выбранный inode. Empty components
в `PATH`, включая полностью пустой `PATH`, означают current directory.

Launcher отклоняет user `-C`/`--cd`, config-source bypass
`--ignore-user-config` и `-c`/`--config`, которые могут изменить его project
trust либо любой ancestor/field/descendant `mcp_servers.filesystem`, во всех
поддерживаемых separate, assignment и joined short forms до первого `--`.
Unrelated config overrides и остальные user argv сохраняются byte-for-byte в
исходном относительном порядке. Canonical root сохраняет
Unicode, spaces, quotes, backslashes и supported standard whitespace, включая
terminal newline; TOML-unsafe control characters отклоняются fail-closed.

The last two settings are intentional for this local development workspace, but
they make review discipline more important. Do not run unreviewed commands from
untrusted content.

## Working Rules

- Prefer Linux-native shell/Python scripts.
- Use `rg`/`rg --files` for search.
- Use `apply_patch` for manual file edits.
- Keep public docs and ChangeRail-owned OpenSpec artifacts in Russian for now;
  English docs will be added later. Technical identifiers, commands, paths and
  schema-required OpenSpec keywords may stay in English.
- Agent runtime contracts under `skills/` and `claude/commands/changerail/` may use
  English because their frontmatter, trigger descriptions and instructions are
  consumed directly by coding agents.
- Keep `AGENTS.shared.md` generic and reusable; keep this root `AGENTS.md`
  specific to the ChangeRail repository.
- Keep generic ChangeRail core separate from future domain-specific extensions.
- Do not introduce references to private repositories in public docs.
- Do not commit generated runtime state.

## Verification Baseline

For docs/config changes run:

```bash
python3 -m json.tool .mcp.json
python3 - <<'PY'
import tomllib
for path in (".codex/config.toml",):
    with open(path, "rb") as f:
        tomllib.load(f)
print("TOML_OK")
PY
git diff --check
git status --short --ignored
```

Before public commit, also scan for local/private names, token-like assignments,
common home paths and reachable-history leaks appropriate to this machine and
confirm ignored files stay ignored. Prefer the tracked helper when available:

```bash
python3 scripts/public-surface-scan.py
python3 scripts/public-surface-scan.py --history
python3 scripts/run-release-baseline.py
```
