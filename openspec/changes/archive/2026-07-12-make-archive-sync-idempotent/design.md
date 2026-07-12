# Design: archive duplicate sync diagnostics

The OpenSpec implementation is executed via pinned `npx` package from the
tracked `bin/openspec` wrapper. ChangeRail does not vendor the package source,
so the low-risk change is wrapper-level detection of the known abort signature:

```text
ADDED failed for header "### Requirement: ..." - already exists
Aborted. No files were changed.
```

The wrapper will run the package normally, capture output only for
`archive` invocations, replay output, and when that signature appears without
`--skip-specs`, return a non-zero status with a diagnostic that recommends
rerunning with `--skip-specs` after confirming main specs were intentionally
synced.

This preserves normal OpenSpec behavior and avoids pretending that duplicate
sync can always be auto-merged safely.
