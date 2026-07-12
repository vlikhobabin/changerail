# Compatibility Notes

Этот документ фиксирует tool compatibility expectations для ChangeRail. Он не
заменяет smoke checks: если tool behavior изменился, release должен обновить
notes, migration guide и проверки.

## ChangeRail Version

Current ChangeRail version:

```text
0.1.0
```

Source: root `VERSION`.

## Codex CLI

Status: supported through repo-local launcher and skill discovery.

Expected contract:

- operators should start Codex in this repository through `./bin/codex`;
- project trust and filesystem scope are defined in `.codex/config.toml`;
- repo-local skills resolve through `.codex/skills/*` entries;
- Codex runtime/auth/session files under `.codex/` are not part of the public
  tracked surface except `.codex/config.toml` and repo-local skill symlinks.

Verification:

```bash
python3 scripts/smoke-wiring-discovery.py
```

## Claude Code

Status: supported through tracked command wrappers and skill links.

Expected contract:

- ChangeRail slash command wrappers live under `claude/commands/changerail/`;
- short aliases live under `claude/commands/chrl/`;
- consumer projects expose both `.claude/commands/changerail` and
  `.claude/commands/chrl`;
- Claude skills resolve through `.claude/skills`;
- `.claude/settings.local.json` remains local and ignored.

Verification:

```bash
python3 scripts/smoke-wiring-discovery.py
```

## OpenSpec CLI

Status: pinned wrapper.

ChangeRail resolves OpenSpec through `bin/openspec`. The wrapper uses:

```text
@fission-ai/openspec@1.3.1
```

Operators may override the pin for diagnostics only:

```bash
OPENSPEC_VERSION=1.3.0 /opt/changerail/bin/openspec validate --all --strict
```

Release-facing changes should use the wrapper, not an unpinned global command,
when testing ChangeRail contracts:

```bash
/opt/changerail/bin/openspec validate --all --strict
```

## Consumer Project Gates

Before treating a tool combination as compatible, run at least:

```bash
/opt/changerail/bin/verify-project /opt/example-project
python3 /opt/changerail/scripts/smoke-wiring-discovery.py
```

Workspace-level compatibility uses operator-provided drift inventory and must
not be committed to ChangeRail:

```bash
python3 /opt/changerail/scripts/smoke-drift.py \
  --config /opt/changerail/internal/changerail-drift.json
```
