# Compatibility Notes

Этот документ фиксирует tool compatibility expectations для OPSX. Он не
заменяет smoke checks: если tool behavior изменился, release должен обновить
notes, migration guide и проверки.

## OPSX Version

Current OPSX version:

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

- OPSX slash command wrappers live under `claude/commands/opsx/`;
- consumer projects expose them through `.claude/commands/opsx`;
- Claude skills resolve through `.claude/skills`;
- `.claude/settings.local.json` remains local and ignored.

Verification:

```bash
python3 scripts/smoke-wiring-discovery.py
```

## OpenSpec CLI

Status: pinned wrapper.

OPSX resolves OpenSpec through `bin/openspec`. The wrapper uses:

```text
@fission-ai/openspec@1.3.1
```

Operators may override the pin for diagnostics only:

```bash
OPENSPEC_VERSION=1.3.0 /opt/opsx/bin/openspec validate --all --strict
```

Release-facing changes should use the wrapper, not an unpinned global command,
when testing OPSX contracts:

```bash
/opt/opsx/bin/openspec validate --all --strict
```

## Consumer Project Gates

Before treating a tool combination as compatible, run at least:

```bash
/opt/opsx/bin/verify-project /opt/example-project
python3 /opt/opsx/scripts/smoke-wiring-discovery.py
```

Workspace-level compatibility uses operator-provided drift inventory and must
not be committed to OPSX:

```bash
python3 /opt/opsx/scripts/smoke-drift.py \
  --config /opt/opsx/internal/opsx-drift.json
```
