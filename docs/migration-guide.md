# Migration Guide

Этот документ описывает migration notes между версиями ChangeRail. Записи должны
быть public-safe: только generic paths, без private workspace names,
credentials, traces или machine-local inventory.

## Unreleased

### What Changed

- **BREAKING**: OPSX has been renamed to ChangeRail. The canonical source path
  is `/opt/changerail`; lifecycle commands are `/changerail:*`; Codex skills are
  `$changerail-*`; helper wrappers use `bin/changerail-*`; runtime evidence
  uses `.runtime/changerail`; public schema ids use `changerail.*.v1`.
- Pinned OpenSpec CLI bumped `1.3.0` -> `1.3.1`. `skills/openspec-*` were
  refreshed with `openspec update` (all lifecycle skills preserved; sharper
  `contextFiles` guidance in apply-change/verify-change). Not breaking.

### Required Actions

For operators maintaining the source checkout:

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

For consumers whose `bin/openspec` symlinks into `/opt/changerail`: none — they pick
up `1.3.1` automatically. Re-run verification to confirm:

```bash
/opt/changerail/bin/verify-project /opt/example-project
```

Consumers that keep a local `openspec-*` copy (not a symlink into ChangeRail) can
refresh it to `1.3.1` with `openspec update` in that project, or switch to the
ChangeRail symlink to track the pin centrally.

### Rollback

Override the pin for one command without changing the wrapper:

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
