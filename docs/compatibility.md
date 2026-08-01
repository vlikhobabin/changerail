# Compatibility Notes

Этот документ фиксирует tool compatibility expectations для ChangeRail. Он не
заменяет smoke checks: если tool behavior изменился, release должен обновить
notes, migration guide и проверки.

## ChangeRail Version

Current ChangeRail version:

```text
0.3.0
```

Source: root `VERSION`.

`0.3.0` changes ChangeRail delivery runner behavior, consumer Codex auth setup
guidance and approved optional browser MCP package verification. It does not
change Codex CLI, Claude Code or OpenSpec CLI pins, and it does not add browser
MCP packages to default ChangeRail config or generated templates. Existing
consumers should run project-local verification and restart active agent
sessions after updating.

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

## MCP npm packages

Status: exact-version pinned with tracked integrity metadata and a trusted
setup check.

Automatically executed npm MCP packages in `.mcp.json`, `.codex/config.toml`
and generated consumer templates must include exact versions and appear in
`mcp-npm-lock.json`:

```text
@modelcontextprotocol/server-filesystem@2026.7.10
@upstash/context7-mcp@2.1.6
```

Approved optional browser MCP packages for consumer-local tooling are locked in
the same file, but are not part of root ChangeRail config or generated
consumer templates:

```text
@playwright/mcp@0.0.68
chrome-devtools-mcp@0.20.3
```

`verify-project` recognizes these optional packages when a consumer `npx`
command passes the exact pin as a direct package argument,
`--package=<package>@<version>` or `--package <package>@<version>`.
Unversioned, non-exact, unlocked or integrity-mismatched optional browser MCP
packages fail closed like default MCP packages.

`bin/verify-project` treats the lock as a trusted setup gate: it parses
`mcp-npm-lock.json`, requires SRI-shaped npm integrity values, and compares each
referenced package/version with `npm view <package>@<version> dist.integrity
--json`. A mismatch, missing `npm`, unavailable registry lookup or unlisted
package fails verification before the generated project is considered safe to
use with auto-started MCP servers.

Refresh pins only in a reviewed release change:

```bash
npm view @modelcontextprotocol/server-filesystem version dist.integrity --json
npm view @upstash/context7-mcp@2.1.6 version dist.integrity --json
npm view @playwright/mcp@0.0.68 version dist.integrity --json
npm view chrome-devtools-mcp@0.20.3 version dist.integrity --json
python3 scripts/smoke-verify-project.py
python3 scripts/smoke-release-ci.py
```

The smoke suite uses a local fake `npm view` fixture for determinism and includes
a tampered-integrity case. Release review should still run `bin/verify-project`
or the relevant `npm view ... dist.integrity` commands with real registry access
before relying on new pins. Upgrading optional browser MCP packages is separate
release work and should not be folded silently into consumer adoption fixes.

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

## Python Runtime

Status: supported through shared runtime selector for ChangeRail Python helpers.

Expected contract:

- ChangeRail Python helper entrypoints require Python `3.11` or newer.
- Runtime helper dependencies are declared in `requirements-runtime.txt`.
- `tomllib` is required from the Python 3.11 stdlib.
- `jsonschema` is required for schema-backed manifest and verdict validation.
- `requirements-dev.txt` includes runtime requirements plus release-only tools
  such as `PyYAML` and `ruff`; it is not the implicit runtime API.
- Operators can choose a specific interpreter without editing tracked shebangs:

```bash
CHANGERAIL_PYTHON=/opt/example-project/.runtime/python/bin/python \
  /opt/changerail/bin/verify-project /opt/example-project
```

Runtime selection diagnostics are emitted before helper-specific imports when
the interpreter is too old, the override is invalid or a required module is
missing. The selector records sanitized check state only under ignored
runtime state:

```text
.runtime/changerail/python-runtime/last-check.json
```

Install runtime dependencies in the selected environment:

```bash
python3 -m pip install --disable-pip-version-check -r requirements-runtime.txt
```

Verification:

```bash
python3 scripts/smoke-python-runtime.py
```

## ChangeRail Runtime Helpers

Status: supported as tracked Python helpers.

Expected contract:

- `bin/changerail-delivery-runner` launches one card through the repo launcher
  and writes structured runtime status under `.runtime/changerail/delivery-runs/`;
- single-card `preflight` classifies remote publish-target failures as
  `ssh_config`, `dns`, `auth`, `missing_branch`, `timeout` or
  `unknown_remote_failure`; only transient classes are retried, and
  `resume --status-path <status.json>` repeats a full fresh preflight before
  relaunching delivery;
- `bin/changerail-delivery-runner` also exposes explicit queue plan commands
  `plan`, `preflight-plan`, `run-plan`, `resume-plan` and `status-plan` that
  use `changerail.delivery-plan.v1` and
  `changerail.delivery-plan-status.v1` without changing single-card `run`;
- `bin/changerail-delivery-metrics` reads delivery run records and review-cycle
  history plus aggregate queue status and renders missing optional values as
  `unknown`;
- review verdict and delivery manifest helpers validate payloads against
  tracked Draft 2020-12 schemas before applying semantic checks.

Verification:

```bash
python3 scripts/smoke-python-runtime.py
python3 scripts/smoke-delivery-runner.py
python3 scripts/smoke-delivery-metrics.py
python3 scripts/smoke-review-verdict-validation.py
python3 scripts/smoke-review-fingerprint.py
python3 scripts/smoke-contract-schemas.py
```

## Release Gate Tooling

Status: pinned direct Python tooling for the release gate.

`requirements-dev.txt` includes `requirements-runtime.txt` and pins
release-gate Python tools:

```text
-r requirements-runtime.txt
PyYAML==6.0.3
ruff==0.6.9
```

Use an ignored virtualenv before running the full local baseline:

```bash
python3 -m venv .runtime/changerail/ci-venv
.runtime/changerail/ci-venv/bin/python -m pip install \
  --disable-pip-version-check -r requirements-dev.txt
python3 scripts/run-release-baseline.py
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
