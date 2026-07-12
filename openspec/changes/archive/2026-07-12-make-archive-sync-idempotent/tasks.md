## 1. Wrapper Behavior

- [x] 1.1 Update `bin/openspec` to detect duplicate already-synced archive aborts.
- [x] 1.2 Keep normal non-archive and `--skip-specs` archive behavior delegated
  to the pinned OpenSpec CLI.

## 2. Smoke Coverage

- [x] 2.1 Add a smoke that creates a temporary duplicate requirement archive
  scenario and expects a non-zero diagnostic without `--skip-specs`.
- [x] 2.2 Verify that the diagnostic names `--skip-specs`.

## 3. Verification

- [x] 3.1 Run the new archive diagnostic smoke.
- [x] 3.2 Run `./bin/openspec validate "make-archive-sync-idempotent" --strict`.
- [x] 3.3 Run `./bin/openspec validate --all --strict`.
- [x] 3.4 Run `git diff --check`.

## Verification Notes

- `bash -n bin/openspec` passed.
- `python3 scripts/smoke-openspec-archive-diagnostics.py` passed with
  `SMOKE_OPENSPEC_ARCHIVE_DIAGNOSTICS_OK`.
- `./bin/openspec validate make-archive-sync-idempotent --strict` passed.
- `./bin/openspec validate --all --strict` passed with 18 items before archive.
- `git diff --check` passed.
