# Migration Guide

Этот документ описывает migration notes между версиями ChangeRail. Записи должны
быть public-safe: только generic paths, без private workspace names,
credentials, traces или machine-local inventory.

## Unreleased

### What Changed

- ChangeRail Python helpers now share one runtime selector:
  `bin/changerail-python`.
- Python helper entrypoints require Python `3.11` or newer and runtime
  dependencies from `requirements-runtime.txt`.
- Operators can set `CHANGERAIL_PYTHON` to choose an interpreter without
  editing tracked shebangs.
- Unsupported runtimes fail early with remediation diagnostics before
  helper-specific imports run.

### Required Actions

For operators maintaining the source checkout:

```bash
cd /opt/changerail
python3 -m pip install --disable-pip-version-check -r requirements-runtime.txt
python3 scripts/smoke-python-runtime.py
```

For consumer projects that keep generated wrapper symlinks, refresh wiring so
`bin/changerail-python` points at the ChangeRail source of truth:

```bash
ln -sfnT /opt/changerail/bin/changerail-python /opt/example-project/bin/changerail-python
/opt/changerail/bin/verify-project /opt/example-project
```

If the host default `python3` is too old, use an explicit interpreter:

```bash
CHANGERAIL_PYTHON=/opt/example-project/.runtime/python/bin/python \
  /opt/changerail/bin/verify-project /opt/example-project
```

Runtime selector state remains ignored under
`.runtime/changerail/python-runtime/`.

### Rollback

Unset `CHANGERAIL_PYTHON` or point it at the previous supported local Python,
then return `/opt/changerail` to the previous reviewed ref and rerun project
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
  `changerail-deliver` same-card rescue budget is now five bounded rescue/review
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
