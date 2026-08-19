# Compatibility Notes

Этот документ фиксирует tool compatibility expectations для ChangeRail. Он не
заменяет smoke checks: если tool behavior изменился, release должен обновить
notes, migration guide и проверки.

## ChangeRail Version

Current ChangeRail version:

```text
0.5.0
```

Source: root `VERSION`.

`0.5.0` adds the repository knowledge and maintenance surface, hardens
consumer bootstrap/verification through explicit profiles, consumer locks,
generated-owned refresh and runtime diagnostics, and expands release CI with
maintenance, repository-knowledge and generated consumer-CI smokes. It does not
change Codex CLI, Claude Code, OpenSpec CLI or MCP npm package pins. Existing
consumers should install refreshed runtime dependencies, run project-local
verification and restart active agent sessions after updating.

## Codex CLI

Status: supported through repo-local launcher and skill discovery.

Expected contract:

- operators should start Codex in this repository through `./bin/codex`;
- project trust and filesystem scope are defined in `.codex/config.toml`;
- repo-local skills resolve through `.codex/skills/*` entries;
- Codex runtime/auth/session files under `.codex/` are not part of the public
  tracked surface except `.codex/config.toml` and repo-local skill symlinks.

Generated consumers track `project_doc_max_bytes = 32768`. Static verifier
measurement uses UTF-8 bytes: below 85 percent passes, 85 percent through the
limit warns non-blocking, and over the limit fails blocking. A missing key in
an older consumer uses the same compatibility default until migration.

Opt-in runtime diagnostics currently support the `codex-cli 0.147.x`
`doctor --json` schema version 1 and `debug prompt-input` JSON shape. Other
versions or schemas are reported as unsupported/invalid rather than runtime
success. Default `verify-project` never invokes Codex; explicit
`--runtime-diagnostics` requires project-local `CODEX_HOME`, stores raw output
under ignored `.runtime/changerail/diagnostics/` and emits only allowlisted
statuses, role classes, counts and project-relative evidence location.

Verification:

```bash
python3 scripts/smoke-wiring-discovery.py
python3 scripts/smoke-runtime-diagnostics.py
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
- `markdown-it-py` (`markdown_it` import module) is required for deterministic
  maintenance Markdown local-link checks.
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
- review verdict/preflight and delivery manifest helpers validate payloads
  against tracked Draft 2020-12 schemas before applying semantic checks;
  deterministic preflight blocks manifest/board/scope/strict-check defects
  before an LLM payload review is launched.

Verification:

```bash
python3 scripts/smoke-python-runtime.py
python3 scripts/smoke-windows-entrypoints.py
python3 scripts/smoke-delivery-runner.py
python3 scripts/smoke-delivery-metrics.py
python3 scripts/smoke-review-verdict-validation.py
python3 scripts/smoke-review-fingerprint.py
python3 scripts/smoke-review-fingerprint-benchmark.py
python3 scripts/smoke-review-fingerprint-cache.py
python3 scripts/smoke-review-preflight.py
python3 scripts/smoke-contract-schemas.py
python3 scripts/smoke-maintenance-runner.py
python3 scripts/smoke-repository-knowledge.py
```

## ChangeRail Maintenance

Status: supported as a read-only/default repository maintenance lifecycle with
explicit local write flags only.

Expected contract:

- `bin/changerail-maintenance` validates repository knowledge catalogs,
  renders deterministic indexes, scans active knowledge, builds lifecycle
  reports, validates triage annotations, previews cards and computes feedback
  and quality rollups;
- default audit/report/triage/card-preview operations write only ignored
  runtime state or no state at all;
- tracked writes require explicit operator flags such as `render-index --write`,
  `accept-baseline --write` or `cards --write`;
- maintenance does not commit, push, publish, open pull requests, write issues
  or mutate external systems;
- consumer opt-in through `bootstrap-project --with-maintenance` creates a
  first-run-green starter catalog, policy and generated index.

Verification:

```bash
bin/changerail-maintenance validate-catalog --json
bin/changerail-maintenance report --json
python3 scripts/smoke-maintenance-runner.py
python3 scripts/smoke-repository-knowledge.py
```

## Native Windows Lab

Status: research lab available through operator-managed SSH inventory for
series `030-native-windows-discovery`.

The native Windows lab is a controlled research surface, not permanent CI
infrastructure. Tracked ChangeRail files identify hosts only as
`windows-host-a` and `windows-host-b`. Raw hostnames, usernames, SSH targets,
credentials, private Windows paths, disposable root mappings and raw session
logs remain in ignored operator/runtime files.

Default ignored inventory path:

```text
internal/windows-lab-inventory.json
```

Public-safe inventory shape:

```json
{
  "schema": "changerail.windows-lab-inventory.v1",
  "hosts": [
    {
      "id": "windows-host-a",
      "ssh_command": "ssh windows-host-a",
      "disposable_root": "C:/Temp/changerail-lab-a"
    },
    {
      "id": "windows-host-b",
      "ssh_command": "ssh windows-host-b",
      "disposable_root": "C:/Temp/changerail-lab-b"
    }
  ]
}
```

Protocol rules:

- run probes through `scripts/windows-lab-probe.py`;
- use only non-interactive SSH commands with per-host timeout;
- create a per-run child directory under each ignored `disposable_root`;
- transfer only deterministic test fixtures into that disposable directory;
- clean up only files and directories created by the probe, and make cleanup
  idempotent;
- do not write to real ChangeRail or consumer repositories on the Windows
  hosts;
- do not request UAC, `runas`, administrator elevation or persistent machine
  configuration without a separate operator action recorded by the active card;
- retain raw command output only under ignored `.runtime/changerail/` evidence
  paths;
- copy only command class, generic host id, outcome and sanitized capability
  values into tracked cards or docs.

Local dry-run validation does not contact real Windows hosts:

```bash
python3 scripts/windows-lab-probe.py dry-run --sample --json
```

Live research probes use the ignored inventory and write sanitized reports under
ignored runtime state:

```bash
python3 scripts/windows-lab-probe.py run \
  --inventory internal/windows-lab-inventory.json --json
```

Current `030-01` native Windows lab baseline:

```text
retained report: .runtime/changerail/windows-lab/20260802T060958Z/report.json
aggregate result: passed, 2/2 hosts ready
command class: non-interactive SSH + PowerShell readiness probe
```

| Host | OS baseline | Filesystem | Git | Python | Shell | Privilege |
| --- | --- | --- | --- | --- | --- | --- |
| `windows-host-a` | Windows 11 Pro, version `10.0.22631`, build `22631`, `64-bit` | disposable root present, `NTFS` | `git version 2.43.0.windows.1` | `python`: `Python 3.13.1`; `py -3`: `Python 3.13.1` | Windows PowerShell `5.1.22621.4391`, Desktop edition | current SSH token reported `elevated=true`; Developer Mode `unknown` |
| `windows-host-b` | Windows 11 Pro, version `10.0.26200`, build `26200`, `64-bit` | disposable root present, `NTFS` | `git version 2.45.2.windows.1` | `python`: `Python 3.13.1`; `py -3`: `Python 3.13.1` | Windows PowerShell `5.1.26100.8972`, Desktop edition | current SSH token reported `elevated=true`; Developer Mode `unknown` |

Readiness checks passed on both hosts: SSH access, non-interactive PowerShell
execution, disposable root setup, deterministic fixture write/read and
idempotent cleanup. The elevated-token observation records the current SSH
session capability only; it does not authorize elevated destructive probes.
Future elevated-mode research still requires separate operator action in the
active card.

Current `030-02` native Windows runtime/wiring reproduction:

```text
primary report: .runtime/changerail/windows-runtime-wiring/20260802T070216Z/report.json
repeatability report: .runtime/changerail/windows-runtime-wiring/20260802T070225Z/report.json
aggregate result: passed, 2/2 hosts completed cleanup
command class: non-interactive SSH + remote Python disposable runtime/wiring probe
repeatability: 0 per-check status mismatches between primary and cleanup rerun
```

Both hosts ran the same disposable fixture. Current SSH sessions again reported
`elevated=true`, Developer Mode remained `unknown`, and the harness did not
request UAC, `runas` or persistent elevation. Therefore direct `os.symlink`
was observed under the current SSH token, while non-elevated Developer Mode
symlink behavior is explicitly `not-applicable` for this run.

| Strategy | `windows-host-a` | `windows-host-b` | Trade-offs |
| --- | --- | --- | --- |
| Direct directory `os.symlink` | passed under current elevated SSH token | passed under current elevated SSH token | Small tracked surface, but privilege/Developer Mode portability is not proven by this lab token. |
| Direct file `os.symlink` | passed under current elevated SSH token | passed under current elevated SSH token | File links behave separately from directory links; same privilege caveat as directory symlinks. |
| Non-elevated Developer Mode symlink proof | not applicable: token already elevated, Developer Mode `unknown` | not applicable: token already elevated, Developer Mode `unknown` | Requires a future explicitly non-elevated host token before using as the default portability claim. |
| Directory junction | passed | passed | No Developer Mode evidence required in this run, but Git sees the junction path during status/add/index checks and cleanup must be link-aware. |
| Generated copy drift | passed: source update left copy stale | passed: source update left copy stale | Most portable and Git-friendly, but requires explicit drift detection and refresh on ChangeRail source updates. |
| Generated copy source refresh | passed: explicit refresh matched source | passed: explicit refresh matched source | Upgrade behavior is deterministic only when the generator owns refresh semantics. |
| Direct extensionless `bin/openspec` launch | failed with Win32 application error | failed with Win32 application error | Native Windows direct process launch cannot rely on extensionless shell scripts. |
| `.cmd` wrapper launch | passed | passed | Best native operator entrypoint candidate among wrapper variants observed here. |
| PowerShell wrapper launch | passed | passed | Works on both hosts, but adds PowerShell quoting/execution-policy surface. |
| Python wrapper launch | passed | passed | Works on both hosts because Python is present; couples runtime entrypoint to Python availability. |
| Explicit Bash invocation | unsupported: Bash unavailable | failed through the host Bash/WSL environment | Not portable across the two-host lab and unsuitable as the native default. |
| Git porcelain/dry-run/index inspection | passed; all linked/generated paths were mentioned | passed; all linked/generated paths were mentioned | Git does not make wiring invisible: status, `git add --dry-run` and index inspection must be part of Windows safety checks. |

Current `030-03` native Windows architecture decision:

```text
status: architecture frozen; implementation planned in series 040
runtime default: tracked .cmd entrypoints
wiring default: generated project-local copies with verifier/drift ownership
```

The selected native Windows default is intentionally conservative. Native
Windows support must not depend on direct extensionless wrapper launch, implicit
Bash, Developer Mode, administrator elevation or junction traversal. The
default implementation path is:

| Surface | Default | Bounded fallbacks | Evidence basis |
| --- | --- | --- | --- |
| Command entrypoints | tracked `bin/*.cmd` wrappers | Python helper invocation for Python-backed helpers; PowerShell only for diagnostics or explicit fallback; POSIX wrapper only in POSIX/WSL environments | `.cmd`, PowerShell and Python wrapper launches passed on both hosts; extensionless direct launch and implicit Bash did not |
| Project wiring | generated project-local command, skill and helper copies owned by a verifier-readable manifest | symlink mode only after explicit operator opt-in and verified Developer Mode/privilege; junction mode only as an explicit compatibility fallback with link-aware cleanup and Git-safety evidence | generated copy drift and refresh were deterministic; symlink success was observed only under elevated tokens; Git sees junction paths |
| Bootstrap/verify/drift | generated-copy bootstrap, `verify-project` ownership checks and refresh share one wiring classification | local absolute config only through explicit operator opt-in | deterministic local fixtures cover generated ownership, stale copies, divergence, refresh and POSIX regression; live Windows host proof remains in later `040` cards |

Prerequisites for the selected native Windows support path:

- Windows host with `cmd.exe` and Windows PowerShell available for diagnostics
  and lab automation.
- Python `3.11` or newer reachable through `python` or `py -3` for
  ChangeRail Python helpers.
- Git for Windows available for repository checks, `git status --porcelain`,
  `git add --dry-run` and index inspection.
- Developer Mode, administrator elevation and symlink privilege are not
  prerequisites for the generated-copy default.
- Symlink fallback requires explicit operator selection and positive
  least-privilege or privilege evidence on the target host. Bootstrap accepts a
  native probe result or a validated `--windows-fallback-proof` report with
  source metadata plus concrete evidence for passed directory symlink, file
  symlink and privilege/Developer Mode checks; status-only reports fail closed.
- Junction fallback requires explicit operator selection, link-aware cleanup and
  fail-closed Git-safety checks before any staging recommendation. Bootstrap
  requires a validated `--windows-fallback-proof` report with source metadata
  plus concrete evidence for passed junction creation, link-aware cleanup, Git
  status, dry-run add and index-safety checks; status-only reports fail closed.

Tracked/generated/ignored ownership:

- ChangeRail tracked source owns templates, skill directories, Claude command
  wrappers, helper scripts, `.cmd` wrappers, schemas, specs and docs.
- Consumer tracked files may include rendered project config and generated
  command, skill and helper wiring copies when they are declared
  generated-owned by a manifest or tracked project policy.
- Generated copied wiring must carry enough source identity, content digest or
  equivalent metadata for `verify-project` and drift checks to distinguish
  valid generated content from stale copies or project-owned divergence.
- Machine-local source roots, Windows lab inventory, raw SSH/session output,
  raw reports, temporary refresh state, credentials and agent runtime state
  remain ignored.
- Refresh/upgrade updates only manifest-owned generated files and must not
  overwrite project-owned files silently.
- Cleanup removes only files created by the current run or marked
  generated-owned; symlink and junction paths must be treated as links rather
  than traversed recursively.

Threat model for implementation:

- Junction traversal can expose ChangeRail source to consumer Git operations;
  junction mode is therefore explicit fallback only.
- Accidental staging is blocked by explicit path staging plus Git porcelain,
  dry-run add and index checks for generated, symlink and junction paths.
- Credentials near Codex, Claude, MCP, SSH or runtime state must never be
  copied, printed or committed.
- Windows command construction must preserve argv, cwd, environment and exit
  code, and must handle spaces and non-ASCII paths without shell
  reinterpretation.
- Untrusted repository content must not be interpolated into shell strings; use
  structured argv or an equivalent quoting discipline.

Mandatory implementation test matrix for series `040`:

- deterministic local fixtures for `.cmd` wrappers, argv/cwd/env/exit-code
  propagation, spaces and non-ASCII paths;
- generated-copy wiring fixtures for fresh bootstrap, stale copy detection,
  explicit refresh, project-owned divergence and partial-failure cleanup;
- Git safety fixtures for status, dry-run staging and index inspection;
- negative fixtures for extensionless launch, implicit Bash assumptions,
  unsupported symlink fallback and unsafe junction fallback;
- live sanitized smoke on `windows-host-a` and `windows-host-b`, or an explicit
  blocker/caveat before claiming host coverage;
- repeatability after cleanup;
- primary Linux release baseline to preserve existing POSIX behavior.

Automated native Windows smoke is aggregated by:

```bash
python3 scripts/smoke-windows-matrix.py --json
```

Default local mode is platform-neutral: it runs from the current ChangeRail
checkout, creates disposable fixtures under ignored `.runtime/changerail/`,
executes the focused entrypoint, bootstrap, verifier/drift and Git-safety
smokes, and validates the public-safe Windows lab report shape without
contacting real Windows hosts. A local pass is not a two-host support claim;
it only proves the deterministic fixture contract.

Repeatability after cleanup is checked with:

```bash
python3 scripts/smoke-windows-matrix.py --repeat --json
```

The repeat run executes the same local matrix after cleanup and reports any
status mismatch in the retained matrix report.

Live two-host smoke is explicit and uses ignored operator inventory:

```bash
python3 scripts/smoke-windows-matrix.py --live \
  --inventory internal/windows-lab-inventory.json --json
```

The live matrix may track only generic host ids `windows-host-a` and
`windows-host-b`. It writes sanitized structured reports under ignored
`.runtime/changerail/windows-smoke/` and retains raw child command output only
below that ignored run directory. If either host is unavailable, cleanup fails
or a live probe cannot complete, the card or operator report must record a
sanitized blocker/caveat before claiming host coverage.

Future Windows CI can use the same live command only when the runner provides
inventory through secure runner-local configuration. SSH targets, usernames,
credentials, private disposable roots and raw host output must remain outside
tracked repository files.

Current native Windows clean-clone end-to-end result after the follow-up
prerequisite remediation pass:

```text
aggregate live matrix report: .runtime/changerail/windows-smoke/20260802T151242Z-1f65f8db/report.json
clean-clone child report: .runtime/changerail/windows-smoke/20260802T151242Z-1f65f8db/primary/live/clean-clone-lifecycle/primary/report.json
aggregate result: passed, 9/9 matrix items passed
clean-clone lifecycle: passed, 2/2 hosts passed, 16/16 host checks passed
```

This result establishes the generated-copy native Windows clean-clone lifecycle
on both prepared operator-managed Windows hosts. The support claim is scoped to
the documented prerequisites: Git, Python `3.11+` with
`requirements-runtime.txt`, `cmd.exe`, Node/npm/npx and npm registry access.
Host identities, SSH targets, private disposable roots and raw output remain
ignored runtime state.

| Host | Prerequisite baseline | Live clean-clone result |
| --- | --- | --- |
| `windows-host-a` | Git, Python `3.13.1`, Node `v24.11.1`, npm `11.6.2`; selected Python can import runtime modules from `requirements-runtime.txt` | passed clean clone, native `.cmd` helper launch, generated-copy bootstrap, `verify-project.cmd`, generated surface discovery, stale generated wiring refresh, scoped no-push staging and cleanup |
| `windows-host-b` | Git, Python `3.13.1`, Node `v24.11.1`, npm `11.15.0`; selected Python can import runtime modules from `requirements-runtime.txt` | passed clean clone, native `.cmd` helper launch, generated-copy bootstrap, `verify-project.cmd`, generated surface discovery, stale generated wiring refresh, scoped no-push staging and cleanup |

Local deterministic matrix items passed in the same aggregate run:
entrypoint smoke `56/56`, generated bootstrap smoke `15/15`, verifier/drift
smoke `40/40`, Windows wiring Git safety smoke `6/6`, lab sample dry-run and
runtime/wiring sample dry-run. Live readiness and live runtime/wiring smoke
also passed on both hosts.

Implemented native runtime entrypoint surface:

- `bin/bootstrap-project.cmd`
- `bin/openspec.cmd`
- `bin/changerail-python.cmd`
- `bin/changerail-delivery-manifest.cmd`
- `bin/verify-project.cmd`
- `bin/changerail-review-verdict.cmd`
- `bin/changerail-evidence.cmd`
- `bin/changerail-delivery-runner.cmd`
- `bin/changerail-delivery-metrics.cmd`
- `bin/changerail-maintenance.cmd`
- `bin/changerail-maintenance-runner.cmd`

Python-backed `.cmd` wrappers launch through `changerail-python.cmd`, which
uses the same Python `3.11+` and `requirements-runtime.txt` contract as the
POSIX selector. `openspec.cmd` invokes the pinned OpenSpec CLI version through
native Windows command launch. Deterministic wrapper behavior coverage is part
of the `040-01` entrypoint verification change. `bootstrap-project` selects
`verify-project.cmd` on native Windows, and `verify-project` selects
`openspec.cmd` for OpenSpec validation on native Windows. Live Windows
clean-clone coverage passed on both prepared hosts in the follow-up live matrix.

Series `040-native-windows-implementation` owns the runtime implementation for
this decision. The generated-copy implementation is present and has two-host
live clean-clone evidence after the Windows lab hosts provided the documented
Python runtime modules and npm/npx tooling.

## Bootstrap Profile Compatibility

New consumers use canonical `--profile generic|workspace-root|service`,
`--surfaces all-surfaces|codex-only` and
`--codex-policy safe-interactive|trusted-automation`. In `0.5.0`, the public
default changed from implicit unattended full access to explicit
`safe-interactive`, which renders `on-request` and `workspace-write`. Existing
automation that depends on the old authority must pass
`--codex-policy trusted-automation`; existing generated consumers are not
rewritten automatically.

`--kind` remains a bounded alias for `--profile`. Matching values are accepted,
while conflicting canonical and legacy values fail before target mutation.
Consumers generated before canonical profile metadata remain supported through
the strict all-surfaces verification path.

POSIX greenfield consumers default to absolute symlink targets. Explicit
`--wiring-path-mode relative` remains supported for a shared movable tree.
Schema-valid `changerail.consumer-lock.v1` adds advisory or strict revision
matching without changing frozen Windows generated-copy ownership semantics.
Lockless consumers remain on the legacy wiring checks; missing lock alone is
not a blocking failure.

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
