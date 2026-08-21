## 1. Episode collection

- [ ] 1.1 Add RED metrics fixtures for preflight-only, one-pass, blocked/resumed,
  multiple review rescue, abandoned recovery and same-card unrelated episodes.
- [ ] 1.2 Implement schema-valid episode collection with deterministic fallback
  from explicit-lineage owner artifacts and isolated legacy run rows.
- [ ] 1.3 Remove card-id-only review joins and surface missing/conflicting
  lineage as explicit diagnostics/unknown fields.

## 2. Episode rollup

- [ ] 2.1 Derive final outcome only from linked terminal/publish owners and
  exclude preflight-only episodes from delivery and review-rate denominators.
- [ ] 2.2 Roll up attempt/recovery counts, wall/active/wait/operator-wait time,
  usage and complete command/tool aggregates without double-counting attempt
  ids.
- [ ] 2.3 Preserve unknown versus zero and report sampling limits/truncation for
  long runs.

## 3. Output compatibility

- [ ] 3.1 Add episode rows to text and JSON output, one-row-per-episode CSV and
  explicit attempt-detail mode while retaining bounded legacy fields.
- [ ] 3.2 Update queue summaries to expose linked episode/attempt counts without
  reading child logs.
- [ ] 3.3 Document changed denominators, legacy behavior and output migration.

## 4. Verification

- [ ] 4.1 Run `python3 scripts/smoke-delivery-metrics.py` and observe all episode,
  denominator, legacy, truncation and unknown fixtures pass.
- [ ] 4.2 Run `python3 scripts/smoke-contract-schemas.py` and observe metrics
  inputs remain schema-valid.
- [ ] 4.3 Run `bin/openspec validate --all --strict`, `git diff --check` and
  `python3 scripts/public-surface-scan.py`; record concise outcomes without
  tracking runtime reports.
