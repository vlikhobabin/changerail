# Migration Guide

Этот документ описывает migration notes между версиями ChangeRail. Записи должны
быть public-safe: только generic paths, без private workspace names,
credentials, traces или machine-local inventory.

## Unreleased

- `bootstrap-project --refresh-wiring` is lock-owned and remains fail-closed
  when `openspec/changerail-consumer-lock.json` is missing. Legacy lockless
  consumers use explicit `--configure-existing --adopt-lockless-wiring`
  migration after reviewing the dry-run inventory.
- `verify-project` now reports whether lockless wiring appears adoptable or
  unsafe without recommending overwrite of project-owned surfaces.
- `bootstrap-project --refresh-wiring` ремонтирует только wiring для lock,
  который уже совпадает с текущим ChangeRail source revision. Если consumer
  lock указывает на старую revision, текущий checkout намеренно останавливается
  с source-drift диагностикой: сначала используйте checkout, совпадающий с
  lock, или заведите отдельный explicit migration на принятие новой ChangeRail
  revision в consumer lock.

## 0.4.0 -> 0.5.0

### What Changed

- ChangeRail now has a tracked repository knowledge catalog and maintenance
  lifecycle: deterministic generated index, policy, scan, report, triage,
  baseline/waiver, card preview/deduplication, feedback and quality rollup.
- Operators can run read-only maintenance audits through
  `bin/changerail-maintenance report --json`, `$changerail-maintain audit` or
  `$chrl-maintain audit`. Write-capable maintenance fix mode remains outside
  the supported surface.
- Consumer bootstrap can opt into maintenance with `--with-maintenance`; the
  generated starter catalog, policy and index are first-run green for
  `validate-catalog`, `render-index --check` and `scan --json`.
- POSIX bootstrap defaults to absolute symlink targets and can write
  `changerail.consumer-lock.v1` with advisory or strict source enforcement.
- Existing lockless consumers remain supported through legacy verification and
  explicit `--configure-existing --adopt-lockless-wiring` migration.
  Development fixtures that intentionally use a dirty ChangeRail checkout
  should pass `--lock-enforcement none` explicitly.
- Existing relative-layout consumers can retain that topology with
  `--wiring-path-mode relative`; lock-owned repair uses `--refresh-wiring` and
  refuses project-owned paths or unrelated dirty state.
- Existing wired consumers can run bounded `--configure-existing` with only
  `--link-codex-auth`, lock-owned POSIX `--refresh-wiring` and explicit
  `--adopt-lockless-wiring`; template and profile flags are rejected before
  mutation.
- Greenfield consumers can explicitly request a minimal README and local Git
  initialization. `--init-git` may set the initial branch and `origin`, but
  never stages, commits, pushes or creates a remote repository.
- Generated Codex config now tracks `project_doc_max_bytes = 32768`; older
  consumers without the key use that compatibility default until migrated.
  New bootstrap keeps generated `AGENTS.md` below 70% of that limit. After a
  shared instruction update, inventory every ChangeRail consumer, refresh only
  the marker-bounded generated section, review the project-specific prefix and
  rerun `verify-project` plus the local project baseline.
  Runtime proof is separate and opt-in through `verify-project
  --runtime-diagnostics`; default verification remains static and does not
  invoke Codex.
- **BREAKING** for new unattended bootstrap automation: default generated Codex
  policy is now `safe-interactive`. Automation that requires unattended full
  repository authority must pass `--codex-policy trusted-automation`
  explicitly.

### Required Actions

For operators maintaining the source checkout:

```bash
cd /opt/changerail
git pull --ff-only
python3 -m pip install --disable-pip-version-check -r requirements-runtime.txt
/opt/changerail/bin/verify-project /opt/example-project
```

Restart active Codex/Claude sessions after updating so loaded skill and
workflow-contract text is refreshed.

For lock-backed consumers whose lock already matches the active ChangeRail
checkout, refresh generated-owned wiring and rerun verification. If the lock
pins an older ChangeRail revision, do not run the current checkout as a blind
repair: install the locked revision in a disposable path for lock-owned repair,
or run an explicit consumer migration that accepts the new source revision.
Lockless consumers must first use explicit adoption.

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project --refresh-wiring --skip-verify
/opt/changerail/bin/verify-project /opt/example-project
```

For projects that opt into maintenance:

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project --with-maintenance --skip-verify
cd /opt/example-project
bin/changerail-maintenance validate-catalog --json
bin/changerail-maintenance render-index --check --json
bin/changerail-maintenance scan --json
```

If an existing consumer keeps a customized catalog or policy, review the
generated diff before accepting refresh. Maintenance runtime reports,
annotations, previews, locks and raw logs must remain under ignored
`.runtime/changerail/maintenance/`.

If bootstrap automation relied on the old default trusted Codex authority, add
the explicit policy:

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project \
  --profile generic \
  --codex-policy trusted-automation
```

### Rollback

Return `/opt/changerail` to `v0.4.0`, refresh generated-owned wiring if the
consumer was already updated to `0.5.0`, and rerun project verification:

```bash
git -C /opt/changerail checkout v0.4.0
/opt/changerail/bin/bootstrap-project /opt/example-project --refresh-wiring --skip-verify
/opt/changerail/bin/verify-project /opt/example-project
```

## 0.3.0 -> 0.4.0

### What Changed

- ChangeRail Python helpers now share one runtime selector:
  `bin/changerail-python`.
- Python helper entrypoints require Python `3.11` or newer and runtime
  dependencies from `requirements-runtime.txt`.
- Operators can set `CHANGERAIL_PYTHON` to choose an interpreter without
  editing tracked shebangs.
- Unsupported runtimes fail early with remediation diagnostics before
  helper-specific imports run.
- Native Windows operators can launch supported helper surfaces through tracked
  `.cmd` entrypoints under `bin/` without relying on extensionless POSIX
  wrappers or implicit Bash.
- Native Windows bootstrap uses generated project-local wiring by default,
  includes `bootstrap-project.cmd` in generated helper copies, runs
  `verify-project.cmd` from bootstrap and runs `openspec.cmd` from
  `verify-project`.
- Review verdict freshness validation now binds verdicts to Git tree identity
  and diff fingerprints.
- Publish finalization separates payload and published commits in ignored
  delivery manifests.
- Delivery runner preflight proves remote publish targets, classifies failures
  and supports resume after a fresh transient remote proof.
- Delivery evidence, manifest handoff summaries, one-command delivery smoke and
  queue metrics are part of the release gate.

### Required Actions

For operators maintaining the source checkout:

```bash
cd /opt/changerail
git pull --ff-only
python3 -m pip install --disable-pip-version-check -r requirements-runtime.txt
/opt/changerail/bin/verify-project /opt/example-project
```

Restart active Codex/Claude sessions after updating so loaded skill and
workflow-contract text is refreshed.

For consumer projects that keep generated wrapper copies or copied ChangeRail
helpers, refresh wiring so `bin/changerail-python` and the `.cmd` wrappers point
at the current ChangeRail source of truth:

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project --refresh-wiring --skip-verify
/opt/changerail/bin/verify-project /opt/example-project
```

If the host default `python3` is too old, use an explicit interpreter:

```bash
CHANGERAIL_PYTHON=/opt/example-project/.runtime/python/bin/python \
  /opt/changerail/bin/verify-project /opt/example-project
```

Runtime selector state remains ignored under
`.runtime/changerail/python-runtime/`.

If local automation writes review verdicts directly, refresh it to include the
current `workspace.tree_sha` and `workspace.diff_fingerprint` fields produced
by:

```bash
/opt/changerail/bin/changerail-review-verdict fingerprint --workspace /opt/example-project
```

On native Windows, use the `.cmd` entrypoint for supported helpers, for example:

```bat
set CHANGERAIL_ROOT=C:\opt\changerail
set PROJECT=C:\opt\example-project
"%CHANGERAIL_ROOT%\bin\verify-project.cmd" "%PROJECT%"
```

Native Windows hosts must provide Python `3.11+` with
`requirements-runtime.txt` installed and npm/npx for OpenSpec and MCP integrity
verification:

```bat
py -3 -m pip install --disable-pip-version-check -r "%CHANGERAIL_ROOT%\requirements-runtime.txt"
where node
where npm
where npx
```

For a new empty native Windows consumer, use generated-copy wiring and verify
through native wrappers:

```bat
"%CHANGERAIL_ROOT%\bin\bootstrap-project.cmd" "%PROJECT%" --name example-project --kind generic
"%CHANGERAIL_ROOT%\bin\verify-project.cmd" "%PROJECT%"
```

After updating ChangeRail, refresh generated-owned wiring and rerun
verification:

```bat
"%CHANGERAIL_ROOT%\bin\bootstrap-project.cmd" "%PROJECT%" --refresh-wiring --skip-verify
"%CHANGERAIL_ROOT%\bin\verify-project.cmd" "%PROJECT%"
```

### Rollback

Unset `CHANGERAIL_PYTHON` or point it at the previous supported local Python,
then return `/opt/changerail` to `v0.3.0` and rerun project
verification.

## 0.2.0 -> 0.3.0

### What Changed

- Delivery runner gained `generate-plan`, which emits canonical
  `changerail.delivery-plan.v1` JSON from ordered card paths, workspace aliases
  and optional dependencies.
- Queue `preflight-plan` and `status-plan` now report compact child preflight
  failures such as `example-card: CODEX auth fail` while preserving full child
  `changerail.delivery-run.v1` status records under ignored runtime state.
- Consumer Codex auth setup is documented and checked more explicitly:
  bootstrap can create an opt-in ignored auth marker symlink, `verify-project`
  emits delivery readiness advisories, and runner preflight diagnostics point
  to the remediation guide.
- Approved optional browser MCP packages are locked for consumer-local usage:
  `@playwright/mcp@0.0.68` and `chrome-devtools-mcp@0.20.3`. They remain absent
  from root ChangeRail config and default generated templates.
- Delivery safety-stop handling now preserves `fix_budget_exhausted`, fails
  closed for unpublished child exit `0`, and requires explicit `recovery_for`
  queue cards before blocked downstream work resumes.

### Required Actions

For operators maintaining the source checkout:

```bash
cd /opt/changerail
git pull --ff-only
/opt/changerail/bin/verify-project /opt/example-project
```

Before unattended delivery runner or queue use, configure one supported Codex
auth source for each consumer workspace:

```bash
mkdir -p /opt/example-project/.codex
ln -sfn "$HOME/.codex/auth.json" /opt/example-project/.codex/auth.json
/opt/changerail/bin/changerail-delivery-runner preflight \
  openspec/board/3.inprogress/example-card.md \
  --workspace /opt/example-project --json
```

Alternatively run with explicit `CODEX_HOME`:

```bash
CODEX_HOME="$HOME/.codex" /opt/changerail/bin/changerail-delivery-runner preflight \
  openspec/board/3.inprogress/example-card.md \
  --workspace /opt/example-project --json
```

Consumers that keep local copied ChangeRail skills, runbooks, bootstrap
templates or verification helpers should refresh those copies from
`/opt/changerail`. Symlink-based consumers normally need only `git pull`,
project verification and active agent session restart.

For queue plans, generate and inspect plans before live delivery:

```bash
/opt/changerail/bin/changerail-delivery-runner generate-plan --id example-plan \
  --workspace service-a=service-a --workspace service-b=service-b \
  --card service-a-card.md \
  --card service-b-card=service-b:service-b-card.md \
  --depends service-b-card=service-a-card \
  --output delivery-plan.json --consumer-root /opt/example-workspace
/opt/changerail/bin/changerail-delivery-runner plan delivery-plan.json \
  --consumer-root /opt/example-workspace --json
/opt/changerail/bin/changerail-delivery-runner preflight-plan delivery-plan.json \
  --consumer-root /opt/example-workspace --json
```

### Rollback

Return `/opt/changerail` to the previous release tag and rerun project
verification:

```bash
git -C /opt/changerail checkout v0.2.0
/opt/changerail/bin/verify-project /opt/example-project
```

If a queue was already started with `0.3.0`, inspect ignored aggregate status
under `.runtime/changerail/delivery-plans/` before resuming on an older
checkout, because compact diagnostics and recovery-card evidence may be easier
to interpret with the newer runner.

## 0.1.0 -> 0.2.0

### What Changed

- **BREAKING**: OPSX has been renamed to ChangeRail. The canonical source path
  is `/opt/changerail`; lifecycle commands are `/changerail:*`; Codex skills are
  `$changerail-*`; helper wrappers use `bin/changerail-*`; runtime evidence
  uses `.runtime/changerail`; public schema ids use `changerail.*.v1`.
- Pinned OpenSpec CLI bumped `1.3.0` -> `1.3.1`. `skills/openspec-*` were
  refreshed with `openspec update` (all lifecycle skills preserved; sharper
  `contextFiles` guidance in apply-change/verify-change). Not breaking.
- Delivery runner and metrics helpers are tracked: `bin/changerail-delivery-runner`
  writes `changerail.delivery-run.v1` runtime status, and
  `bin/changerail-delivery-metrics` reads run records plus review-cycle history.
- Review and manifest contracts now include fresh reviewer independence,
  review-cycle history, delivery manifest derivation, publish finalization
  metadata and schema-backed helper validation.
- Daily aliases `$chrl-*` and `/chrl:*` are available while canonical runtime
  names remain `changerail`.
- Release verification now includes pinned `ruff`/`jsonschema` tooling,
  contract schema smoke, inventory-based Python compile checks, public-surface
  scans and a single local release baseline command.
- **BREAKING**: autonomous repeated `NO-GO` policy changed. Default
  `changerail-deliver` same-card rescue budget is now two bounded rescue/review
  cycles. When the budget is exhausted, the autonomous path is linked
  rescue/replacement or investigation card escalation, not manual exceptional
  authorization.

### Required Actions

For operators maintaining the source checkout at `/opt/changerail`:

```bash
cd /opt/changerail
git pull --ff-only
/opt/changerail/bin/verify-project /opt/example-project
```

If the local checkout still uses the old OPSX source path:

```bash
cd /opt
mv opsx changerail
git -C /opt/changerail remote -v
git -C /opt/changerail remote set-url origin git@github.com:vlikhobabin/changerail.git
```

Rename the GitHub repository from `opsx` to `changerail` before migrating known
local consumers. If `/opt/changerail` already exists, do not overwrite it:
inspect both checkouts and choose one source of truth. Treat old GitHub
redirects as compatibility only, not canonical documentation targets.

For existing consumers, migrate one project at a time:

- finish or stop active Claude/Codex sessions in that project;
- replace `/opt/opsx` symlinks with `/opt/changerail`;
- replace `.claude/commands/opsx`, `.codex/skills/opsx-*` and `bin/opsx-*`
  defaults with ChangeRail equivalents;
- update project docs/config that mention `/opsx:*`, `$opsx-*`,
  `.runtime/opsx` or `opsx.*.v1`;
- run `/opt/changerail/bin/verify-project /opt/example-project`.

For consumers whose `bin/openspec` and lifecycle skills symlink into
`/opt/changerail`: no tracked file rewiring is required for the autonomous
`NO-GO` policy. Re-run verification and restart active agent sessions so loaded
skill text is refreshed:

```bash
/opt/changerail/bin/verify-project /opt/example-project
```

Stop or finish active Claude/Codex sessions before relying on the new
five-cycle rescue policy. A long-lived session may still have the old
two-cycle/manual authorization instructions in memory.

Consumers that keep a local `openspec-*` copy (not a symlink into ChangeRail) can
refresh it to `1.3.1` with `openspec update` in that project, or switch to the
ChangeRail symlink to track the pin centrally.

Consumers that keep local copied ChangeRail lifecycle skills or runbooks must
refresh at least:

- `changerail-deliver` / `chrl-deliver`;
- any local instructions that mention `--max-review-cycles 2`, two rescue
  attempts, third consecutive `no-go` safety stop, or manual exceptional
  authorization as the default path;
- local delivery runbooks that decide what to do after repeated `NO-GO`.

After refresh, run:

```bash
/opt/changerail/bin/verify-project /opt/example-project
python3 /opt/changerail/scripts/smoke-wiring-discovery.py
```

For maintainers preparing a ChangeRail release, install release-gate tooling in
an ignored virtualenv and run the local baseline:

```bash
cd /opt/changerail
python3 -m venv .runtime/changerail/ci-venv
.runtime/changerail/ci-venv/bin/python -m pip install \
  --disable-pip-version-check -r requirements-dev.txt
python3 scripts/run-release-baseline.py
```

Existing consumers do not need to adopt runner/metrics helpers unless they want
non-interactive supervised delivery records or aggregate review/delivery
metrics.

### Rollback

Return `/opt/changerail` to the previous reviewed commit or release point and
rerun project verification:

```bash
git -C /opt/changerail checkout <previous-reviewed-ref>
/opt/changerail/bin/verify-project /opt/example-project
```

If the rollback is only for OpenSpec CLI compatibility, override the pin for one
command without changing the wrapper:

```bash
OPENSPEC_VERSION=1.3.0 /opt/changerail/bin/openspec validate --all --strict
```

## 0.1.0

Initial public baseline.

### From

No earlier public ChangeRail release.

### What Changed

- ChangeRail source of truth documented under `/opt/changerail`.
- Generic lifecycle skills and Claude command wrappers are present.
- OpenSpec lifecycle skills are present.
- Project bootstrap, verify-project, drift gate and wiring smoke are present.
- Release discipline docs are introduced.

### Required Actions

For a new consumer project:

```bash
/opt/changerail/bin/bootstrap-project /opt/example-project \
  --name example-project \
  --kind generic
```

For an already wired consumer project:

```bash
/opt/changerail/bin/verify-project /opt/example-project
```

For workspace-level drift:

```bash
python3 /opt/changerail/scripts/smoke-drift.py \
  --config /opt/changerail/internal/changerail-drift.json
```

Keep the inventory in ignored operator-controlled space such as `internal/`.

### Rollback

Return `/opt/changerail` to the previous commit/tag and rerun project-local
verification:

```bash
/opt/changerail/bin/verify-project /opt/example-project
```

Because `0.1.0` is the initial public baseline, rollback target is the
operator's previous local checkout.
