## 1. Runner Capture

- [x] 1.1 Add runner-side JSONL event observation with bounded performance summary data.
- [x] 1.2 Extract command start/end events into command count, duration and slow-command summaries.
- [x] 1.3 Populate available event counts, agent message count, file-change count, review timing and publish timing in status records.

## 2. Regression Coverage

- [x] 2.1 Extend `scripts/smoke-delivery-runner.py` with a fake child that emits multiple command lifecycle events.
- [x] 2.2 Assert runner status includes measurable command durations and preserves terminal outcome behavior.

## 3. Specs And Verification

- [x] 3.1 Sync delta specs into `openspec/specs/changerail-delivery-runner/spec.md` and `openspec/specs/changerail-delivery-observability/spec.md`.
- [x] 3.2 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 3.3 Run `./bin/openspec validate capture-delivery-run-performance --strict`.
- [x] 3.4 Run `git diff --check`.
