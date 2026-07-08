# Migration Guide

Этот документ описывает migration notes между версиями OPSX. Записи должны
быть public-safe: только generic paths, без private workspace names,
credentials, traces или machine-local inventory.

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
