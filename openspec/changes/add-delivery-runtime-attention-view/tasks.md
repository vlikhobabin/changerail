## 1. Status Reader CLI

- [ ] 1.1 Add `bin/changerail-delivery-runner status` argument parsing with
  explicit path, `--run-id`, latest workspace selection, `--workspace`,
  `--runtime-root` and `--json`.
- [ ] 1.2 Implement selector validation so conflicting selectors, missing
  latest records, missing files, corrupt JSON and schema-invalid
  `changerail.delivery-run.v1` inputs fail closed.
- [ ] 1.3 Implement compact human-readable output for card, phase, result,
  `updated_at`, `terminal_reason` and selected status path.
- [ ] 1.4 Derive canonical manifest, review verdict, review history and
  evidence paths from the validated status card/workspace, validate existing
  linked artifacts and render manifest `runtime_pause_reasons` summaries and
  `next_action` values without raw-log inference.
- [ ] 1.5 Ensure the command is read-only by avoiding writes to board files,
  locks, manifests, verdicts, evidence indexes, logs and status records.

## 2. Documentation

- [ ] 2.1 Update `docs/changerail-contracts.md` with the single-card
  `status` command, selection modes, fail-closed validation and JSON source
  record behavior.
- [ ] 2.2 Update `docs/how-it-works.md` to distinguish single-card
  `status` from aggregate `status-plan`.

## 3. Smoke Coverage

- [ ] 3.1 Extend `scripts/smoke-delivery-runner.py` with synthetic fixtures for
  explicit status-path success, `--run-id` or latest selection and blocked or
  no-go diagnostics.
- [ ] 3.2 Add smoke coverage for manifest `runtime_pause_reasons` rendering
  and corrupt or unsupported status failure.
- [ ] 3.3 Add a read-only assertion that selected status and linked runtime
  artifact content is unchanged after status inspection.

## 4. Verification

- [ ] 4.1 Run `python3 -m py_compile bin/changerail-delivery-runner
  scripts/smoke-delivery-runner.py`.
- [ ] 4.2 Run `python3 scripts/smoke-delivery-runner.py`.
- [ ] 4.3 Run
  `./bin/openspec validate add-delivery-runtime-attention-view --strict`.
- [ ] 4.4 Run `./bin/openspec validate --all --strict`.
- [ ] 4.5 Run `git diff --check`.
- [ ] 4.6 Run an untracked-file trailing-whitespace scan over
  `git ls-files --others --exclude-standard`.
- [ ] 4.7 Run `python3 scripts/public-surface-scan.py`.
