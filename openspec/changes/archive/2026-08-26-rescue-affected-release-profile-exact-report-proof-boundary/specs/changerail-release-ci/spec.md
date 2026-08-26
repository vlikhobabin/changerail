## ADDED Requirements

### Requirement: Exact report/proof rescue MUST replace terminal unpublished affected paths
ChangeRail MUST publish
`rescue-affected-release-profile-exact-report-proof-boundary` as one docs-only
decision from exact published `authorize-bounded-affected-release-profile-v1`
commit `cd5393a643b7b0e8f9ea83574945b837aa4089e8`.

The unpublished `implement-bounded-affected-release-profile-v1` and unpublished
`rescue-affected-release-profile-closed-validation-boundary` paths MUST be
terminal, non-conforming and forensic-only. Their payloads, cards, manifests,
verdicts, logs and evidence MUST NOT satisfy any dependency, authorization,
implementation, review or publication gate. Published cards and archives MUST
remain unchanged.

The only conforming order MUST be this decision, docs-only
`authorize-bounded-affected-release-profile-v2`, clean
`implement-bounded-affected-release-profile-v2`, then
`certify-accelerated-release-loop-v1`. The v2 authorization MUST contain exactly
one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-exact-report-proof-boundary.md","investigation_id":"rescue-affected-release-profile-exact-report-proof-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v2.md","successor_id":"implement-bounded-affected-release-profile-v2","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`rescue-affected-release-profile-exact-report-proof-boundary`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v1`. It MUST block only
`implement-bounded-affected-release-profile-v2`.

The v2 implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v2.md","authorization_id":"authorize-bounded-affected-release-profile-v2"}
```

Its `Depends On` relation MUST contain exactly those four published predecessors
plus `authorize-bounded-affected-release-profile-v2`; it MUST block only
`certify-accelerated-release-loop-v1`; it MUST start from the
authorization-publishing HEAD, add at most 499 production LOC and reconstruct
from published sources without copying or cherry-picking terminal work.

#### Scenario: Rescue leaves one published-source successor path
- **WHEN** maintainers publish this decision
- **THEN** both unpublished predecessor paths are exhausted and exact v2 lineage is exclusive
- **AND** authorization, implementation and certification successors remain absent.

### Requirement: Affected v2 MUST preserve admission and non-authority boundaries
Future v2 MUST preserve exact 35-ID registry/digest, complete 35→30 physical
resolution, bounded aggregate NUL Git selector, rename/copy old+new operands,
sole scheduler v1 activation and full-only authority without changing published
broker/scheduler supervision or cleanup.

Both requested profiles MUST complete one aggregate bounded effective-PATH
admission before Git selection and before any semantic scheduler call. Admission
MUST verify Python `>=3.11`, exact requirement pins and installed origins, Ruff
`0.6.9` from the selected environment, Git/repository identity, Node/npm/npx,
pinned OpenSpec `1.3.1` offline and every registry target. Any admission fault
MUST return one bounded aggregate failure with `semantic_started: 0` and MUST
launch no semantic task.

Requested affected MUST remain `authoritative:false` for subset success and
full fallback. Only admitted requested full-release with exact complete pass MAY
be authoritative. V2 MUST create and accept no receipt, capture, marker or
cache. Review, publish and certification gates MUST reject affected/focused
output and every forged or replayed protocol artifact as full evidence.

#### Scenario: Admission or protocol uncertainty cannot authorize
- **WHEN** admission fails, affected falls back, or receipt/capture/marker/cache material appears
- **THEN** semantic launch is zero on admission failure and authority remains false
- **AND** no protocol artifact can upgrade affected or focused output.

### Requirement: Affected v2 MUST validate exact scheduler summaries and rows
At the runner trust boundary, a scheduler summary MUST have exactly fields
`version`, `status`, `jobs`, `results`; version MUST equal
`changerail.release-semantic-scheduler.v1`; jobs MUST equal requested `1` or
`4`; results MUST contain every planned physical ID exactly once in registry
order. Summary status MUST be exactly `pass` if all rows have status `pass` and
MUST be exactly `fail` otherwise.

Every row MUST have exactly `id`, `status`, `reason`, `returncode`,
`output_bytes`, `cleanup_complete`, `messages`. Return code MUST be null or an
exact integer and MUST NOT be boolean; output and messages MUST be exact
non-negative integers, not booleans, within `0..8193` and `0..3`; cleanup MUST
be boolean; reason MUST be bounded ASCII. Each row MUST satisfy exactly one:

- pass MUST be status `pass`, reason `completed`, return code `0`, output
  `0..8192`, cleanup `true`, messages `3`;
- `child_failed` MUST be status `fail`, nonzero integer return code, output
  `0..8192`, cleanup `true`, messages `3`;
- `execution_timeout` MUST be status `fail`, integer return code, output
  `0..8192`, cleanup `true`, messages `3`;
- `output_limit` MUST be status `fail`, integer return code, output `8193`,
  cleanup `true`, messages `3`;
- `cleanup_incomplete` MUST be status `fail`, null or integer return code,
  output `0..8193`, cleanup `false`, messages `3`;
- `internal_error` MUST be status `fail`, null or integer return code, output
  `0..8192`, boolean cleanup, messages `3`;
- `protocol_error`, `broker_lost`, `outer_timeout` or `outer_cleanup_error` MUST
  be status `fail`, null or integer return code, output `0`, cleanup `false`,
  messages `0..2`;
- `supervisor_result_error`, `supervisor_error` or `executor_error` MUST be
  status `fail`, null return code, output `0`, cleanup `false`, messages `0`;
- `cancelled` MUST be status `fail`, null return code, output `0`, cleanup
  `true`, messages `0`.

Missing/extra fields, unknown reasons, invalid cross-fields, wrong summary
status, missing/duplicate/unknown/reordered/cross-ID rows and canonical JSON over
64 KiB MUST fail terminal and MUST NOT authorize full release.

#### Scenario: Every non-all-pass summary is exact fail
- **WHEN** any terminal, outer or synthetic row occurs or any row/schema invariant fails
- **THEN** summary status is exactly `fail` and release authority is false
- **AND** a failure row can never claim status `pass` or another status.

### Requirement: Affected v2 MUST validate the exact canonical CI schema
Canonical CI MUST parse YAML without YAML 1.1 key coercion. Its top-level field
set MUST be exactly `{name, on, permissions, jobs}` with name `ChangeRail CI`,
trigger map keys exactly `push`, `pull_request`, `workflow_dispatch` and each
trigger value exactly null, permissions exactly `{contents: read}`, and only
job `verify`.

The verify-job field set MUST be exactly `{name, runs-on, steps}` with name
`Verify ChangeRail release gates` and `runs-on: ubuntu-latest`. It MUST contain
exactly these ordered steps and no others:

1. fields `{name, uses, with}`, name `Check out repository`,
   `uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5`,
   `with: {fetch-depth: "0"}`;
2. fields `{name, uses, with}`, name `Set up Node.js for OpenSpec wrapper`,
   `uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020`,
   `with: {node-version: "20"}`;
3. fields `{name, run}`, name `Prepare offline release dependencies`, and exact
   run scalar:

```text
python3 -m venv .runtime/changerail/ci-venv
.runtime/changerail/ci-venv/bin/python -m pip install --disable-pip-version-check -r requirements-dev.txt
echo "$PWD/.runtime/changerail/ci-venv/bin" >> "$GITHUB_PATH"
./bin/openspec --version >/dev/null
```

4. fields `{name, run}`, name `Run canonical full release`, and exact run
   `python3 scripts/run-release-baseline.py --profile full-release`.

Any other top-level/job/step field, job, trigger/value, permission, action,
`with` key/value, run, order or step; workflow/job/step `env`; strategy/matrix;
condition; continue-on-error; timeout; shell; working-directory; wrapper;
chain; indirect runner; affected, scheduler, broker or individual semantic
command MUST fail the parsed ownership oracle.

#### Scenario: CI schema mutation cannot preserve authority
- **WHEN** any top-level, job, trigger, permission, action, with-map, run, field, order or gating value changes
- **THEN** the parsed CI oracle fails even if the canonical runner text remains
- **AND** no alternate execution surface can satisfy canonical full release.

### Requirement: Affected v2 MUST retain exhaustive connected counterfactual proof
Disposable focused scheduler fixtures MUST enumerate every valid row tuple and
mutate each status/reason/return-code/output/cleanup/message cross-field,
top-level field/version/jobs/status, summary size, result count, identity,
order, missing/extra/duplicate/unknown/cross-ID row. Protocol fixtures MUST add,
forge and replay receipt, capture, marker and cache artifacts and prove none can
change authority.

CI fixtures MUST mutate every exact top-level and verify-job field set/name,
each trigger key/value, permission, action SHA, `with` map, step name/field/order,
run scalar, workflow/job/step env, extra job/uses/run, one/multiple matrix,
condition, continue-on-error, timeout, shell/working-directory and direct,
chained, wrapped or indirect execution surface.

The preserved selector/admission/authority floor MUST cover Git A/M/D/R/C
old+new operands, staged/unstaged/untracked aggregation, base/framing/status/
path/count/per-path/aggregate/stderr/nonzero/timeout/self/unknown fallbacks,
zero semantic launch for every admission fault, zero-argument/full parity,
exact full authority and affected subset/full-fallback non-authority. Every
mutation MUST assert it changed the fixture and MUST fail if its corresponding
guard is weakened.

#### Scenario: No-op or disconnected fixture cannot count
- **WHEN** a fixture misses a row/protocol/CI/selector/admission/authority branch or mutates the wrong surface
- **THEN** the required proof remains incomplete
- **AND** no no-op mutation or tautological assertion is accepted.

### Requirement: Exact report/proof rescue MUST remain docs-only
This decision MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC 0 and MUST NOT create successor cards,
code, dependencies, schemas, CI or runtime authority.

It MUST NOT run or accept reachable history, real full baseline, affected
benchmark, live matrix, certification or unpublished prototype evidence. One
fresh Sol/high review and one same-card docs repair are available.

#### Scenario: Decision cannot claim executable closure
- **WHEN** this decision is delivered or reviewed
- **THEN** only lineage and exact future trust boundaries change
- **AND** executable closure remains absent until separately published v2 work.
