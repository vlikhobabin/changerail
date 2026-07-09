# Migration Guide

Этот документ описывает migration notes между версиями OPSX. Записи должны
быть public-safe: только generic paths, без private workspace names,
credentials, traces или machine-local inventory.

## Unreleased

### What Changed

- Pinned OpenSpec CLI bumped `1.3.0` -> `1.3.1`. `skills/openspec-*` were
  refreshed with `openspec update` (all lifecycle skills preserved; sharper
  `contextFiles` guidance in apply-change/verify-change). Not breaking.

### Required Actions

For consumers whose `bin/openspec` symlinks into `/opt/opsx`: none — they pick
up `1.3.1` automatically. Re-run verification to confirm:

```bash
/opt/opsx/bin/verify-project /opt/example-project
```

Consumers that keep a local `openspec-*` copy (not a symlink into OPSX) can
refresh it to `1.3.1` with `openspec update` in that project, or switch to the
OPSX symlink to track the pin centrally.

### Rollback

Override the pin for one command without changing the wrapper:

```bash
OPENSPEC_VERSION=1.3.0 /opt/opsx/bin/openspec validate --all --strict
```

## 0.1.0

Initial public baseline.

### From

No earlier public OPSX release.

### What Changed

- OPSX source of truth documented under `/opt/opsx`.
- Generic lifecycle skills and Claude command wrappers are present.
- OpenSpec lifecycle skills are present.
- Project bootstrap, verify-project, drift gate and wiring smoke are present.
- Release discipline docs are introduced.

### Required Actions

For a new consumer project:

```bash
/opt/opsx/bin/bootstrap-project /opt/example-project \
  --name example-project \
  --kind generic
```

For an already wired consumer project:

```bash
/opt/opsx/bin/verify-project /opt/example-project
```

For workspace-level drift:

```bash
python3 /opt/opsx/scripts/smoke-drift.py \
  --config /opt/opsx/internal/opsx-drift.json
```

Keep the inventory in ignored operator-controlled space such as `internal/`.

### Rollback

Return `/opt/opsx` to the previous commit/tag and rerun project-local
verification:

```bash
/opt/opsx/bin/verify-project /opt/example-project
```

Because `0.1.0` is the initial public baseline, rollback target is the
operator's previous local checkout.
