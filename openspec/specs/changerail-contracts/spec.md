# changerail-contracts Specification

## Purpose
Зафиксировать публичные wire contracts ChangeRail для review, delivery и evidence
handoff, а также helper-поведение для review-verdict validation и freshness
fingerprint/reviewed-tree identity.
## Requirements
### Requirement: ChangeRail contract schemas
ChangeRail MUST provide tracked JSON schemas for review verdict, delivery manifest
and evidence index contracts using canonical `changerail.*` schema ids.

#### Scenario: Maintainer inspects contract schemas
- **WHEN** the `schemas/` directory is listed
- **THEN** schemas exist for `changerail.review-verdict.v1`,
  `changerail.delivery-manifest.v1` and `changerail.evidence-index.v1`

### Requirement: Repository knowledge contract schemas
ChangeRail MUST provide tracked JSON schemas for repository knowledge catalog and
maintenance policy contracts using canonical `changerail.*` schema ids.

#### Scenario: Maintainer inspects repository knowledge schemas
- **WHEN** the `schemas/` directory is listed
- **THEN** schemas exist for `changerail.repository-knowledge.v1` and `changerail.maintenance-policy.v1`

#### Scenario: Contract schema smoke covers repository knowledge schemas
- **WHEN** `python3 scripts/smoke-contract-schemas.py` runs
- **THEN** the smoke validates representative valid and invalid documents for both schema ids

### Requirement: Review verdict helper validation
ChangeRail MUST provide a review-verdict helper that validates verdict shape,
cross-field consistency and optional HEAD, reviewed-tree and working-tree
freshness.

#### Scenario: Publish checks a verdict before staging
- **WHEN** publish validates `.runtime/changerail/reviews/<card-id>.json` with
  `--check-fresh`
- **THEN** validation fails unless the verdict schema is
  `changerail.review-verdict.v1`, the result is internally consistent and the
  recorded head commit, reviewed tree SHA and diff fingerprint match the current
  working tree

### Requirement: Review independence attestation
Review verdicts MUST include a machine-checkable reviewer independence
attestation that states whether the reviewer used a fresh context and did not
plan or implement the reviewed payload.

#### Scenario: Reviewer writes a go verdict
- **WHEN** a reviewer writes `.runtime/changerail/reviews/<card-id>.json`
- **THEN** the `reviewer` object includes an independence attestation with
  `fresh_context: true`, `did_not_plan_or_implement: true` and a non-empty
  basis

#### Scenario: Publish validates a verdict without attestation
- **WHEN** `bin/changerail-review-verdict validate --check-fresh` checks a
  verdict whose reviewer independence attestation is missing or false
- **THEN** validation fails before publish can stage files

### Requirement: Independence limits are explicit
Review verdict docs MUST state that helper validation checks reviewer
attestation and working-tree freshness, but cannot by itself prove the real
identity or full memory boundary of an external agent session.

#### Scenario: Maintainer reads review contract docs
- **WHEN** a maintainer reads the review verdict reference
- **THEN** the document distinguishes machine-checked attestation from
  operator-enforced session independence

### Requirement: Review verdict fingerprint
ChangeRail MUST provide a deterministic helper command that computes the review
freshness fingerprint and reviewed tree SHA from git HEAD, status, tracked diff
and untracked non-ignored file content. The helper MUST compute the exact
reviewed tree from a machine-readable changed path set without a full-index
refresh when Git can represent the current workspace changes safely.

#### Scenario: Reviewer writes a verdict
- **WHEN** reviewer runs `bin/changerail-review-verdict fingerprint --workspace .`
- **THEN** the helper emits JSON containing the current head commit and
  `sha256:<hex>` diff fingerprint
- **AND** it emits a 40-hex `tree_sha` for the exact reviewed tree

#### Scenario: Untracked deliverable content changes
- **WHEN** an untracked non-ignored file's content changes without changing its
  path
- **THEN** the helper emits a different `sha256:<hex>` diff fingerprint
- **AND** it emits a different `tree_sha`

#### Scenario: Ignored runtime content changes
- **WHEN** an ignored file such as `.runtime/changerail/reviews/<card-id>.json` is
  added or changed
- **THEN** the helper emits the same `sha256:<hex>` diff fingerprint for the
  otherwise unchanged working tree
- **AND** it emits the same `tree_sha`

#### Scenario: Publish detects reviewed tree drift
- **WHEN** `bin/changerail-review-verdict validate --check-fresh` checks a
  verdict whose `workspace.tree_sha` differs from the current reviewed tree
- **THEN** validation fails before publish can stage files

#### Scenario: Docs-only payload avoids full-index refresh
- **WHEN** a large repository has a docs-only working-tree payload and Git
  reports an exact changed path set
- **THEN** the helper computes the reviewed tree by applying only that changed
  path set to a temporary index
- **AND** it does not run full-repository `git add -A` for the happy path

#### Scenario: Optimized tree matches reference tree for path edge cases
- **WHEN** the workspace contains additions, modifications, deletions, renames,
  symlinks, Unicode paths, spaces, literal ` -> ` text or valid non-UTF-8 Linux
  paths
- **THEN** the optimized reviewed-tree builder emits the same `tree_sha` and
  `diff_fingerprint` as the reference full-tree algorithm

#### Scenario: Unsafe path state does not produce approximate freshness
- **WHEN** Git reports a changed path set that the optimized builder cannot
  represent exactly
- **THEN** the helper either uses the reference full-tree algorithm or exits
  non-zero before emitting freshness data

### Requirement: Review fingerprint cost measurement
ChangeRail MUST provide public-safe measurement for deterministic review
fingerprint and review preflight phases without changing the canonical
freshness values.

#### Scenario: Operator measures review fingerprint phases
- **WHEN** an operator runs the review fingerprint measurement surface for a
  workspace
- **THEN** the result lists separate durations for changed path discovery,
  reviewed-tree construction, untracked non-ignored content hashing and final
  fingerprint assembly
- **AND** the result includes the same `head_commit`, `tree_sha` and
  `diff_fingerprint` values as the canonical fingerprint command for the same
  workspace state

#### Scenario: Preflight measurement separates non-fingerprint gates
- **WHEN** review preflight runs with measurement enabled
- **THEN** the result lists fingerprint, OpenSpec validation, scoped whitespace
  check and public-surface scan durations as distinct phases
- **AND** failed checks continue to fail closed with their existing check ids

### Requirement: Synthetic large-repository fingerprint benchmark
ChangeRail MUST include focused benchmark coverage for review fingerprint cost
using synthetic public-safe repositories.

#### Scenario: Benchmark compares docs-only and source payloads
- **WHEN** the benchmark smoke runs
- **THEN** it creates a synthetic repository with many generic tracked files
- **AND** it records docs-only and source-payload timings before deleting the
  temporary repository
- **AND** it does not write private consumer paths, raw field-validation logs or
  generated repository contents to tracked files

#### Scenario: Benchmark threshold is derived from fixture behavior
- **WHEN** maintainers inspect the benchmark configuration
- **THEN** the threshold is based on the measured synthetic baseline and fixture
  size
- **AND** it does not depend on a specific consumer repository identity

### Requirement: Canonical review fingerprint consumers
ChangeRail MUST use one canonical review fingerprint implementation for review
preflight, review verdict freshness validation and publish gate freshness
checks.

#### Scenario: Review gates observe the same payload identity
- **WHEN** review preflight, `bin/changerail-review-verdict validate --check-fresh`
  and the publish gate run against the same workspace state
- **THEN** they observe identical `head_commit`, `tree_sha` and
  `diff_fingerprint` values
- **AND** a mismatch in any of those values continues to fail publish before
  staging

#### Scenario: Canonical implementation changes
- **WHEN** the review fingerprint implementation is updated
- **THEN** review preflight, verdict validation and publish freshness checks use
  the updated implementation without maintaining divergent freshness logic

### Requirement: Validated review fingerprint cache
ChangeRail MUST validate ignored runtime review fingerprint cache entries before
reuse. It MAY reuse them only when cheap current workspace checks prove the
cache binds the exact current payload, and MUST fail closed or recompute before
emitting freshness values when that proof is unavailable.

#### Scenario: Repeated unchanged preflight reuses cache
- **WHEN** review preflight runs twice for an unchanged workspace
- **THEN** the second run may reuse a cache entry whose HEAD and changed path
  metadata match the current workspace
- **AND** the reused result includes the same reviewed `tree_sha` and
  `diff_fingerprint` as a full canonical recomputation

#### Scenario: Workspace change invalidates cache
- **WHEN** tracked content, tracked path state, untracked non-ignored content or
  Git exclude behavior changes after a cache entry is written
- **THEN** the next freshness check recomputes the canonical fingerprint before
  emitting `tree_sha` or `diff_fingerprint`

#### Scenario: Cache remains ignored runtime state
- **WHEN** cache entries are written
- **THEN** they live under ignored `.runtime/changerail/` state
- **AND** tracked cards, manifests, specs and docs do not store cache payloads

#### Scenario: Malformed cache fails closed
- **WHEN** a cache entry is unreadable, malformed or missing required freshness
  fields
- **THEN** the helper ignores it or exits non-zero
- **AND** it does not emit approximate freshness data from the malformed entry

### Requirement: Delivery manifest file operations
Delivery manifests MUST represent card-owned file operations well enough for
publish to build a complete staging proposal for additions, modifications,
deletions and renames.

#### Scenario: Board card move is claimed completely
- **WHEN** a card moves from one board column path to another
- **THEN** the manifest records the source path and target path or equivalent
  structured operation data so publish can stage both sides of the move

#### Scenario: Deleted path remains in scope
- **WHEN** delivery removes a card-owned tracked file
- **THEN** the manifest records the deleted path as a committable path instead
  of only recording remaining files

### Requirement: Delivery manifest derivation helper
ChangeRail MUST provide a helper command that can derive a delivery manifest
from a board card and the current workspace state.
Delivery manifest derivation MUST sanitize repository identity before writing it
to runtime records.

#### Scenario: Delivery derives a card manifest
- **WHEN** an operator runs the manifest helper for a board card
- **THEN** the helper derives card id, card path, card status, ordered changes,
  archived change paths and dirty committable paths
- **AND** it excludes ignored runtime verdict and manifest paths from
  `committable_paths`

#### Scenario: Reviewer inspects derived staging plan
- **WHEN** a derived manifest is passed to `staging-plan`
- **THEN** the output is a deterministic list of repository-relative paths that
  can be audited before publish staging

#### Scenario: Manifest redacts credential-bearing repository identity
- **WHEN** delivery manifest derivation reads an HTTPS remote containing URL
  userinfo, password or token-like query values
- **THEN** the manifest repository identity excludes raw userinfo, password,
  query and fragment values
- **AND** the identity retains non-sensitive scheme, host and repository path
  metadata when available

#### Scenario: Manifest redacts SCP-style SSH userinfo
- **WHEN** delivery manifest derivation reads an SCP-style SSH remote such as
  `user@example.invalid:org/repo.git`
- **THEN** the manifest repository identity excludes the raw SSH username
- **AND** it retains non-sensitive host and repository path metadata

### Requirement: Точный вывод delivery manifest paths
Delivery manifest derivation MUST использовать machine-readable git status data
и MUST записывать точные repository-relative paths для card-owned additions,
modifications, deletions и renames без shell quoting artifacts.

#### Scenario: Manifest точно записывает допустимые символы path
- **WHEN** manifest derivation видит changed paths со spaces, quotes, Unicode
  characters или literal ` -> ` text
- **THEN** `committable_paths` записывает repository-relative paths без
  добавленных quotes, lossy splitting или arrow-based rewrite

#### Scenario: Manifest сохраняет non-UTF-8 path bytes
- **WHEN** manifest derivation видит repository path с valid non-UTF-8 bytes в
  Linux workspace
- **THEN** JSON output остается valid UTF-8 и сохраняет path так, что
  filesystem byte round-trip через `os.fsencode` восстанавливает исходные bytes

#### Scenario: Manifest записывает source и target для rename
- **WHEN** manifest derivation видит card-owned rename
- **THEN** manifest записывает `operation: rename`, `source_path` и
  `target_path`

#### Scenario: Manifest записывает deleted path
- **WHEN** manifest derivation видит card-owned delete
- **THEN** manifest записывает `operation: delete` и `source_path` для removed
  path

### Requirement: Консервативный untracked manifest scope
Delivery manifest derivation MUST NOT включать directory-wide untracked path в
`committable_paths`, когда такой path может stage-ить unrelated files.

#### Scenario: Untracked directory содержит несколько files
- **WHEN** manifest derivation видит untracked files в одном directory
- **THEN** `committable_paths` содержит каждый точный file path вместо parent
  directory

#### Scenario: Untracked path нельзя безопасно перечислить
- **WHEN** manifest derivation не может представить untracked directory или
  non-regular path как точные file paths
- **THEN** helper validation завершается fail до записи staging proposal

### Requirement: Delivery manifest scope reconciliation
Delivery manifest helpers MUST provide a schema-backed `scope-check` command
that compares manifest `committable_paths` with actual Git scope for the
working tree, the staged index or both targets.

#### Scenario: Working-tree scope matches manifest
- **WHEN** `bin/changerail-delivery-manifest scope-check --target working-tree --json` checks a manifest whose committable operations match the current non-ignored working-tree status
- **THEN** the helper exits zero
- **AND** the JSON result reports `ok: true` for the working-tree target

#### Scenario: Staged scope matches manifest
- **WHEN** `bin/changerail-delivery-manifest scope-check --target staged --json` checks a manifest whose committable operations match the staged index
- **THEN** the helper exits zero
- **AND** the JSON result reports `ok: true` for the staged target

#### Scenario: Manifest scope has missing, extra and mismatched paths
- **WHEN** scope reconciliation finds a path claimed by the manifest but absent from the target, a target path absent from the manifest or a path whose operation differs
- **THEN** the helper exits non-zero
- **AND** the JSON result lists those differences under `missing`, `extra` and `mismatched` entries for the checked target

#### Scenario: Runtime paths are excluded from committable scope
- **WHEN** ignored runtime manifest, verdict or review-history paths exist during scope reconciliation
- **THEN** the helper excludes those paths from actual committable scope
- **AND** it does not require runtime paths to appear in `committable_paths`

### Requirement: Delivery manifest helper has a consumer-stable wrapper
ChangeRail MUST expose delivery manifest operations through the tracked
`bin/changerail-delivery-manifest` wrapper and bootstrap that wrapper into
consumer repositories.

#### Scenario: Consumer skill invokes manifest operations
- **WHEN** a wired consumer runs `bin/changerail-delivery-manifest validate`
- **THEN** the wrapper resolves the owning ChangeRail checkout
- **AND** it executes the canonical manifest helper through the shared Python
  runtime without requiring a consumer-local `scripts/` copy

### Requirement: NUL-safe operation-aware scope comparison
Delivery manifest scope reconciliation MUST use machine-readable NUL-delimited
Git data and MUST compare add, modify, delete and rename operations without
lossy path parsing.

#### Scenario: Scope contains add modify delete and rename operations
- **WHEN** a manifest and target Git state contain additions, modifications, deletions and renames
- **THEN** scope reconciliation compares each operation type explicitly
- **AND** rename comparison uses source and target paths rather than a
  human-formatted arrow string

#### Scenario: Scope contains paths requiring byte-preserving round trip
- **WHEN** a target path contains spaces, quotes, Unicode, literal arrow text or valid non-UTF-8 bytes on Linux
- **THEN** scope reconciliation preserves the repository-relative path bytes through filesystem encoding round trip
- **AND** it does not split or quote paths through shell-oriented parsing

### Requirement: Delivery manifest handoff summaries
Delivery manifests MUST support concise machine-readable handoff summaries for
verification evidence, independent review outcome and final board-card state.

#### Scenario: Delivery records verification summary
- **WHEN** delivery updates the manifest after running verification
- **THEN** the manifest can record a concise `verification_summary` containing a result, short summary text and command/evidence references
- **AND** raw command logs remain outside the manifest in ignored runtime evidence

#### Scenario: Review records handoff summary
- **WHEN** independent review writes or validates a verdict for a delivered card
- **THEN** the manifest can record a concise `review_summary` containing the verdict result, review cycle, finding counts and verdict path
- **AND** the latest canonical verdict remains `.runtime/changerail/reviews/<card-id>.json`

#### Scenario: Publish records final card state
- **WHEN** publish finalizes a reviewed board card
- **THEN** the manifest can record `final_card_state` with the final card path, status and stable result summary
- **AND** exact mutable publish details remain in the manifest publish ledger instead of tracked card text

### Requirement: Scope-check smoke coverage
ChangeRail smoke tests MUST cover delivery manifest scope reconciliation,
including negative staged-scope cases that would otherwise produce a false
green publish.

#### Scenario: Extra staged path is rejected
- **WHEN** a staged file is not listed in manifest `committable_paths`
- **THEN** the scope-check smoke observes non-zero helper output
- **AND** the diagnostic lists the staged file under `extra`

#### Scenario: Missing staged path is rejected
- **WHEN** a manifest committable path is not present in the staged index
- **THEN** the scope-check smoke observes non-zero helper output
- **AND** the diagnostic lists the manifest path under `missing`

### Requirement: Delivery manifest publish ledger
Delivery manifests MUST distinguish the reviewed payload commit from the final
published commit and MUST record final push metadata in ignored runtime state.

#### Scenario: Publish records payload and published commits
- **WHEN** `changerail-pub` commits a reviewed payload, finalizes the board card,
  amends deterministic card metadata and publishes the result
- **THEN** the delivery manifest records the original payload commit as
  `publish.payload_commit`
- **AND** it records the final pushed commit as `publish.published_commit`
- **AND** it records final remote, branch, status and push timestamp in
  `publish`

#### Scenario: Publish updates card location in manifest
- **WHEN** helper-assisted finalization moves a board card from `3.inprogress`
  to `4.done`
- **THEN** the ignored delivery manifest records the final `card.path`
- **AND** it records the final `card.status`

#### Scenario: Local-only publish records skipped push
- **WHEN** publish runs with explicit `--no-push`
- **THEN** the delivery manifest records the final committed payload state
- **AND** it records `publish.status: skipped` with a reason and local-only mode
  instead of claiming remote publication readiness

#### Scenario: Manifest validates publish ledger fields
- **WHEN** the delivery manifest helper validates a manifest containing publish
  ledger metadata
- **THEN** schema-backed validation accepts non-empty `payload_commit`,
  `published_commit`, remote, branch, status and timestamp fields
- **AND** validation fails for `publish.status: pushed` unless
  `payload_commit`, `published_commit`, remote, branch, pushed timestamp and
  status are present
- **AND** it rejects unknown publish fields or malformed date-time values

#### Scenario: Manifest validates local-only skipped publish evidence
- **WHEN** the delivery manifest helper validates a manifest with
  `publish.status: skipped`
- **THEN** validation fails unless `payload_commit`, `published_commit`,
  `reason` and `mode: local-only` are present

### Requirement: Canonical schema-backed validation для contracts
ChangeRail helper validation для delivery manifests и review verdicts MUST
валидировать указанный документ по tracked canonical Draft 2020-12 JSON Schema
до применения ChangeRail-specific semantic rules.

#### Scenario: Manifest нарушает canonical schema
- **WHEN** `scripts/changerail_delivery_manifest.py validate --json` получает
  manifest с unknown fields, invalid date-time formats, wrong nested types или
  missing conditional operation fields
- **THEN** helper завершается non-zero со structured diagnostic и не сообщает,
  что manifest valid

#### Scenario: Verdict нарушает canonical schema
- **WHEN** `scripts/changerail_review_verdict.py validate --json` получает
  verdict с unknown fields, invalid date-time formats, wrong nested types или
  malformed nested reviewer/acceptance/finding data
- **THEN** helper завершается non-zero со structured diagnostic и не сообщает,
  что verdict valid

#### Scenario: Publish freshness проверяет malformed go verdict
- **WHEN** publish валидирует malformed `go` verdict с `--check-fresh`
- **THEN** validation завершается fail до того, как freshness может разрешить
  staging

### Requirement: Contract schema validation общая для helpers и tests
Helper smoke tests для manifest и verdict validation MUST проверять тот же
schema-backed validation path, который используют CLI helpers, или включать
negative fixtures, которые падают при drift helper validation от tracked schemas.

#### Scenario: Negative fixture нарушает additionalProperties
- **WHEN** smoke fixture добавляет unknown nested field, запрещенный schema
- **THEN** соответствующий helper завершается non-zero

#### Scenario: Negative fixture нарушает date-time format
- **WHEN** smoke fixture использует non-date-time value в schema `format` field
- **THEN** соответствующий helper завершается non-zero

### Requirement: Delivery run record contract
ChangeRail MUST define a public `changerail.delivery-run.v1` contract for
machine-readable delivery run status, terminal outcomes and an optional stable
terminal reason.

#### Scenario: Runner writes status
- **WHEN** the delivery runner writes
  `<workspace>/.runtime/changerail/delivery-runs/<run-id>/status.json` by default
- **THEN** the JSON uses `changerail.delivery-run.v1` and includes card, phase,
  result, timestamps and command metadata
- **AND** the record includes `commit` when workspace `HEAD` is available

#### Scenario: Runner writes a safety-stop reason
- **WHEN** delivery terminates without publication because the pre-review fix
  budget is exhausted
- **THEN** the record contains terminal outcome `BLOCKED` and
  `terminal_reason: fix_budget_exhausted`
- **AND** aggregate queue status can preserve the same reason without parsing
  raw logs

#### Scenario: Usage is unavailable
- **WHEN** the runner cannot observe token usage from the provider output
- **THEN** the run record explicitly reports usage as unavailable instead of
  guessing values

### Requirement: Recoverable external blocker contract
`changerail.delivery-run.v1` MUST разрешать bounded объект
`changerail.external-blocker.v1` только для blocked attempt. Объект MUST
содержать run-local blocker id, known class, observation timestamp,
`retryable: true` и bounded required evidence ids/maximum age, а также MUST
отклонять prompts, values, response bodies, screenshots и raw output.

#### Scenario: Value-free blocker проходит валидацию
- **WHEN** blocked run записывает known class и normalized evidence ids без
  content-bearing fields
- **THEN** delivery-run schema validation проходит
- **AND** последующий resume может проверить policy без parsing terminal prose

#### Scenario: Secret-bearing blocker не проходит валидацию
- **WHEN** blocker metadata включает entered credential, environment value,
  response body, screen content или arbitrary project-specific reason
- **THEN** schema validation fail closed
- **AND** record не может разрешить retained resume

### Requirement: Delivery progress wire contract
`changerail.delivery-run.v1` and `changerail.delivery-plan-status.v1` MUST
support one optional `changerail.delivery-progress.v1` object with bounded
phase/stage enums, date-time heartbeat and non-negative monotonic event
counter. The object MUST reject undeclared content-bearing fields.

#### Scenario: Safe progress validates
- **WHEN** status contains known phase/stage, valid heartbeat timestamp and
  non-negative event counter
- **THEN** the applicable public schema validates the record
- **AND** aggregate status can mirror the object without semantic conversion

#### Scenario: Content-bearing progress fails validation
- **WHEN** progress contains prompts, command bodies, environment values,
  response bodies, raw log excerpts or unknown phase/stage
- **THEN** schema validation fails closed
- **AND** invalid object is not published as trusted live progress

### Requirement: Bounded progress health contract
Status contracts MUST represent progress health through bounded state,
non-negative heartbeat age and process-alive observation, without giving the
diagnostic terminal or mutation authority.

#### Scenario: Stale health is compatible with running result
- **WHEN** a schema-valid running record reports stale progress health and a
  live process
- **THEN** schema validation passes
- **AND** `result` remains `RUNNING` instead of being derived from health alone

### Requirement: Delivery run performance summary contract
ChangeRail MUST define schema-backed optional performance fields for
`changerail.delivery-run.v1` status records without weakening the required base
status contract.

#### Scenario: Runner writes performance fields
- **WHEN** a delivery runner status record includes performance data
- **THEN** the JSON remains valid against `schemas/changerail-delivery-run.schema.json`
- **AND** the record can include wall time, event counts, command counts,
  slow-command details, file-change counts, review timing and publish timing

#### Scenario: Performance data is unavailable
- **WHEN** a delivery runner cannot observe optional performance data
- **THEN** the status record remains valid without guessing those values
- **AND** the required base fields still include schema, card, phase, result,
  timestamps, command and usage availability

### Requirement: Delivery episode and attempt contracts
Runtime owner schemas MUST support explicit recovery-aware episode lineage
without making legacy records invalid.

#### Scenario: Delivery run declares an attempt
- **WHEN** a delivery-run status includes `episode.id` and a typed `attempt`
- **THEN** schema validation accepts `preflight`, `delivery` or `recovery`
  attempts with optional previous/source linkage
- **AND** legacy status records without these optional fields remain valid

#### Scenario: Review and publish owners link to the episode
- **WHEN** review-cycle history or delivery manifest publish metadata declares
  the same episode and linked attempt ids
- **THEN** schema validation accepts the owner-scoped lineage
- **AND** raw prompts, command bodies and log payloads are still not valid
  fields in those owner artifacts

### Requirement: Derived delivery episode contract
ChangeRail MUST define `changerail.delivery-episode.v1` as an ignored,
public-safe derived index over schema-valid owner artifacts.

#### Scenario: Episode index summarizes owner artifacts
- **WHEN** a delivery episode record is materialized
- **THEN** it contains typed attempt summaries, owner artifact references,
  final outcome and bounded sampling metadata
- **AND** it does not contain prompts, raw commands, MCP payloads, screenshots,
  source content or raw logs

### Requirement: Delivery run schema bounds command output metadata
The `changerail.delivery-run.v1` schema MUST allow structured command output
metadata while forbidding raw command payload copies in status records.

#### Scenario: Status contains command output metadata
- **WHEN** a delivery run record includes per-command output metadata
- **THEN** schema validation accepts non-negative stdout/stderr byte counts,
  result classification, threshold flags and truncation indicators
- **AND** the schema does not allow raw stdout or stderr payload text inside
  per-command metadata

#### Scenario: Legacy status lacks output metadata
- **WHEN** a delivery run record was produced before command output metadata
  existed
- **THEN** schema validation continues to accept the record if all pre-existing
  required fields are valid

### Requirement: Delivery run output metadata remains compact
The delivery-run contract MUST keep output amplification diagnostics bounded so
`status.json` remains a supervisor-friendly summary.

#### Scenario: Many commands exceed threshold
- **WHEN** a delivery run contains many oversized command events
- **THEN** the status record includes aggregate counts and bounded top-command
  metadata rather than every raw output payload
- **AND** ignored raw evidence paths remain outside committable scope

#### Scenario: Detail samples are truncated
- **WHEN** command or timeline detail retention is smaller than observed count
- **THEN** the status record exposes observed count, retained count, limit and
  truncation state
- **AND** aggregate command counts and durations remain based on the complete
  observed set

### Requirement: Delivery run usage breakdown contract
ChangeRail MUST allow delivery run records to expose available token usage
breakdowns while preserving explicit unknown semantics for unavailable usage.

#### Scenario: Usage breakdown is available
- **WHEN** provider output exposes cached input, uncached input, output or
  reasoning token counts
- **THEN** `changerail.delivery-run.v1` can represent those counts as
  non-negative integers under `usage`

#### Scenario: Usage total is derived downstream
- **WHEN** a status record contains input and output token counts but no
  explicit total
- **THEN** the contract allows metrics consumers to derive the display total
  without mutating the runtime record

### Requirement: Delivery run schema fixtures cover performance fields
ChangeRail contract schema validation MUST cover delivery run performance and
usage breakdown fields used by runner and metrics helpers.

#### Scenario: Positive fixture includes performance data
- **WHEN** release schema smoke validates a delivery run fixture with
  performance summary and usage breakdown fields
- **THEN** `schemas/changerail-delivery-run.schema.json` accepts the fixture

#### Scenario: Optional timing fields are absent
- **WHEN** release schema smoke validates a delivery run fixture without
  optional performance fields
- **THEN** the fixture remains valid when required base status fields are present

### Requirement: Delivery run safety-stop fallback evidence
The public delivery-run contract MUST state that `DELIVERED` is not a valid
fallback outcome when structured review-gated evidence or an unpublished card
shows that publish did not complete.

#### Scenario: Maintainer reads runner contract docs
- **WHEN** maintainer reads delivery-run contract documentation
- **THEN** the documentation says structured JSONL terminal signals are the
  preferred terminal outcome and reason source
- **AND** it says runner fallback MUST check canonical review-gated evidence
  and published card state before treating child exit `0` as `DELIVERED`

#### Scenario: Supervisor observes no-go fallback
- **WHEN** a delivery run status is written for child exit `0` without a
  terminal JSONL event but with a fresh canonical `no-go` verdict for an
  unpublished card
- **THEN** `status.json`, printed `terminal_outcome` and wrapper exit code are
  consistent with `NO-GO`

#### Scenario: Supervisor observes fix-budget safety stop
- **WHEN** a completed agent-message event contains exact terminal marker lines
  for `BLOCKED` and `fix_budget_exhausted`
- **THEN** `status.json` preserves both values and the wrapper exits non-zero
- **AND** arbitrary prose containing similar words is not authoritative

#### Scenario: Successful process leaves card unpublished
- **WHEN** child exit is `0`, no authoritative terminal signal or canonical
  review fallback exists, and the card is not uniquely published under
  `4.done`
- **THEN** the runner records `BLOCKED` with
  `terminal_reason: unpublished_card`

### Requirement: Review cycle evidence contract
ChangeRail MUST define runtime review-cycle evidence that can retain previous review
results while leaving `.runtime/changerail/reviews/<card-id>.json` as the latest
canonical publish gate verdict.

#### Scenario: Latest verdict remains canonical
- **WHEN** publish validates a review verdict
- **THEN** it continues to validate `.runtime/changerail/reviews/<card-id>.json`
  against `changerail.review-verdict.v1`

#### Scenario: Metrics reads historical cycles
- **WHEN** review-cycle evidence exists for prior cycles
- **THEN** metrics can count historical findings without modifying the latest
  canonical verdict
- **AND** each historical cycle retains finding details or an immutable
  per-cycle verdict snapshot path

### Requirement: ChangeRail contract namespace
Public machine-readable contracts MUST use the `changerail.*` schema namespace
after the product rename.

#### Scenario: Review verdict is validated
- **WHEN** the review verdict helper validates a post-rename verdict
- **THEN** the verdict schema id is `changerail.review-verdict.v1`
- **AND** verdicts using `opsx.review-verdict.v1` are treated as pre-rename
  legacy artifacts

#### Scenario: Delivery manifest is validated
- **WHEN** the delivery manifest helper validates a post-rename manifest
- **THEN** the manifest schema id is `changerail.delivery-manifest.v1`

### Requirement: ChangeRail schema filenames
Tracked schema filenames MUST use the `changerail-*.schema.json` prefix after
the rename.

#### Scenario: Maintainer lists schemas
- **WHEN** a maintainer lists the tracked schema directory
- **THEN** review verdict, delivery manifest, evidence index, delivery run and
  review cycle history schemas use `changerail-*.schema.json` filenames

### Requirement: Delivery plan contract
ChangeRail MUST define a public schema-backed `changerail.delivery-plan.v1`
contract for declarative multi-workspace delivery queue plans.

#### Scenario: Maintainer lists contract schemas
- **WHEN** the `schemas/` directory is listed
- **THEN** schemas exist for `changerail.delivery-plan.v1` and
  `changerail.delivery-plan-status.v1`

#### Scenario: Plan uses public-safe workspace references
- **WHEN** a delivery plan declares workspaces
- **THEN** each workspace uses a stable alias and a consumer-root-relative path
- **AND** the plan schema rejects machine-specific absolute workspace paths

#### Scenario: Plan rejects credential-bearing values
- **WHEN** a delivery plan contains URL userinfo, password-like fields,
  token-like fields or secret-bearing runtime state
- **THEN** schema-backed validation fails before runner semantic validation

#### Scenario: Plan declares cards and dependencies
- **WHEN** a delivery plan is valid
- **THEN** every card has a stable id, workspace alias, card path or filename,
  optional dependencies, optional wave and optional per-card model or reasoning
  override
- **AND** recovery cards may declare optional `recovery_for` links to a source
  card in the same plan

#### Scenario: Helper-generated plan uses the same contract
- **WHEN** a ChangeRail helper generates a delivery plan from ordered card paths
- **THEN** the output uses `changerail.delivery-plan.v1`
- **AND** downstream runner commands validate it with the tracked delivery plan
  schema before applying queue semantics

### Requirement: Delivery plan status contract
ChangeRail MUST define a public schema-backed
`changerail.delivery-plan-status.v1` contract for aggregate queue status.

#### Scenario: Queue status references child records
- **WHEN** a queue run starts or updates aggregate state
- **THEN** the status record includes the plan fingerprint, per-card states and
  references to child `changerail.delivery-run.v1` status records when those
  child records exist

#### Scenario: Queue status records terminal outcome
- **WHEN** a queue run reaches a terminal state
- **THEN** the status record records terminal outcome `DELIVERED`, `NO-GO` or
  `BLOCKED`
- **AND** it records whether the run used push-enabled or explicit `--no-push`
  success criteria

#### Scenario: Queue status records recovery evidence
- **WHEN** a recovery card is inserted after a recoverable terminal child
- **THEN** aggregate status can preserve `recovery_for`, `terminal_reason`,
  source `recovered` state and `recovered_by` lineage without raw log parsing

#### Scenario: Queue runtime remains ignored
- **WHEN** a queue status record is written
- **THEN** the default path is under ignored `.runtime/changerail/`
- **AND** the status schema does not require raw logs or secrets

#### Scenario: Queue mirrors matching child progress
- **WHEN** an active child status contains schema-valid progress and matching
  run/card identity
- **THEN** aggregate card status may mirror `progress` and `progress_health`
- **AND** it still references the child status instead of embedding raw logs

#### Scenario: Queue rejects mismatched child progress
- **WHEN** a child status progress record belongs to another run or card
- **THEN** aggregate card status does not mirror that progress
- **AND** it records bounded `progress_diagnostic` instead of child values

### Requirement: Delivery plan schema fixtures
ChangeRail contract schema validation MUST cover delivery plan and delivery
plan status schemas in the public schema smoke suite.

#### Scenario: Positive fixtures validate
- **WHEN** release schema smoke validates representative delivery plan and plan
  status fixtures
- **THEN** both fixtures validate against their tracked schemas

#### Scenario: Negative fixture violates plan safety
- **WHEN** release schema smoke validates a delivery plan with an absolute
  workspace path or duplicate identifier
- **THEN** the fixture fails schema or semantic validation

### Requirement: Release checks покрывают все contract schemas
ChangeRail release и verification documentation MUST описывать полный публичный
contract schema set: review verdict, review cycle history, delivery manifest,
delivery run и evidence index.

#### Scenario: Maintainer проверяет release checks
- **WHEN** maintainer читает release или contract documentation
- **THEN** documented schema coverage включает все пять публичных
  `changerail-*.schema.json` contract files

### Requirement: Release schema validation gate
ChangeRail release verification MUST validate every public contract schema with
Draft 2020-12 meta-schema checks and fixture-backed document validation.

#### Scenario: Public schema is malformed
- **WHEN** a tracked `schemas/changerail-*.schema.json` file is not a valid
  Draft 2020-12 schema
- **THEN** the release schema validation smoke exits non-zero

#### Scenario: Helper and schema drift apart
- **WHEN** a positive or negative fixture no longer matches the helper-backed
  validation contract for review verdict, review cycle history, delivery
  manifest, delivery run or evidence index
- **THEN** the release schema validation smoke exits non-zero

### Requirement: Contract helpers use shared Python runtime
Delivery manifest and review verdict helper entrypoints MUST execute through
the shared ChangeRail Python runtime selector before schema-backed helper code
imports runtime dependencies.

#### Scenario: Review verdict helper starts on supported runtime
- **WHEN** an operator invokes the review verdict helper through the ChangeRail
  runtime entrypoint
- **THEN** the shared selector validates the interpreter and required modules
- **AND** verdict validation or fingerprint behavior proceeds normally

#### Scenario: Delivery manifest helper starts on supported runtime
- **WHEN** delivery, review or publish invokes the delivery manifest helper
  through the ChangeRail runtime entrypoint
- **THEN** the shared selector validates the interpreter and required modules
- **AND** manifest derive, validate, staging-plan, finalize-card or
  publish-update behavior proceeds normally

#### Scenario: Contract helper dependency is missing
- **WHEN** the selected interpreter lacks `jsonschema`
- **THEN** contract helper invocation exits non-zero before schema-backed code
  imports
- **AND** the diagnostic names `jsonschema` as the missing runtime dependency

### Requirement: Retained verification evidence capture
ChangeRail MUST provide a helper for ChangeRail-owned verification commands that
captures retained evidence with command identity, timestamps, exit code,
classification, concise summary and raw output reference.

#### Scenario: Successful verification command is retained
- **WHEN** the evidence helper runs a ChangeRail-owned verification command from
  an argv array and the command exits zero
- **THEN** it writes an evidence index entry with a stable evidence id, command
  argv summary, `started_at`, `ended_at`, exit code, classification and concise
  observed summary
- **AND** it writes the command output under ignored `.runtime/changerail/`
  evidence storage and records a repository-relative raw output path

#### Scenario: Failed verification command is retained
- **WHEN** the evidence helper runs a verification command that exits non-zero
- **THEN** it records the non-zero exit code and observed failure summary in the
  evidence index
- **AND** it exits non-zero for the caller without discarding the retained
  runtime evidence

#### Scenario: Timed-out verification command is retained
- **WHEN** the evidence helper terminates a command because its configured
  timeout elapsed
- **THEN** it records timeout status, elapsed timing and retained partial output
  evidence
- **AND** it exits non-zero for the caller

### Requirement: Runtime-only evidence storage
Retained raw command evidence MUST live only under ignored ChangeRail runtime
state, while tracked cards, manifests and verdicts may contain only concise
summaries and references.

#### Scenario: Evidence index uses ignored paths
- **WHEN** the evidence helper writes an index and raw output files
- **THEN** the paths are under `.runtime/changerail/evidence/`
- **AND** tracked card, manifest or verdict payloads contain references instead
  of raw command output

#### Scenario: Missing evidence is rejected
- **WHEN** evidence validation checks an index that references a missing runtime
  output file
- **THEN** validation exits non-zero with a structured diagnostic naming the
  missing evidence id or path

### Requirement: Evidence redaction safety
The evidence helper MUST avoid retaining obvious secret-like values from command
arguments or output.

#### Scenario: Secret-like argv is rejected before execution
- **WHEN** a requested command argv contains an obvious token-like assignment or
  credential-bearing value
- **THEN** the evidence helper refuses to execute the command
- **AND** it records a diagnostic without writing the secret-like value into the
  evidence index or raw output

#### Scenario: Secret-like output is redacted
- **WHEN** command output contains an obvious token-like assignment
- **THEN** the retained output replaces the sensitive value with a redaction
  marker
- **AND** the evidence index records that redaction occurred

### Requirement: Evidence classifications
Retained evidence entries MUST distinguish mandatory, diagnostic and
not-applicable verification evidence.

#### Scenario: Mandatory evidence is captured
- **WHEN** delivery captures a required verification command
- **THEN** the evidence entry classification is `mandatory`

#### Scenario: Diagnostic evidence is captured
- **WHEN** delivery captures a non-gating diagnostic command
- **THEN** the evidence entry classification is `diagnostic`

#### Scenario: Not-applicable evidence is recorded
- **WHEN** delivery records why RED evidence or another check is not applicable
- **THEN** the evidence entry classification is `not_applicable`
- **AND** the entry contains a concise reason instead of a raw command output

### Requirement: Evidence references in manifest and verdict contracts
Delivery manifests and review verdicts MUST allow concise evidence references
that identify retained evidence without embedding raw logs.

#### Scenario: Manifest references verification evidence
- **WHEN** delivery updates a manifest after running verification
- **THEN** `verification_summary` can include command evidence references with
  evidence id, index path and raw output path

#### Scenario: Review verdict references audited evidence
- **WHEN** a reviewer records acceptance or finding evidence
- **THEN** the review verdict can include evidence references with evidence id,
  index path and raw output path
- **AND** validation rejects malformed evidence reference objects

### Requirement: Retained evidence smoke coverage
ChangeRail smoke tests MUST cover retained evidence success, failure, timeout,
redaction and missing evidence cases.

#### Scenario: Evidence smoke suite runs
- **WHEN** the retained evidence smoke is executed
- **THEN** it observes helper success capture, non-zero capture, timeout
  capture, output redaction and missing evidence validation failure

#### Scenario: Release baseline includes evidence smoke
- **WHEN** the release baseline runs
- **THEN** retained evidence smoke coverage is included with the public contract
  and helper validation checks

### Requirement: Delivery run remote preflight evidence
The `changerail.delivery-run.v1` contract MUST support structured sanitized
evidence for remote-push publish-target preflight checks while keeping the
canonical top-level delivery-run fields stable.

#### Scenario: Remote preflight failure evidence validates
- **WHEN** a delivery run status records a failed `publish target` preflight
  check for a remote-push target
- **THEN** the check may include structured fields for result, remote, branch,
  remote URL class, failure class, retryability, attempt count, command summary
  and bounded sanitized detail
- **AND** the document validates against
  `schemas/changerail-delivery-run.schema.json`

#### Scenario: Delivery run does not add duplicate aliases
- **WHEN** remote preflight diagnostics are recorded
- **THEN** the delivery run status continues to use canonical top-level fields
  `schema`, `run_id`, `updated_at`, `workspace`, `card`, `phase`, `result`,
  `timestamps`, `command` and `usage`
- **AND** schema validation rejects duplicate top-level aliases such as `id`,
  `status` or `started_at`

#### Scenario: Sanitized evidence excludes raw secrets and logs
- **WHEN** remote preflight evidence is stored in delivery-run status
- **THEN** it contains no raw remote URL userinfo, token-like query values, raw
  stdout or raw stderr
- **AND** raw logs remain ignored runtime evidence referenced only by existing
  log paths when available

### Requirement: Queue status remote preflight evidence
The `changerail.delivery-plan-status.v1` contract MUST allow queue card
diagnostics to reference child remote preflight evidence without embedding raw
child logs.

#### Scenario: Queue card references child remote failure
- **WHEN** aggregate queue status records a card blocked by child remote
  publish-target preflight
- **THEN** the card entry may include a compact reason, terminal reason or
  failure class summary plus `run_status_path`
- **AND** the status validates against
  `schemas/changerail-delivery-plan-status.schema.json`

### Requirement: Review rescue budget contract
ChangeRail review-cycle history schemas MUST represent post-review same-card
rescue budget state separately from review cycle numbering.

#### Scenario: Initial review consumes no rescue attempt
- **WHEN** a review-cycle history record includes the first independent review
  cycle and the writer knows the rescue budget state
- **THEN** the record can store `rescue_budget.limit`,
  `rescue_budget.used`, `rescue_budget.remaining` and
  `rescue_budget.exhausted`
- **AND** the first cycle can store `same_card_rescue_attempt: 0`

#### Scenario: Re-review records consumed rescue attempts
- **WHEN** a same-card fix follows an independent `no-go` and a fresh re-review
  is recorded
- **THEN** the re-review cycle can store the consumed
  `same_card_rescue_attempt`
- **AND** the top-level `rescue_budget.used` and
  `rescue_budget.remaining` counters reflect the same post-review rescue budget

#### Scenario: Legacy review history remains readable
- **WHEN** an existing review-cycle history record omits rescue budget fields
- **THEN** schema validation still accepts the record
- **AND** consumers treat the absent budget fields as unknown instead of
  deriving a configured limit from prose

### Requirement: Delivery run review rescue budget summary
ChangeRail delivery-run schemas MUST allow a best-effort review rescue budget
summary without making it the canonical source when review-cycle history exists.

#### Scenario: Run record summarizes review budget
- **WHEN** a delivery-run status record includes review performance summary
  data
- **THEN** `performance.review.rescue_budget` can store `limit`, `used`,
  `remaining` and `exhausted`

#### Scenario: Legacy run record omits review budget
- **WHEN** a delivery-run status record lacks `performance.review.rescue_budget`
- **THEN** schema validation still accepts the record
- **AND** observability consumers report budget values as unknown unless
  review-cycle history provides them

### Requirement: Maintenance scan report contract schemas
ChangeRail MUST publish Draft 2020-12 JSON Schemas for maintenance scan reports
and detector results using canonical ids `changerail.maintenance-scan-report.v1`
and `changerail.maintenance-detector-result.v1`.

#### Scenario: Maintainer lists maintenance scan schemas
- **WHEN** the `schemas/` directory is listed
- **THEN** schemas exist for `changerail.maintenance-scan-report.v1`
- **AND** schemas exist for `changerail.maintenance-detector-result.v1`

#### Scenario: Scan report separates diagnostics
- **WHEN** a maintenance scan report contains raw detector findings, detector
  execution errors and configuration diagnostics
- **THEN** schema validation preserves those as distinct fields
- **AND** rejects unknown contract-owned fields

#### Scenario: Contract schema smoke covers scan schemas
- **WHEN** `python3 scripts/smoke-contract-schemas.py` runs
- **THEN** the smoke validates representative positive and negative documents
  for maintenance scan report and detector result schemas

### Requirement: Maintenance adapter detector-result contract
ChangeRail detector-result contracts MUST represent adapter-produced findings
and adapter execution errors without language-specific fields.

#### Scenario: Adapter finding validates
- **WHEN** an adapter emits a generic finding with detector id, severity, code,
  message and repository-relative path evidence
- **THEN** the detector-result schema accepts the mapped finding

#### Scenario: Adapter execution error validates separately
- **WHEN** an adapter times out, exits non-zero or emits invalid JSON
- **THEN** the scan report can represent that outcome as a detector error
- **AND** schema validation keeps it separate from ordinary detector findings

### Requirement: Maintenance run status contract
ChangeRail MUST define a public `changerail.maintenance-run.v1` contract for
machine-readable maintenance runner status, phases, results, timestamps,
report references, annotation references and bounded execution diagnostics.

#### Scenario: Runner writes maintenance status
- **WHEN** the maintenance runner writes
  `.runtime/changerail/maintenance/runs/<run-id>/status.json`
- **THEN** the JSON uses `changerail.maintenance-run.v1`
- **AND** it includes workspace metadata, mode, phase, result, timestamps,
  command metadata, lock diagnostics, timeout diagnostics and optional usage
  availability

#### Scenario: Status references reports indirectly
- **WHEN** scan mode completes and report output is retained
- **THEN** the status references repository-relative ignored runtime paths for
  scan/report artifacts
- **AND** it does not inline raw command logs, credentials or local runtime
  traces

### Requirement: Maintenance run schema validation
ChangeRail MUST publish a Draft 2020-12 JSON Schema for
`changerail.maintenance-run.v1` and include fixture-backed validation in the
public contract smoke suite.

#### Scenario: Maintainer lists maintenance run schema
- **WHEN** the tracked `schemas/` directory is listed
- **THEN** `schemas/changerail-maintenance-run.schema.json` exists

#### Scenario: Contract smoke validates maintenance run fixture
- **WHEN** `python3 scripts/smoke-contract-schemas.py` runs
- **THEN** it validates a representative successful scan-mode
  `changerail.maintenance-run.v1` fixture
- **AND** it rejects a malformed fixture with unknown contract-owned fields or
  invalid timestamp values

### Requirement: Maintenance runner control flow uses structured status
Maintenance runner supervisors MUST determine terminal state from
`changerail.maintenance-run.v1` fields, not from scraped human prose.

#### Scenario: Scan command exits successfully
- **WHEN** deterministic scan/report command exits zero and produces
  schema-valid output
- **THEN** runner status records a successful result from structured command
  outcome and artifact validation

#### Scenario: Human prose conflicts with structured output
- **WHEN** child output contains human text that resembles success but required
  schema-valid artifacts are missing
- **THEN** runner status records failure or blocked diagnostics
- **AND** the supervisor does not treat the run as successful

### Requirement: Maintenance contract reference inventory is complete
ChangeRail contract documentation MUST list every tracked public maintenance
schema and keep feedback, quality rollup and proposal-decision references
current.

#### Scenario: Maintainer inspects contract reference
- **WHEN** a maintainer reads `docs/changerail-contracts.md`
- **THEN** the schema inventory includes `changerail-maintenance-quality-rollup.schema.json`
- **AND** it includes `changerail-maintenance-proposal-decision.schema.json`
- **AND** it does not describe the implemented maintenance harness as only a future harness

#### Scenario: Feedback reference is current
- **WHEN** a maintainer reads the maintenance feedback reference
- **THEN** it documents review-history, blocked delivery-run and external detector-result inputs
- **AND** it states that invalid, unsafe or unsupported feedback inputs fail closed instead of being inferred from prose

#### Scenario: Quality reference is current
- **WHEN** a maintainer reads the quality-rollup reference
- **THEN** it documents text, JSON and CSV output modes
- **AND** it explains complete/incomplete evidence and `known`/`unknown` metric status semantics

### Requirement: Consumer lock public schema
ChangeRail MUST publish `schemas/changerail-consumer-lock.schema.json` with id
`changerail.consumer-lock.v1` and include it in schema inventory, verifier
wiring and contract smoke.

#### Scenario: Valid consumer lock is checked
- **WHEN** a lock records a supported version/revision, source, wiring profiles
  and `advisory` or `strict` enforcement
- **THEN** schema validation succeeds

#### Scenario: Lock contains unsafe or incomplete source data
- **WHEN** a lock omits exact revision, contains an absolute machine path or a
  credential-bearing source URI
- **THEN** schema or semantic validation fails closed

#### Scenario: Schema inventory is incomplete
- **WHEN** a bootstrapped locked consumer lacks the consumer-lock schema
- **THEN** `verify-project` reports the missing public contract as blocking

### Requirement: Deterministic review preflight result
The ChangeRail review helper MUST produce a schema-valid deterministic preflight
result before any LLM payload review is launched.

#### Scenario: Machine gates pass for ordinary code
- **WHEN** a review-ready ordinary card has a valid manifest, exact scope,
  archived changes and all available strict deterministic checks pass
- **THEN** preflight returns `ready-for-llm-review`
- **AND** the result recommends reasoning effort `high`

#### Scenario: Manifest operation metadata is stale
- **WHEN** expected and actual comparable path sets are identical but manifest
  operation metadata differs from Git state
- **THEN** explicit normalization may refresh operation metadata
- **AND** normalization MUST NOT add a missing or extra path to the manifest

#### Scenario: Process gate fails
- **WHEN** manifest, board, archive, scope or an available strict deterministic
  check fails
- **THEN** preflight returns a structured blocker before LLM launch
- **AND** no implementation review cycle is consumed

### Requirement: Bounded review-fingerprint investigation decision
ChangeRail MUST publish a tracked investigation decision before a retained
oversized review-fingerprint implementation can authorize a bounded successor
above the ordinary production-LOC limit. The decision MUST reproduce the
public-safe production LOC breakdown, identify removable duplication or
over-expansion, bind one exact successor card and preserve exact fingerprint
freshness requirements.

#### Scenario: Investigation records bounded successor decision
- **WHEN** the investigation card is completed for the retained
  review-fingerprint payload
- **THEN** it records that the retained attempt is read-only investigation
  evidence and not review evidence
- **AND** it records the 527 production-LOC breakdown from public-safe retained
  evidence
- **AND** it binds the exact successor
  `deliver-bounded-review-fingerprint-optimization`
- **AND** it states a replacement ceiling no greater than 500 added production
  LOC without raising the global limit

#### Scenario: Successor keeps exact fingerprint verification floor
- **WHEN** the bounded successor is authorized from the investigation decision
- **THEN** the successor acceptance keeps exact reviewed-tree parity for add,
  modify, delete, rename, symlink, Unicode, spaces, literal arrow and valid
  non-UTF-8 Linux paths
- **AND** untracked-content hashing, ignored runtime exclusion, cache
  invalidation, shared freshness consumer behavior and synthetic benchmark
  coverage remain mandatory verification targets

### Requirement: Bounded runner retained-resume investigation decision
ChangeRail MUST publish a tracked investigation decision before the retained
runner-resume successor can use a bounded deterministic-preflight exception for
the prior oversized payload. The decision MUST reproduce the public-safe
preflight stop, bind the exact successor card, require a successor ceiling no
greater than 500 added production-counted LOC and preserve the retained-resume
verification floor.

#### Scenario: Investigation records retained runner preflight stop
- **WHEN** the investigation card is completed for the retained runner-resume
  payload
- **THEN** it records that deterministic preflight measured 562 added
  production-counted LOC in `bin/changerail-delivery-runner`
- **AND** it records that the retained payload declared a new runner/status
  protocol boundary without published investigation authorization
- **AND** it states that the retained payload is investigation input only and
  not reviewed or publishable evidence

#### Scenario: Successor remains exact runner resume card
- **WHEN** the investigation decision binds the successor
- **THEN** it names `support-runner-resume-after-investigation-required` as the
  exact successor id
- **AND** it records the current queue path
  `openspec/board/2.todo/support-runner-resume-after-investigation-required.md`
- **AND** it records the authorization-time target path
  `openspec/board/3.inprogress/support-runner-resume-after-investigation-required.md`
- **AND** it requires the later authorization source to use production LOC
  ceiling 500 and `allow_new_authority_or_wire_protocol` true
- **AND** it requires the successor and authorization source to retain exact
  reciprocal relations to the published investigation before deterministic
  preflight can consume the authorization

#### Scenario: Verification floor remains fail-closed
- **WHEN** the successor implementation is simplified below the bounded ceiling
- **THEN** it still verifies retained identity schema acceptance and rejection,
  single-card retained resume success, wrong card, wrong workspace, stale
  authorization, relation mismatch, over-ceiling authorization, fingerprint
  drift, queue original resume, queue replacement recovery and duplicate
  recovery rejection

#### Scenario: Over-ceiling successor cannot reuse the decision
- **WHEN** the successor still adds more than 500 production-counted LOC or
  changes to a different successor card without a new investigation decision
- **THEN** deterministic review preflight returns `investigation-required`
- **AND** it does not launch semantic review or treat this investigation as a
  reusable authorization waiver

### Requirement: Published investigation authorization for deterministic preflight
Deterministic preflight SHALL принимать inline JSON
`Published investigation authorization` только как однозначную bounded chain.
Legacy absence field или ровно одно значение `none` означает
`not-declared`; non-default authorization MUST находиться в единственном
`## Review` section и единственном exact field. Reference MUST быть одним JSON
object с ровно двумя уникальными decoded keys `authorization_card` и
`authorization_id`, значения которых являются non-empty strings и указывают на
clean unchanged tracked `HEAD` artifact в `4.done` с exact path/id/status.

Published source MUST иметь единственный `## Authorization` section и
единственный exact `Investigation authorization` field. Source JSON MUST быть
одним object с ровно шестью уникальными decoded keys `investigation_card`,
`investigation_id`, `successor_card`, `successor_id`,
`production_loc_ceiling` и `allow_new_authority_or_wire_protocol`. Identity
values MUST быть non-empty strings, ceiling MUST быть integer-not-boolean от
301 до 500, protocol allowance MUST быть boolean, а exact current successor и
published investigation path/id/status/tracked state MUST совпадать до выдачи
authority.

Каждый проверяемый `## Depends On`/`## Blocks` MUST существовать ровно в одном
second-level section. Authorization source `Depends On` MUST содержать ровно
одну dependency — exact investigation. Successor `Depends On` и investigation
`Blocks` MUST содержать expected edge ровно один раз, но MAY сохранять другие
legitimate dependencies/targets. Relation reference совпадает только как exact
bare `<id>`, `<id>.md` или canonical
`openspec/board/<lane>/<id>.md`; duplicate equivalent expected forms, missing,
mismatch, foreign stem и non-board path не удовлетворяют edge.

Duplicate field/section/decoded key, missing/extra JSON key, invalid type,
duplicate expected edge и extra authorization-source dependency MUST вернуть
authorization `invalid`, outcome `investigation-required` и запретить semantic
review eligibility. Этот active exact-cardinality contract supersedes прежнюю
multi-candidate tolerance для нескольких exact source fields: clean published
authorization source содержит ровно один object; JSON вне exact field не
является candidate. Все остальные production LOC, ceiling, protocol,
repeated-defect, scope, freshness и risk gates остаются независимыми и
fail-closed.

#### Scenario: Exact published chain допускает bounded successor
- **WHEN** successor содержит ровно один schema-valid two-field reference,
  source содержит ровно один schema-valid six-field object и три required
  relation edges однозначно связывают clean published cards
- **THEN** preflight применяет только declared LOC, repeated-defect и protocol
  decisions к exact successor
- **AND** ordinary payload в пределах ceiling получает
  `ready-for-llm-review` с route `high`

#### Scenario: Duplicate или extra authorization structure отклоняется
- **WHEN** successor reference или source field/section повторяется, JSON
  содержит duplicate decoded key, missing/extra key либо value неверного type
- **THEN** authorization имеет `status: invalid`
- **AND** preflight возвращает exit `1`, outcome `investigation-required` и
  `llm_review.required: false` до semantic review

#### Scenario: Authorization source имеет ambiguous dependency
- **WHEN** source `Depends On` отсутствует, повторен, ссылается не на exact
  investigation либо содержит второй dependency item/reference
- **THEN** source не выдает bounded authority
- **AND** preflight возвращает `investigation-required` без semantic review

#### Scenario: Shared board relations сохраняют совместимость
- **WHEN** exact successor dependency встречается ровно один раз рядом с
  unrelated successor dependencies либо exact investigation `Blocks` edge
  встречается ровно один раз рядом с другими blocked targets
- **THEN** unrelated relations не делают exact authorization invalid
- **AND** duplicate equivalent form самого required edge остается invalid

#### Scenario: Published card использует filename reference
- **WHEN** required relation использует exact `<id>.md` или canonical board path
  с этим filename
- **THEN** preflight нормализует его в exact card id
- **AND** другой stem или noncanonical path не совпадает с required edge

#### Scenario: Repeated defect не имеет valid authorization
- **WHEN** successor объявляет repeated defect, а authorization отсутствует,
  unreadable, stale, unpublished, ambiguous или не связывает exact successor
- **THEN** preflight возвращает `investigation-required`
- **AND** LLM не запускается и authority не выводится из prose

#### Scenario: Successor превышает published ceiling
- **WHEN** valid authorization объявляет ceiling 500, но successor добавляет
  больше 500 production LOC
- **THEN** preflight возвращает `investigation-required`
- **AND** result называет превышенный explicit ceiling

#### Scenario: Successor не имеет protocol allowance
- **WHEN** valid authorization связывает exact successor, но boolean protocol
  allowance равен false, а successor объявляет новый authority/wire protocol
- **THEN** preflight возвращает `investigation-required`
- **AND** valid relation/repeated authorization не переопределяет protocol
  decision

#### Scenario: Ранее допускавшийся второй exact source field больше не выбирается
- **WHEN** clean source содержит canonical matching object и второй exact
  `Investigation authorization` field, включая unrelated object
- **THEN** preflight отклоняет source по field cardinality вместо target
  selection
- **AND** JSON examples вне exact field остаются ignored и не влияют на
  authorization cardinality

### Requirement: Published bounded review-fingerprint authorization source
ChangeRail MUST publish the bounded review-fingerprint authorization as one
clean tracked `4.done` board card before the successor
`deliver-bounded-review-fingerprint-optimization` can use the bounded
production-LOC exception. The authorization source MUST contain exactly one
schema-valid investigation authorization object bound to investigation
`investigate-bounded-review-fingerprint-payload`, successor
`deliver-bounded-review-fingerprint-optimization`, production LOC ceiling 500
and `allow_new_authority_or_wire_protocol` false.

#### Scenario: Authorization source binds the exact card chain
- **WHEN** deterministic review preflight evaluates
  `deliver-bounded-review-fingerprint-optimization` after the investigation and
  authorization cards are published in `4.done`
- **THEN** it accepts the bounded authorization only if the successor references
  `openspec/board/4.done/authorize-bounded-review-fingerprint-payload.md`
- **AND** the authorization source depends on
  `investigate-bounded-review-fingerprint-payload`
- **AND** the published investigation blocks
  `deliver-bounded-review-fingerprint-optimization`
- **AND** the authorization object uses the exact investigation id, successor
  id, canonical board paths, ceiling 500 and protocol allowance false

#### Scenario: Mismatched authorization cannot be reused
- **WHEN** another card references the published review-fingerprint
  authorization source or the exact reciprocal card links do not match
- **THEN** deterministic review preflight returns `investigation-required`
- **AND** it does not launch an LLM review or treat the authorization as a
  reusable waiver

### Requirement: Published bounded runner retained-resume authorization source
ChangeRail MUST publish the bounded runner retained-resume authorization as one
clean tracked `4.done` board card before successor
`support-runner-resume-after-investigation-required` can use the bounded
production-LOC and runner/status protocol-boundary exception. The authorization
source MUST contain exactly one schema-valid investigation authorization object
bound to investigation `investigate-runner-retained-resume-payload-boundary`,
successor `support-runner-resume-after-investigation-required`, production LOC
ceiling 500 and `allow_new_authority_or_wire_protocol` true.

#### Scenario: Authorization source binds the exact runner resume card chain
- **WHEN** deterministic review preflight evaluates
  `support-runner-resume-after-investigation-required` after the investigation
  and authorization cards are published in `4.done`
- **THEN** it accepts the bounded authorization only if the successor references
  `openspec/board/4.done/authorize-bounded-runner-retained-resume-payload.md`
- **AND** the authorization source depends on
  `investigate-runner-retained-resume-payload-boundary`
- **AND** the published investigation blocks
  `support-runner-resume-after-investigation-required`
- **AND** the authorization object uses the exact investigation id, successor
  id, canonical board paths, ceiling 500 and protocol allowance true

#### Scenario: Runner resume authorization cannot be reused
- **WHEN** another card references the published runner retained-resume
  authorization source or the exact reciprocal card links do not match
- **THEN** deterministic review preflight returns `investigation-required`
- **AND** it does not launch an LLM review or treat the authorization as a
  reusable waiver

### Requirement: Published bounded execution-target authorization source
ChangeRail MUST publish the bounded execution-target authorization as one clean
tracked `4.done` board card before successor
`enforce-declared-execution-target-invariant` can use the bounded
production-LOC and target-identity protocol-boundary exception. The
authorization source MUST contain exactly one schema-valid investigation
authorization object bound to investigation
`investigate-bounded-field-validation-batch`, successor
`enforce-declared-execution-target-invariant`, production LOC ceiling 500 and
`allow_new_authority_or_wire_protocol` true.

#### Scenario: Authorization source binds the exact execution-target card chain
- **WHEN** deterministic review preflight evaluates
  `enforce-declared-execution-target-invariant` after the investigation and
  authorization cards are published in `4.done`
- **THEN** it accepts the bounded authorization only if the successor references
  `openspec/board/4.done/authorize-bounded-execution-target-payload.md`
- **AND** the authorization source depends on
  `investigate-bounded-field-validation-batch`
- **AND** the published investigation blocks
  `enforce-declared-execution-target-invariant`
- **AND** the authorization object uses the exact investigation id, successor
  id, canonical board paths, ceiling 500 and protocol allowance true

#### Scenario: Execution-target authorization cannot be reused
- **WHEN** another card references the published execution-target
  authorization source or the exact reciprocal card links do not match
- **THEN** deterministic review preflight returns `investigation-required`
- **AND** it does not launch an LLM review or treat the authorization as a
  reusable waiver

### Requirement: Published bounded live-progress authorization source
ChangeRail MUST publish the bounded live-progress authorization as one clean
tracked `4.done` board card before successor
`expose-structured-live-delivery-progress` can use the bounded production-LOC
and progress/status protocol-boundary exception. The authorization source MUST
contain exactly one schema-valid investigation authorization object bound to
investigation `investigate-bounded-field-validation-batch`, successor
`expose-structured-live-delivery-progress`, production LOC ceiling 500 and
`allow_new_authority_or_wire_protocol` true.

#### Scenario: Authorization source binds the exact live-progress card chain
- **WHEN** deterministic review preflight evaluates
  `expose-structured-live-delivery-progress` after the investigation and
  authorization cards are published in `4.done`
- **THEN** it accepts the bounded authorization only if the successor references
  `openspec/board/4.done/authorize-bounded-live-progress-payload.md`
- **AND** the authorization source depends on
  `investigate-bounded-field-validation-batch`
- **AND** the published investigation blocks
  `expose-structured-live-delivery-progress`
- **AND** the authorization object uses the exact investigation id, successor
  id, canonical board paths, ceiling 500 and protocol allowance true

#### Scenario: Live-progress authorization cannot be reused
- **WHEN** another card references the published live-progress authorization
  source, raw-log telemetry authority is attempted, or the exact reciprocal
  card links do not match
- **THEN** deterministic review preflight returns `investigation-required`
- **AND** it does not launch an LLM review or treat the authorization as a
  reusable telemetry waiver

### Requirement: Published bounded external-blocker resume authorization source
ChangeRail MUST publish the bounded external-blocker resume authorization as
one clean tracked `4.done` board card before successor
`resume-retained-payload-after-external-blocker` can use the bounded
production-LOC and retained-payload blocker/evidence protocol-boundary
exception. The authorization source MUST contain exactly one schema-valid
investigation authorization object bound to investigation
`investigate-bounded-field-validation-batch`, successor
`resume-retained-payload-after-external-blocker`, production LOC ceiling 500
and `allow_new_authority_or_wire_protocol` true.

#### Scenario: Authorization source binds the exact external-blocker resume chain
- **WHEN** deterministic review preflight evaluates
  `resume-retained-payload-after-external-blocker` after the investigation and
  authorization cards are published in `4.done`
- **THEN** it accepts the bounded authorization only if the successor
  references
  `openspec/board/4.done/authorize-bounded-external-blocker-resume-payload.md`
- **AND** the authorization source depends on
  `investigate-bounded-field-validation-batch`
- **AND** the published investigation blocks
  `resume-retained-payload-after-external-blocker`
- **AND** the authorization object uses the exact investigation id, successor
  id, canonical board paths, ceiling 500 and protocol allowance true

#### Scenario: External-blocker resume authorization cannot be reused
- **WHEN** another card references the published external-blocker resume
  authorization source, generic dirty bypass or credential/target authority is
  attempted, or the exact reciprocal card links do not match
- **THEN** deterministic review preflight returns `investigation-required`
- **AND** it does not launch an LLM review or treat the authorization as a
  reusable dirty-resume waiver

### Requirement: Published bounded recovery-episodes authorization source
ChangeRail MUST publish the bounded recovery-episodes authorization as one clean
tracked `4.done` board card before successor
`report-recovery-aware-delivery-episodes` can use the bounded production-LOC
and episode/attempt lineage plus derived metrics protocol-boundary exception.
The authorization source MUST contain exactly one schema-valid investigation
authorization object bound to investigation
`investigate-bounded-field-validation-batch`, successor
`report-recovery-aware-delivery-episodes`, production LOC ceiling 500 and
`allow_new_authority_or_wire_protocol` true. The accepted split is runner
lineage up to 300 production LOC and metrics collection/output up to 200
production LOC, and it MUST NOT authorize raw-log reconstruction, prompt/tool
payload retention or broader content-bearing telemetry.

#### Scenario: Authorization source binds the exact recovery-episodes chain
- **WHEN** deterministic review preflight evaluates
  `report-recovery-aware-delivery-episodes` after the investigation and
  authorization cards are published in `4.done`
- **THEN** it accepts the bounded authorization only if the successor
  references
  `openspec/board/4.done/authorize-bounded-recovery-episodes-payload.md`
- **AND** the authorization source depends on
  `investigate-bounded-field-validation-batch`
- **AND** the published investigation blocks
  `report-recovery-aware-delivery-episodes`
- **AND** the authorization object uses the exact investigation id, successor
  id, canonical board paths, ceiling 500 and protocol allowance true

#### Scenario: Recovery-episodes authorization cannot be reused
- **WHEN** another card references the published recovery-episodes
  authorization source, raw-log reconstruction or broader telemetry authority
  is attempted, one side exceeds its accepted split budget, or the exact
  reciprocal card links do not match
- **THEN** deterministic review preflight returns `investigation-required`
- **AND** it does not launch an LLM review or treat the authorization as a
  reusable telemetry waiver

### Requirement: Published bounded verification-coverage authorization source
ChangeRail MUST publish the bounded verification-coverage authorization as one
clean tracked `4.done` board card before successor
`define-verification-coverage-map` can use the bounded production-LOC and
verification map/ledger protocol-boundary exception. The authorization source
MUST contain exactly one schema-valid investigation authorization object bound
to investigation `investigate-bounded-field-validation-batch`, successor
`define-verification-coverage-map`, production LOC ceiling 500 and
`allow_new_authority_or_wire_protocol` true. The accepted boundary is one
five-field project map and derived runtime ledger with references to
acceptance, tasks and evidence instead of copied secondary truth.

#### Scenario: Authorization source binds the exact verification-coverage chain
- **WHEN** deterministic review preflight evaluates
  `define-verification-coverage-map` after the investigation and authorization
  cards are published in `4.done`
- **THEN** it accepts the bounded authorization only if the successor
  references
  `openspec/board/4.done/authorize-bounded-verification-coverage-payload.md`
- **AND** the authorization source depends on
  `investigate-bounded-field-validation-batch`
- **AND** the published investigation blocks
  `define-verification-coverage-map`
- **AND** the authorization object uses the exact investigation id, successor
  id, canonical board paths, ceiling 500 and protocol allowance true

#### Scenario: Verification-coverage authorization cannot be reused
- **WHEN** another card references the published verification-coverage
  authorization source, a payload copies acceptance/tasks/evidence into a
  second source of truth, or the exact reciprocal card links do not match
- **THEN** deterministic review preflight returns `investigation-required`
- **AND** it does not launch an LLM review or treat the authorization as a
  reusable coverage-catalog waiver

### Requirement: Published bounded source-profile authorization source
ChangeRail MUST publish the bounded source-profile authorization as one clean
tracked `4.done` board card before successor
`materialize-versioned-source-classification-profiles` can use the bounded
production-LOC and profile provenance/materialization/check protocol-boundary
exception. The authorization source MUST contain exactly one schema-valid
investigation authorization object bound to investigation
`investigate-bounded-field-validation-batch`, successor
`materialize-versioned-source-classification-profiles`, production LOC ceiling
500 and `allow_new_authority_or_wire_protocol` true. The accepted boundary is
the existing `.changerail/source-classification.yaml` as the only effective
rules input, with profile detection, materialization and drift reporting using
one canonical normalization path.

#### Scenario: Authorization source binds the exact source-profile chain
- **WHEN** deterministic review preflight evaluates
  `materialize-versioned-source-classification-profiles` after the
  investigation and authorization cards are published in `4.done`
- **THEN** it accepts the bounded authorization only if the successor
  references
  `openspec/board/4.done/authorize-bounded-source-profile-payload.md`
- **AND** the authorization source depends on
  `investigate-bounded-field-validation-batch`
- **AND** the published investigation blocks
  `materialize-versioned-source-classification-profiles`
- **AND** the authorization object uses the exact investigation id, successor
  id, canonical board paths, ceiling 500 and protocol allowance true

#### Scenario: Source-profile authorization cannot be reused
- **WHEN** another card references the published source-profile authorization
  source, a second effective rules source is added, or the exact reciprocal card
  links do not match
- **THEN** deterministic review preflight returns `investigation-required`
- **AND** it does not launch an LLM review or treat the authorization as a
  reusable source-classification waiver

### Requirement: Field-validation successors MUST use bounded investigation decisions
ChangeRail MUST require bounded decisions for exact successors
`enforce-declared-execution-target-invariant`,
`expose-structured-live-delivery-progress`,
`resume-retained-payload-after-external-blocker`,
`report-recovery-aware-delivery-episodes`,
`define-verification-coverage-map` and
`materialize-versioned-source-classification-profiles`, which receive separate
published authorization sources with a ceiling no higher than 500 and protocol
allowance only after a tracked investigation decision that lists them in
`Blocks`. The decision MUST identify every successor id, its authorization-time
`3.inprogress` path, accepted protocol boundary and verification floor. It
MUST NOT act as a reusable/global waiver, authorize another successor, raise
the global ceiling or allow provider discovery, provision, credential handling,
target substitution, prose/raw-log parsing or a second acceptance source of
truth outside the accepted successor boundary.

#### Scenario: Exact successor uses bounded source
- **WHEN** a successor references its own separate `4.done` authorization
  source, bound to this investigation and the exact `3.inprogress` successor
  card path
- **THEN** deterministic preflight can apply the source's ceiling up to 500
  and the accepted protocol allowance
- **AND** reciprocal relation checks still require the successor, authorization
  source and investigation cards to name the same exact ids and canonical
  board paths

#### Scenario: Payload expands the decision
- **WHEN** production LOC is above 500, successor/path does not match, the
  implementation adds authority outside the accepted boundary or the same
  unresolved blocker hypothesis repeats
- **THEN** the authorization is not applicable
- **AND** delivery requires a split or a new investigation instead of extending
  the same-card rescue

### Requirement: Repeated field defect MUST become one bounded hypothesis
Investigation MUST allow a post-investigation successor to clear the
repeated-defect stop only when the decision fixes a single-source
implementation boundary, verification floor and absence of extra same-card
rescue budget for the exact successor.

#### Scenario: Bounded successor implements the decision
- **WHEN** the successor preserves exact investigated scope and dependency
  lineage
- **THEN** the card can declare `Repeated defect class: no`
- **AND** protocol/LOC authorization remains mandatory

#### Scenario: The same defect repeats after bounded implementation
- **WHEN** verification or review again finds the same unresolved invariant or
  blocker class
- **THEN** the successor does not expand scope under the current authorization
- **AND** a linked investigation or split decision is required

### Requirement: Go test files are not production LOC
The deterministic preflight MUST exclude paths ending in `*_test.go` from
added production LOC while continuing to count other scoped Go source files.

#### Scenario: Go production and test files share a scope
- **WHEN** a scoped change adds a production `.go` file and a `*_test.go` file
- **THEN** only the production file contributes to `added_production_loc`

### Requirement: Review preflight source classification
The deterministic review preflight MUST support an optional tracked
`.changerail/source-classification.yaml` consumer file using schema id
`changerail.source-classification.v1`. When present, the file MUST declare
repository-relative production source roots and source-kind rules using safe
paths that are neither absolute nor path-traversing. Missing classification
MUST preserve existing built-in source suffix behavior. Malformed
classification MUST block preflight before LLM review and MUST NOT be ignored
as a legacy fallback.

#### Scenario: Consumer declares production source kind
- **WHEN** preflight runs in a consumer repository with a schema-valid source
  classification file that declares a production root and source kind
- **THEN** files under that root matching the declared source kind are eligible
  for production complexity accounting
- **AND** built-in non-production path parts continue to exclude tests,
  fixtures, examples, schemas, templates, docs and OpenSpec artifacts

#### Scenario: Source classification is missing
- **WHEN** preflight runs without `.changerail/source-classification.yaml`
- **THEN** existing built-in production suffixes and executable helper rules
  continue to determine `added_production_loc`
- **AND** domain-specific suffixes that require declaration are not counted by
  default

#### Scenario: Source classification is unsafe
- **WHEN** the classification file contains an absolute path, traversal, root
  escape, duplicate source-kind id or schema-invalid value
- **THEN** preflight returns `blocked`
- **AND** the result includes a failing deterministic check explaining the
  invalid classification

### Requirement: Versioned source classification profile
ChangeRail MUST validate `changerail.source-classification-profile.v1` as a
data-only envelope with stable id/version, compatible classification payload
and bounded repository-name detection signals. Contract and helper semantics
MUST reject absolute or traversing paths, executable behavior, commands,
imports, network sources and unsupported measurement strategies.

#### Scenario: Built-in and integration profiles use shared validation
- **WHEN** a tracked built-in generic profile or explicitly supplied local
  integration profile contains safe rules and signals
- **THEN** both validate through the same public schema and checksum helper
- **AND** neither source can load executable code or network data

#### Scenario: Unsafe profile is rejected
- **WHEN** a profile contains machine-absolute paths, traversal, command, URL,
  dynamic module or unsupported measurement strategy
- **THEN** schema or semantic validation fails closed
- **AND** no source classification is derived from that profile

### Requirement: Stable profile checksum and identity
ChangeRail MUST compute `sha256:<hex>` from documented canonical serialization
of the complete validated profile. Equal id/version with different checksum
MUST be treated as an immutable-version conflict.

#### Scenario: Equivalent profile loaded twice
- **WHEN** identical profile content is loaded from supported sources
- **THEN** id, version and checksum match
- **AND** source reports distinguish source kind without retaining an absolute
  machine path

#### Scenario: Published profile version changes content
- **WHEN** profile id/version matches a known profile but canonical checksum
  differs
- **THEN** validation or merge blocks
- **AND** maintainers must publish a new profile version

### Requirement: Deterministic profile merge
Multiple selected profiles MUST merge in declared order with deterministic
canonical output, equivalent-rule deduplication and fail-closed conflicts for
overlapping rules with conflicting measurements or different content under one
source-kind id.

#### Scenario: Compatible profiles merge
- **WHEN** selected profiles have disjoint or exactly equivalent rules
- **THEN** merge creates one stable source classification and ordered
  provenance
- **AND** repeated merge produces the same checksum and output

#### Scenario: Measurement conflict is detected
- **WHEN** overlapping suffix/root rules classify one source through different
  measures such as `lines` and `xml-structure`
- **THEN** merge stops with a machine-readable conflict
- **AND** it does not choose by discovery or file-system order

### Requirement: Classification profile provenance compatibility
`changerail.source-classification.v1` MUST allow optional ordered profile
identity/checksum/source provenance and normalized declared override paths
while keeping final source kinds and non-production roots as the only rules
used by review preflight.

#### Scenario: Legacy project file has no provenance
- **WHEN** an existing schema-valid classification has no profile provenance
- **THEN** it remains valid and preflight behavior does not change
- **AND** profile-aware diagnostics report provenance as unavailable

#### Scenario: Materialized file declares overrides
- **WHEN** final classification differs from profile baseline only in declared
  normalized override paths
- **THEN** check reports the differences as project overrides
- **AND** values are read from final classification rather than duplicated in
  provenance

### Requirement: Read-only source profile detection
ChangeRail MUST provide a machine-readable `detect` command that evaluates
validated profile path signals against tracked `HEAD` or an explicit Git tree
snapshot and reports candidates, matched signals, bounded confidence,
ambiguities and recommended action without modifying files.

#### Scenario: Detection runs in dirty working tree
- **WHEN** the working tree adds a profile marker that is not in tracked `HEAD`
  and no explicit snapshot is provided
- **THEN** detection evaluates `HEAD` and ignores the dirty marker
- **AND** review preflight risk and classification do not change

#### Scenario: Multiple candidates match
- **WHEN** a mixed repository matches signals for several profiles with equal
  or overlapping confidence
- **THEN** JSON output lists all candidates and ambiguities with stable scores
- **AND** the command does not choose or materialize one automatically

### Requirement: Explicit preview-first profile materialization
ChangeRail MUST materialize source classification only from explicitly selected
schema-valid profiles. Default materialization MUST be preview-only; mutation
MUST require `--write`, revalidate inputs and atomically create a schema-valid
project file.

#### Scenario: New project confirms profile
- **WHEN** the target file is absent and the operator previews then writes an
  exact profile selection
- **THEN** the helper creates `.changerail/source-classification.yaml` with
  final rules and ordered id/version/checksum/source provenance
- **AND** existing review preflight validates and uses that file

#### Scenario: Existing file differs
- **WHEN** project classification already exists with different effective rules
  or provenance
- **THEN** materialization returns non-zero with bounded semantic diff and
  `migration-required`
- **AND** it does not overwrite or reformat the existing file

#### Scenario: Repeated materialization is idempotent
- **WHEN** the same profile selection and inputs target an already matching
  file
- **THEN** the command reports no change and exits successfully
- **AND** file bytes and effective rules remain stable

### Requirement: Candidate has no classification authority
Detected but unaccepted profiles MUST NOT affect `added_production_loc`, risk
tier, investigation decision or source breakdown. Current review preflight may
be affected only by tracked schema-valid `.changerail/source-classification.yaml`.

#### Scenario: High-confidence candidate is not materialized
- **WHEN** detect reports a high-confidence domain profile but project
  classification is absent
- **THEN** preflight continues with the current built-in classifier
- **AND** the candidate report is advisory evidence only

### Requirement: Source classification profile check report
ChangeRail MUST emit schema-valid `changerail.source-classification-check.v1`
with selected profile identities, source/checksum state, declared project
overrides, effective rule summary, bounded covered/excluded/uncovered counts
and diagnostics. The report MUST NOT include source contents or
machine-absolute paths.

#### Scenario: Final file matches profile and declared overrides
- **WHEN** profile baseline is available and all final differences are in exact
  declared override paths
- **THEN** check reports matching provenance and named project overrides
- **AND** effective rules come from the final project classification

#### Scenario: Profile divergence is undeclared
- **WHEN** a final rule differs from confirmed selected profile outside
  declared override paths or same profile id/version has a different checksum
- **THEN** check reports blocking `confirmed_profile_drift`
- **AND** it does not rewrite or silently merge the file

### Requirement: Detection-only drift has no risk authority
Unaccepted candidate and uncovered-source diagnostics MUST remain value-free and
advisory until they prove divergence from an explicitly selected schema-valid
profile. Advisory detection MUST NOT change current source classification or
risk calculation.

#### Scenario: Unknown suffix points to candidate
- **WHEN** tracked HEAD contains path signals for an unaccepted profile not
  covered by built-in or final rules
- **THEN** check reports bounded confidence, counts and capped normalized path
  examples as advisory
- **AND** `added_production_loc` and review route use final classification

#### Scenario: Selected profile rule no longer covers matching source
- **WHEN** a confirmed selected profile requires a source rule but final project
  classification omits it without declared override
- **THEN** check reports blocking drift
- **AND** preflight cannot treat the omission as a lower-risk payload

### Requirement: Review preflight reports source-kind complexity detail
The `changerail.review-preflight-result.v1` result MUST retain aggregate
complexity guard fields and MUST include bounded source-kind detail for counted
production source. Each detail entry MUST identify the source kind, measure
strategy, counted path count, raw added lines and effective complexity
contribution without copying source content.

#### Scenario: Payload has mixed source kinds
- **WHEN** a scoped payload contains production files counted by more than one
  source kind
- **THEN** the preflight result reports the aggregate guard value
- **AND** it reports source-kind breakdown entries that explain how each kind
  contributed to the aggregate

#### Scenario: Breakdown remains public-safe
- **WHEN** preflight emits source-kind detail
- **THEN** the result contains repository-relative paths or counts only
- **AND** it does not include raw source snippets, customer data or ignored
  runtime content

### Requirement: Review preflight counts declared production BSL
The deterministic review preflight MUST count added `.bsl` lines toward
production complexity only when the path is classified as production BSL source
by the consumer source-classification contract. Existing non-production path
parts MUST continue to exclude BSL tests, fixtures, examples, schemas,
templates, docs and OpenSpec artifacts from production complexity.

#### Scenario: Production BSL crosses default ceiling
- **WHEN** a scoped payload adds more than 300 lines to `.bsl` files under a
  declared production BSL source root
- **THEN** preflight reports those lines in `added_production_loc`
- **AND** preflight returns `investigation-required` unless a valid bounded
  published investigation authorization applies

#### Scenario: Non-production BSL is excluded
- **WHEN** a scoped payload adds `.bsl` files under `test`, `tests`,
  `fixtures`, `examples` or another built-in non-production root
- **THEN** those lines do not contribute to `added_production_loc`
- **AND** source-kind breakdown explains that no production BSL contribution was
  counted for those paths

#### Scenario: Existing source suffixes are unchanged
- **WHEN** a scoped payload adds Python, Go, JavaScript or executable helper
  files covered by the built-in classifier
- **THEN** their production complexity behavior remains the same as before this
  change

### Requirement: Review preflight counts declared Designer XML structurally
The deterministic review preflight MUST count Designer XML only when a valid
consumer source-classification rule proves that the XML path belongs to a
production Designer XML source kind. The preflight MUST NOT treat generic
`.xml` paths as production source by suffix alone.

#### Scenario: Production Designer XML is classified
- **WHEN** a scoped payload adds Designer XML under a declared production
  Designer XML source root
- **THEN** preflight counts the file through the Designer XML measure strategy
- **AND** the source-kind breakdown identifies Designer XML as a production
  contribution

#### Scenario: Generic XML remains non-production
- **WHEN** a scoped payload adds `.xml` files under schemas, templates,
  fixtures, examples, docs, OpenSpec or an unclassified path
- **THEN** those XML files do not contribute to production complexity
- **AND** they do not make the payload `investigation-required` by suffix alone

### Requirement: Designer XML complexity is fail-closed and explainable
Designer XML production complexity MUST use an effective structural measure
instead of unconditional raw XML line count when the helper can measure the XML
safely. If the helper cannot safely prove structural complexity, it MUST either
fall back to raw added lines or block preflight; it MUST NOT silently report
zero for classified production Designer XML.

#### Scenario: Verbose Designer XML has bounded structural complexity
- **WHEN** a classified Designer XML addition has raw added lines above the
  default or authorized LOC ceiling but measured structural complexity within
  the applicable ceiling
- **THEN** preflight may continue to the declared risk-appropriate review route
- **AND** the result reports both raw added lines and effective structural
  complexity for the Designer XML source kind

#### Scenario: Designer XML exceeds effective ceiling
- **WHEN** classified Designer XML effective complexity exceeds the applicable
  default or published authorization ceiling
- **THEN** preflight returns `investigation-required`
- **AND** the complexity guard reasons identify the exceeded effective ceiling

#### Scenario: Designer XML cannot be measured safely
- **WHEN** classified production Designer XML is malformed or the structural
  measure cannot be computed conservatively
- **THEN** preflight uses raw added lines as the effective contribution or
  returns `blocked`
- **AND** the result explains the fallback or blocker in source-kind detail

### Requirement: Mixed 1C payload complexity is itemized
The preflight result MUST itemize mixed production payloads so maintainers can
see how BSL and Designer XML contribute to the guard without inspecting raw
source content.

#### Scenario: BSL and Designer XML share a payload
- **WHEN** a scoped payload contains declared production BSL and Designer XML
  changes
- **THEN** `added_production_loc` reflects their aggregate effective
  contribution
- **AND** source-kind detail reports separate BSL and Designer XML entries with
  path counts, raw added lines, effective contribution and measure strategy

### Requirement: Review history phase counters
Review-cycle history MUST support independent optional counters for planning,
delivery-fix, implementation-review and live-admission phases.

#### Scenario: Planning is repeated before implementation review
- **WHEN** a card needs multiple planning corrections before its first semantic
  implementation payload review
- **THEN** planning cycles increase independently
- **AND** implementation review/rescue counters remain unchanged

### Requirement: Retained payload identity status contract
`changerail.delivery-run.v1` MUST allow an optional `retained_payload` object
using `schema: changerail.retained-payload-identity.v1`. When present for
`terminal_reason: investigation_required`, the object MUST include the source
run id, source status path, captured timestamp, card id/path, workspace root,
`HEAD` commit, reviewed tree SHA, diff fingerprint and review target kind.

#### Scenario: Schema validates retained identity
- **WHEN** a delivery-run status records an `investigation_required` retained
  payload with all required identity fields
- **THEN** `schemas/changerail-delivery-run.schema.json` validation succeeds
- **AND** the diff fingerprint matches the canonical `sha256:<hex>` format

#### Scenario: Retained identity is tied to the prior status
- **WHEN** a retained-payload identity is present
- **THEN** it names the source run id and source status path that produced the
  `investigation_required` stop
- **AND** a later consumer can compare those values with the resume input before
  evaluating the current working tree

### Requirement: Retained payload identity is public-safe
The retained-payload identity contract MUST describe only bounded metadata. It
MUST NOT require raw source content, raw command output, credentials, customer
data, absolute private project aliases beyond the existing workspace root field
or ignored runtime evidence content.

#### Scenario: Schema rejects raw retained content fields
- **WHEN** a retained-payload identity attempts to embed raw source text or raw
  stdout/stderr as required proof
- **THEN** the delivery-run schema does not accept those fields as part of the
  identity contract
- **AND** consumers rely on canonical fingerprints and explicit runtime path
  references instead

### Requirement: Retained-payload resume validation contract
`changerail.delivery-run.v1` resume checks MUST represent retained-payload
resume validation as structured preflight checks with stable machine reasons.
The contract MUST distinguish prior-status invalidity, card mismatch, workspace
mismatch, missing retained identity, payload drift, authorization absence,
authorization staleness, relation mismatch, authorization ceiling violation,
missing/stale/mismatched external evidence, non-passing evidence and target
identity mismatch.

#### Scenario: Successful retained resume records fresh checks
- **WHEN** retained-payload resume validation succeeds
- **THEN** the resumed delivery-run status contains passing checks for prior
  status validation, retained-payload fingerprint validation and published
  investigation authorization validation
- **AND** those checks are fresh for the resumed run rather than copied as pass
  evidence from the prior blocked status

#### Scenario: Failed retained resume is machine-classified
- **WHEN** retained-payload resume validation fails for a known unsafe class
- **THEN** the resumed delivery-run status has `terminal_outcome: BLOCKED`
- **AND** `terminal_reason` is a stable lowercase machine value describing that
  class

### Requirement: External resume evidence contract
Retained external resume MUST ссылаться на schema-valid ignored evidence index,
scope которого идентифицирует source run/card, а required entries имеют passed,
fresh и redacted state согласно blocker policy.

#### Scenario: Fresh evidence принимается
- **WHEN** каждый required evidence id существует один раз, имеет
  `status: passed`, принадлежит source scope и завершен после blocker observation
  в пределах maximum age
- **THEN** resume записывает fresh passing checks для blocker, evidence и
  payload identity
- **AND** raw evidence output не копируется в delivery status

#### Scenario: Evidence нельзя переиспользовать между scope
- **WHEN** evidence принадлежит другому card/run, не содержит required id,
  является stale или сообщает non-passing status
- **THEN** resume status становится `BLOCKED` со stable failure reason
- **AND** child continuation не запускается

### Requirement: Published authorization remains source of truth for retained resume
Retained-payload resume MUST use the published investigation authorization
contract as the only authority to cross the investigation-required boundary.
Authorization paths MUST be tracked under `openspec/board/4.done/`, clean at
`HEAD`, relation-matched to the successor card and within the declared ceiling.

#### Scenario: Stale authorization blocks retained resume
- **WHEN** the authorization card or investigation card is missing, outside
  `4.done`, untracked, modified in the index/worktree or stale relative to
  `HEAD`
- **THEN** retained-payload resume returns `BLOCKED`
- **AND** it does not launch review or publish

#### Scenario: Relation mismatch blocks retained resume
- **WHEN** the authorization source does not bind the exact investigation card,
  investigation id, successor card, successor id and reciprocal card links
- **THEN** retained-payload resume returns `BLOCKED`
- **AND** the status identifies the mismatch as authorization validation failure

### Requirement: Queue retained recovery status metadata
`changerail.delivery-plan-status.v1` MUST represent
`investigation_required` and `recoverable_external_blocker` recovery with
bounded structured metadata. Aggregate card status MUST be able to identify the
recovery kind, source run status path, source terminal reason, retained-payload
fingerprint summary and external blocker policy when applicable without
embedding raw child logs or raw source payload.

#### Scenario: Aggregate status records retained recovery context
- **WHEN** `resume-plan` evaluates a prior `investigation_required` child
- **THEN** aggregate status records a bounded reference to the prior child
  status and retained-payload fingerprint summary
- **AND** schema validation succeeds without raw child stdout/stderr content

#### Scenario: Duplicate recovery paths fail closed
- **WHEN** aggregate status or current plan would attach more than one active
  recovery path to the same `investigation_required` source
- **THEN** queue validation records `BLOCKED`
- **AND** it identifies the duplicate recovery as a stable machine reason

### Requirement: Aggregate retained external recovery contract
`changerail.delivery-plan-status.v1` MUST представлять source run/status, card,
fingerprint, blocker id/class и evidence policy для resume одного original
child, не изменяя существующий investigation recovery object.

#### Scenario: Plan status сохраняет resumable context
- **WHEN** child завершается на valid recoverable external blocker
- **THEN** aggregate card status сохраняет bounded recovery context и source
  identity
- **AND** raw logs и evidence contents остаются indirect ignored references

### Requirement: Queue recovery terminal reasons are stable
Queue retained recovery MUST use stable lowercase machine reasons for rejected
resume or recovery augmentation. The contract MUST cover missing prior status,
invalid prior status, wrong card, wrong workspace, missing retained identity,
fingerprint drift, stale authorization, missing/stale evidence, target mismatch
and duplicate recovery path.

#### Scenario: Failed queue recovery is machine-readable
- **WHEN** `resume-plan` rejects an `investigation_required` recovery
- **THEN** aggregate status contains `result: BLOCKED`
- **AND** the affected card status contains a stable terminal reason or reason
  detail that identifies the rejected class

#### Scenario: Downstream blocked state is explicit
- **WHEN** a downstream card depends on an `investigation_required` source that
  is not delivered or recovered
- **THEN** aggregate status keeps the downstream card pending or blocked
- **AND** it does not infer success from the presence of an authorization card
  alone

### Requirement: Declared execution target contract
ChangeRail MUST принимать optional tracked `.changerail/execution-target.json`
только как `changerail.execution-target.v1` с bounded logical `id`,
non-sensitive `fingerprint` и `target_substitution_policy: forbid` и MUST
отклонять physical endpoint, credentials, target contents и unknown fields.

#### Scenario: Valid declaration принимается
- **WHEN** project содержит regular tracked declaration с точным v1 shape
- **THEN** ChangeRail получает canonical target identity projection
- **AND** не выполняет discovery, network access или provider commands

#### Scenario: Content-bearing declaration отклоняется
- **WHEN** declaration содержит endpoint, credential, environment value,
  arbitrary metadata или symlink/path escape
- **THEN** verification и delivery fail closed до child launch

### Requirement: Target-bound evidence contract
Если declaration присутствует, manifest, delivery status и runtime evidence MUST
ссылаться на один exact target id/fingerprint, а blocker и evidence MUST NOT
давать authority на provision, rebind или substitution.

#### Scenario: Evidence совпадает с declaration
- **WHEN** applicable runtime evidence содержит одну identity, совпадающую с
  captured declaration и manifest
- **THEN** target identity gate может пройти вместе с domain oracle checks

#### Scenario: Evidence не доказывает объявленную цель
- **WHEN** evidence отсутствует, ссылается на другую или несколько identities
- **THEN** review/publish gate fail closed
- **AND** raw endpoint или credential не запрашивается как remediation

### Requirement: Retained recovery SHALL preserve declared execution target
The delivery contracts MUST сохранять logical id/fingerprint объявленной
project execution target в retained identity и MUST NOT принимать
blocker/evidence как authority на provision, rebind или substitution.

#### Scenario: Target identity совпадает
- **WHEN** blocker, current project declaration, evidence-index metadata and
  every recovery evidence entry refer to the same logical id/fingerprint
- **THEN** target identity check может пройти вместе с остальными resume gates
- **AND** physical endpoint и credentials не копируются в status.

#### Scenario: Target identity изменилась
- **WHEN** current declaration отсутствует, имеет другой fingerprint или
  evidence относится к другой/нескольким целям
- **THEN** retained resume fail closed
- **AND** explicit rebind требует нового clean delivery attempt.

### Requirement: Explicit target rebind invalidates prior lineage
Изменение tracked execution target MUST начинать новый clean delivery attempt и
MUST делать prior retained status, evidence, manifest и review verdict
неприменимыми.

#### Scenario: Declaration изменилась после blocker
- **WHEN** current target id/fingerprint не совпадает с retained identity
- **THEN** dirty resume fail closed до child launch
- **AND** оператор начинает новый clean attempt

### Requirement: Episode and attempt identity contract
Runtime owner schemas MUST использовать schema-valid episode ids и typed
attempt objects с unique ids и optional parent/previous links. Links MUST
разрешаться внутри одного workspace/card/episode и MUST отклонять cycles или
conflicting duplicate attempt ids.

#### Scenario: Cross-artifact lineage проходит валидацию
- **WHEN** delivery status, review history и manifest используют один episode id
  и distinct linked attempt ids
- **THEN** contract validation и episode materialization проходят
- **AND** каждый source остается authoritative для owned fields

#### Scenario: Cross-episode link fail closed
- **WHEN** attempt ссылается на parent/previous id другого episode либо duplicate
  id имеет другое content
- **THEN** episode refresh сообщает contract conflict
- **AND** не merge ambiguous attempts

### Requirement: Derived delivery episode record
`changerail.delivery-episode.v1` MUST быть ignored public-safe derived index
schema-valid attempt summaries и indirect owner-artifact references. Он MUST
NOT включать prompts, raw commands, MCP payloads, screenshots, source content
или raw logs.

#### Scenario: Episode refresh объединяет owner artifacts
- **WHEN** matching delivery, review и publish artifacts существуют для одного
  episode
- **THEN** refresh атомарно пишет ordered attempt summaries и final lifecycle
  state
- **AND** detailed evidence остается referenced через normalized ignored paths

#### Scenario: Legacy run не имеет explicit lineage
- **WHEN** reader встречает valid legacy delivery run без episode fields
- **THEN** он может показать isolated synthetic episode для этого run
- **AND** missing lineage и later review/publish data остаются `unknown`

### Requirement: Sampling and duration contract
Performance/episode schemas MUST отличать complete aggregate totals от bounded
detail samples и MUST явно представлять incomplete intervals.

#### Scenario: Detail sample усечен
- **WHEN** retained detail count меньше observed count
- **THEN** record объявляет truncation и sample limit
- **AND** aggregate totals остаются valid для complete observed set

### Requirement: Project-owned verification coverage map
ChangeRail MUST валидировать optional tracked map
`changerail.verification-coverage.v1`, entries которой содержат только `id`,
`applies_to`, `invariant`, `oracle` и `required_evidence`. Invalid configured
map MUST fail closed; отсутствующая map MUST сохранять current project-declared
verification floor.

#### Scenario: Minimal generic Python rule проходит валидацию
- **WHEN** project rule использует normalized Python path selectors, stable
  invariant, bounded project oracle ref и required command/runtime evidence
- **THEN** schema validation проходит
- **AND** rule не делает formatter, typing или environment matrix checks
  mandatory вне explicit project policy

#### Scenario: Настроено unsafe или incomplete rule
- **WHEN** entry имеет duplicate id, absolute/traversing glob, не имеет selector,
  содержит unknown oracle kind, unbound evidence ref или undeclared extra policy
  field
- **THEN** map validation fail closed
- **AND** ни один coverage ledger этой map не считается trusted

### Requirement: Verification coverage plan and ledger contracts
ChangeRail MUST предоставлять tracked per-change plan-reference contract и
ignored runtime ledger contract. Оба MUST быть fingerprint-bound и ссылаться на
coverage ids/card acceptance hashes без дублирования invariant, oracle,
commands, acceptance text или final verdict authority.

#### Scenario: Planning ссылается на selected coverage
- **WHEN** `ff` оценивает configured map для change
- **THEN** tracked plan записывает map fingerprint, selected rule ids и exact
  card acceptance hashes
- **AND** map и card остаются sources referenced content

#### Scenario: Runtime ledger записывает observed evidence
- **WHEN** delivery reconciles actual manifest scope и записывает evidence
- **THEN** ignored ledger связывает map/plan/manifest/review fingerprints и
  evidence-index refs для каждого applicable rule
- **AND** evidence refs содержат required kind/oracle_ref binding и указывают
  на schema-valid passed evidence-index entries
- **AND** не объявляет business acceptance и не включает raw outputs

### Requirement: Domain verification surface extension boundary
Coverage selectors MUST принимать schema-valid namespaced surface kinds от
project/domain extension, не назначая domain semantics или execution tools
generic ChangeRail core.

#### Scenario: Domain extension различает specialized surfaces
- **WHEN** extension выдает namespaced kinds для language modules, metadata,
  forms, roles, posting, reports, migrations или runtime UI
- **THEN** generic coverage matching может выбрать project-owned rules по ids
- **AND** domain classification/oracle behavior остается owned by extension

#### Scenario: Manifest сообщает extension surfaces
- **WHEN** delivery manifest содержит schema-valid `extension_surfaces`
- **THEN** deterministic preflight включает эти namespaced kinds в coverage
  applicability
- **AND** invalid surface report блокируется manifest schema validation

### Requirement: Manifest coverage summary
`changerail.delivery-manifest.v1` MUST поддерживать concise verification
coverage summary, который ссылается на ignored ledger path/fingerprint и
сообщает configured/applicable/covered/missing/invalid counts без map content
или raw evidence.

#### Scenario: Delivery обновляет coverage summary
- **WHEN** actual manifest scope reconciled с configured map и ledger
- **THEN** manifest записывает bounded counts и ledger reference
- **AND** evidence contents остаются в ignored evidence index/output paths

#### Scenario: Summary заявляет complete при stale ledger
- **WHEN** manifest summary сообщает отсутствие missing entries, но ledger
  fingerprints не совпадают с current map/card/scope/review target
- **THEN** deterministic preflight отклоняет summary
- **AND** independent review не запускается на его основании

### Requirement: Published bounded phase-routed delivery authorization source
ChangeRail MUST publish the bounded phase-routed delivery authorization as one
clean tracked `4.done` board card before successor
`implement-phase-routed-delivery-authorization-boundary` can use the bounded
production-LOC and aggregate/child authority, resume and status
protocol-boundary exception. The source MUST contain exactly one schema-valid
investigation authorization object with only the six generic authorization
fields, bound to investigation
`investigate-phase-routed-delivery-authorization-boundary`, successor
`implement-phase-routed-delivery-authorization-boundary`, production LOC
ceiling 500 and `allow_new_authority_or_wire_protocol` true.

#### Scenario: Exact phase-routed successor consumes the authorization
- **WHEN** deterministic review preflight evaluates
  `implement-phase-routed-delivery-authorization-boundary` in `3.inprogress`
  after the investigation and authorization cards are published in `4.done`
- **THEN** it accepts the bounded authorization only if the successor references
  `openspec/board/4.done/authorize-bounded-phase-routed-delivery-payload.md`
- **AND** the authorization source depends on
  `investigate-phase-routed-delivery-authorization-boundary`
- **AND** the published investigation blocks
  `implement-phase-routed-delivery-authorization-boundary`
- **AND** the successor depends on
  `investigate-phase-routed-delivery-authorization-boundary` and references
  the authorization source
- **AND** the authorization object uses the exact investigation id, successor
  id, canonical board paths, ceiling 500 and protocol allowance true

#### Scenario: Phase-routed authorization mismatch fails closed
- **WHEN** another card references the source or any card id, canonical path,
  investigation relation, ceiling or protocol flag differs from the published
  authorization chain
- **THEN** deterministic review preflight returns `investigation-required`
- **AND** it does not launch semantic review or treat the source as authority
  for a third repair, an alternate aggregate runtime root, a reusable protocol
  waiver or weakened global review policy

### Requirement: Решение для type-safe классификации decoded authorization target
ChangeRail MUST опубликовать tracked decision-only investigation до следующей
authorization implementation после двух последовательных отклоненных lineages
одного decoded-target defect class. Решение MUST сделать classification total
для любого JSON value, сохранить decoded object pairs, запретить hashing или
set membership непроверенных identity values, связать полную connected matrix и
выбрать ровно один новый exact authorization source.

#### Scenario: Decode сохраняет пары и не выпускает input exception
- **WHEN** exact field `Investigation authorization` содержит любой JSON value
- **THEN** parser декодирует ровно одно значение и представляет каждый object
  как ordered decoded key/value pairs, включая duplicate decoded keys
- **AND** trailing content, invalid JSON, top-level scalar/container values и
  произвольные nested values дают bounded classified result
- **AND** input-dependent `TypeError`, hash error, path error или иной Python
  exception не выходит без structured preflight result
- **AND** JSON вне exact source field не является authorization candidate

#### Scenario: Typed hints предшествуют target selection
- **WHEN** decoded candidates классифицируются для current successor и
  investigation dependency
- **THEN** parser линейно проверяет четыре identity keys в исходном pair order и
  создает hint только из validated non-empty string
- **AND** array, object, null, boolean и number identity values никогда не
  используются в hashing, set membership, mapping construction, path
  construction или semantic relation lookup
- **AND** current-target candidate имеет хотя бы один exact typed successor hint
  и хотя бы один exact typed investigation hint из trusted card/dependency
  metadata
- **AND** unrelated и fully distinct candidates не выбираются

#### Scenario: Candidate selection exact и fail closed
- **WHEN** все pair-preserved values получили typed target hints
- **THEN** до strict validation требуется ровно один current-target candidate
- **AND** ноль либо два и более matches возвращают authorization `invalid` с
  detail `authorization source must contain exactly one matching current target`
- **AND** canonical плюс malformed matching отклоняется как ambiguity, а
  canonical плюс unrelated или fully distinct сохраняет ровно один match
- **AND** единственный malformed matching candidate выбирается и отклоняется по
  earliest duplicate, shape или type rule, а не трактуется как unrelated

#### Scenario: Strict validation order предшествует semantics
- **WHEN** выбран ровно один current-target candidate
- **THEN** validation по порядку проверяет duplicate decoded keys, exact
  six-field shape, identity string types, integer-not-boolean ceiling range,
  protocol boolean type и exact typed target equality
- **AND** parser материализует mapping только после уникальности keys и valid
  types всех required values
- **AND** filesystem, published/tracked card и reciprocal relation semantics
  запускаются только над validated mapping
- **AND** review eligibility вычисляется только после прохождения всех semantic
  checks

#### Scenario: Structural rejection имеет единый machine oracle
- **WHEN** decode, selection, duplicate, shape, identity type, range, boolean
  либо typed-target validation завершается отказом
- **THEN** preflight возвращает exit 1, outcome `investigation-required`,
  authorization status `invalid`, exact row detail, `llm_review.required` false
  и reason `complexity guard requires investigation/simplification`
- **AND** `semantic_check_delta`, `semantic_review_dispatch_delta` и
  `model_launch_delta` равны нулю
- **AND** `uncaught_exception` равен false
- **AND** semantic relation failures могут иметь `semantic_check_delta` один,
  но сохраняют `semantic_review_dispatch_delta` и `model_launch_delta` нулевыми
  и не получают review eligibility

#### Scenario: Identity matrix покрывает каждый key, value kind и duplicate order
- **WHEN** будущий authorization parser готовится к review
- **THEN** каждый из `investigation_card`, `investigation_id`, `successor_card` и
  `successor_id` имеет connected single-value rows для exact string, empty
  string, distinct string, null, true, false, integer, float, array и object
- **AND** каждый key имеет positives с legal equivalent escaped key/value
- **AND** каждый key пересекается с каждым перечисленным value в обоих orders:
  literal-then-alternate-escaped и alternate-escaped-then-literal duplicate
- **AND** каждый duplicate row возвращает exact detail `authorization source
  contains duplicate decoded key: <key>` до type, schema либо semantic dispatch
  независимо от duplicate values

#### Scenario: Connected matrix покрывает shape и candidate cardinality
- **WHEN** запускается full focused matrix
- **THEN** она покрывает каждый missing required field, extra fields, каждый
  top-level JSON kind, ceiling boundaries/types и protocol allowance types
- **AND** она покрывает canonical, unrelated, distinct и malformed candidates в
  zero-, one- и multiple-match combinations, а также JSON вне exact field
- **AND** она покрывает source, successor и investigation path/id/status/tracked
  state и reciprocal relation mutations
- **AND** каждый mutated fixture сначала доказывает passing fresh unmodified
  canonical base на той же production preflight boundary и записывает exact
  structured actual/expected results и owned dispatch counters

#### Scenario: Выбран один replacement authorization source
- **WHEN** эта investigation опубликована и разрешена follow-up work
- **THEN** единственный следующий work item —
  `authorize-type-safe-phase-routed-resume-integrity-payload` с initial path
  `openspec/board/2.todo/authorize-type-safe-phase-routed-resume-integrity-payload.md`
  и published path
  `openspec/board/4.done/authorize-type-safe-phase-routed-resume-integrity-payload.md`
- **AND** он зависит от
  `investigate-type-safe-decoded-target-classification-boundary`, блокирует
  `replace-phase-routed-resume-integrity-boundary`, меняет только owning parser
  и connected smoke production surface и остается в пределах 300 added
  production LOC
- **AND** rejected source/rescue payloads остаются forensic-only без repair,
  publication или reuse как новый tracked source

#### Scenario: Exact object сохраняет bounded downstream authority
- **WHEN** новый authorization source позднее опубликован
- **THEN** он содержит ровно один object, связывающий published investigation
  `investigate-type-safe-decoded-target-classification-boundary` с successor
  `replace-phase-routed-resume-integrity-boundary` по exact `3.inprogress` path,
  production LOC ceiling 500 и `allow_new_authority_or_wire_protocol` true
- **AND** successor ссылается только на published source
  `authorize-type-safe-phase-routed-resume-integrity-payload` по exact `4.done`
  path и id
- **AND** измерение successor 501 или больше останавливает работу для новой
  investigation и split authorization вместо повышения ceiling

#### Scenario: Review handoff не circular
- **WHEN** эта investigation или будущий authorization item завершает
  implementation/verification handoff
- **THEN** fresh independent review запускается для получения `GO` или `NO-GO`
  без требования GO на входе
- **AND** только fresh GO разрешает publish и deterministic finalization
- **AND** этот decision-only change не создает authorization card или
  implementation successor

#### Scenario: Fast-forward остается planning-only
- **WHEN** `$changerail-ff` завершает эту investigation
- **THEN** создаются или обновляются только ее board card и один active OpenSpec
  change
- **AND** production code, schemas, tests, CLI, synced main specs, public runtime
  docs и runtime behavior остаются без изменений
