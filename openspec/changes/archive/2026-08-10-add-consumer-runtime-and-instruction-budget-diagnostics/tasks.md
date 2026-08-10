## 1. Instruction Budget

- [x] 1.1 Render explicit `project_doc_max_bytes = 32768` in consumer Codex
  config and keep the default generated `AGENTS.md` below 85 percent.
- [x] 1.2 Add UTF-8 byte measurement and pass/warn/fail severity to
  `verify-project` with measured budget and remediation.
- [x] 1.3 Add below-threshold, 85-percent boundary and over-budget fixtures that
  fail against the current no-budget behavior before implementation.

## 2. Runtime Diagnostic Adapter

- [x] 2.1 Add explicit `--runtime-diagnostics` orchestration with supported
  version-aware structured Codex probes and no default network/runtime call.
- [x] 2.2 Store raw outputs under ignored diagnostics state and emit allowlisted
  redacted summaries separated from static verification.
- [x] 2.3 Add unsupported command/schema, wrong `CODEX_HOME`, local-path and
  credential-redaction negative fixtures.

## 3. Templates And Docs

- [x] 3.1 Update generated guidance to distinguish static PASS, runtime evidence
  and ignored raw output.
- [x] 3.2 Update compatibility/adoption docs with supported probe versions,
  instruction budget and remediation policy.

## 4. Verification

- [x] 4.1 Run focused budget/runtime diagnostics smoke and
  `python3 scripts/smoke-verify-project.py` and observe all fixtures pass.
- [x] 4.2 Run `python3 scripts/run-release-baseline.py` and observe the full
  baseline pass without requiring runtime diagnostics.
- [x] 4.3 Run `./bin/openspec validate --all --strict`, current/history
  public-surface scans and `git diff --check`.
