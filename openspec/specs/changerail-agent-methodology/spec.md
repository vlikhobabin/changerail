# changerail-agent-methodology Specification

## Purpose
Зафиксировать общую ChangeRail-методологию для AI-агентов и проектов-потребителей:
где живет reusable agent guidance, какие публичные safety-ограничения она
соблюдает и как будущий bootstrap/verify flow должен использовать этот source
of truth.
## Requirements
### Requirement: Общая методология агентов
ChangeRail MUST provide tracked file `AGENTS.shared.md`, который задает reusable
agent methodology для ChangeRail consumers.

#### Scenario: Проект-потребитель получает ChangeRail methodology
- **WHEN** consumer project bootstrapped from ChangeRail templates
- **THEN** project receives methodology content derived from
  `AGENTS.shared.md`

### Requirement: Generic public-safe content
Shared methodology MUST avoid private workspace names, customer data, secrets,
local traces, credentials и machine-specific runtime state.
Public-safety verification MUST detect common secret assignments, private home
paths and reachable-history leaks while preserving generic examples.

#### Scenario: Ревью публичного репозитория
- **WHEN** `AGENTS.shared.md` reviewed before commit
- **THEN** file contains only generic ChangeRail rules and documented example paths
  such as `/opt/changerail` and `/opt/example-project`

#### Scenario: Public scanner detects secrets and home paths
- **WHEN** public-surface verification scans ChangeRail public files
- **THEN** it fails on token-like secret assignments and common Linux, macOS or
  Windows home-directory paths
- **AND** generic examples such as `/opt/changerail` and
  `/opt/example-project` remain allowed

#### Scenario: Scanner redacts secret values
- **WHEN** a token-like assignment is reported
- **THEN** scanner output identifies file, line and finding kind without
  printing the full secret value

#### Scenario: Scanner allows only explicit placeholder secrets
- **WHEN** public-surface verification encounters a token-like assignment
  containing words such as `token` or `secret`
- **THEN** it reports the assignment unless the value matches a narrow explicit
  placeholder allowlist

#### Scenario: Reachable history is scanned
- **WHEN** release verification runs the documented history scan mode
- **THEN** reachable git history is checked for the same public-safety finding
  classes without printing full secret values

### Requirement: Покрытие workflow
Shared methodology MUST cover ChangeRail lifecycle from exploration through publish,
including board usage, OpenSpec artifacts, review gates, verification evidence и
scoped publishing.

#### Scenario: Агент читает shared methodology
- **WHEN** agent receives shared methodology in consumer project
- **THEN** agent has enough workflow guidance to follow `explore -> ff -> do ->
  review -> pub` without relying on project-private ChangeRail notes

### Requirement: Drift-aware embedding
Shared methodology MUST state that generated consumer-project sections are
subject to future drift checks against ChangeRail source of truth.

#### Scenario: Future verify-project проверяет generated instructions
- **WHEN** consumer project has embedded ChangeRail methodology section
- **THEN** `verify-project` can treat that section as generated content that
  must match `AGENTS.shared.md`

### Requirement: Review-gated story finalization
ChangeRail MUST treat archived card-owned OpenSpec changes as completed change
payload, but MUST keep a review-gated story in `3.inprogress` until a fresh
`go` verdict is published.

#### Scenario: Delivery archives changes before review
- **WHEN** `changerail-do` finishes every planned change for a board card
- **THEN** the card-owned changes are archived and the card remains eligible for
  independent review while still in `3.inprogress`

#### Scenario: Publish finalizes the story
- **WHEN** `changerail-pub` successfully publishes a reviewed card payload
- **THEN** the card is finalized into `4.done` using the board's documented
  post-publish metadata protocol

### Requirement: Post-review change invalidation
ChangeRail MUST require re-review when any substantive tracked content, docs, specs,
schemas, scripts or tests change after a `go` verdict.

#### Scenario: Content changes after go
- **WHEN** a `go` verdict exists and a substantive file in the reviewed payload
  changes before publish
- **THEN** publish treats the verdict as stale and requires a fresh review

#### Scenario: Deterministic post-publish metadata
- **WHEN** publish records deterministic card metadata such as commit or push
  status after a successful commit
- **THEN** that metadata is separated from substantive reviewed payload changes

### Requirement: Project-declared verification floor
ChangeRail delivery MUST execute every mandatory verification command declared by the
project rules, OpenSpec artifacts and affected toolchain, and MUST NOT treat
undeclared generic formatter, strict typing or environment matrices as
mandatory for every consumer project.

#### Scenario: Project declares required checks
- **WHEN** `AGENTS.md`, `openspec/config.yaml`, `tasks.md`, `design.md` or the
  changed toolchain declares a required command
- **THEN** delivery runs that command or stops with a recorded blocker

#### Scenario: Generic workflow has no universal formatter
- **WHEN** a consumer project does not declare a formatter or strict type check
  for the changed surface
- **THEN** ChangeRail does not require that command solely because the generic
  workflow is being used

### Requirement: Verification evidence claims
ChangeRail verification claims MUST identify the executed command, observed outcome
and retained evidence path when raw output is retained.

#### Scenario: Delivery records a passing check
- **WHEN** delivery records a verification command in the card, tasks or
  manifest
- **THEN** the record includes the command and a concrete outcome summary

### Requirement: Test adequacy evidence
ChangeRail delivery MUST explain whether added or changed tests can fail for the
claimed regression and observe the intended behavior source.

#### Scenario: Behavioral test is changed
- **WHEN** delivery adds or modifies a test for a behavioral claim
- **THEN** the evidence records why that test would fail if the behavior were
  broken

#### Scenario: RED evidence is not applicable
- **WHEN** a change is docs-only, config-only or otherwise not usefully
  test-first
- **THEN** delivery records why RED evidence is not applicable instead of
  claiming an unrun failure

### Requirement: Scoped rescue review loop
ChangeRail methodology MUST describe how a no-go review leads to scoped fixes,
re-review and publish only after a fresh go verdict.

#### Scenario: Over-claim receives no-go
- **WHEN** review finds an over-claimed publish scope or unbacked evidence
- **THEN** the implementing session fixes only the scoped blocker and requests a
  fresh review before publish

#### Scenario: Re-review returns go
- **WHEN** a later independent review returns a fresh `go` verdict
- **THEN** publish can proceed while retaining earlier no-go evidence for
  operational learning

### Requirement: ChangeRail public methodology identity
The reusable agent methodology MUST use ChangeRail as the canonical product
name and MUST describe OpenSpec as the artifact/spec workflow dependency rather
than as the product identity.

#### Scenario: Consumer reads shared methodology
- **WHEN** a consumer project receives generated agent methodology
- **THEN** the methodology identifies ChangeRail as the workflow/toolchain
  layer
- **AND** it identifies OpenSpec as the artifact/spec workflow dependency

#### Scenario: Public examples are reviewed
- **WHEN** tracked methodology examples are reviewed before commit
- **THEN** canonical source-of-truth examples use `/opt/changerail`
- **AND** old `/opt/opsx` examples appear only in explicit migration or history
  notes

### Requirement: ChangeRail delivery handoff examples
Shared methodology MUST use ChangeRail lifecycle invocations in delivery
handoff examples.

#### Scenario: Agent completes fast-forward planning
- **WHEN** a card reaches apply-ready OpenSpec artifacts
- **THEN** the handoff example uses `$changerail-do <card-path>` when the
  ChangeRail delivery surface is installed

#### Scenario: Claude user follows the workflow
- **WHEN** a Claude Code user invokes the documented lifecycle
- **THEN** the documented command namespace is `/changerail:*`

### Requirement: Short alias guidance preserves canonical naming
ChangeRail public methodology and user-facing docs MUST present `chrl-*` and
`/chrl:*` as recommended daily shorthand while preserving `changerail-*` and
`/changerail:*` as canonical reference names.

#### Scenario: Agent reads lifecycle guidance
- **WHEN** an agent reads ChangeRail lifecycle documentation
- **THEN** the guidance shows `chrl-*` or `/chrl:*` as acceptable daily
  invocation shorthand
- **AND** it identifies canonical `changerail-*` or `/changerail:*` commands as
  the source-of-truth contract names

#### Scenario: Runtime contracts are reviewed
- **WHEN** runtime paths, schema ids or OpenSpec namespaces are reviewed after
  alias implementation
- **THEN** they continue to use `changerail` naming
- **AND** no new `chrl` runtime namespace is introduced

### Requirement: Board docs align with lifecycle surface
ChangeRail board documentation MUST describe the currently available lifecycle
surface and MUST NOT retain obsolete statements that delivery, review or
publish skills are unavailable when those skills are part of the public surface.

#### Scenario: Agent reads the root board README
- **WHEN** an agent reads `openspec/board/README.md`
- **THEN** the README describes `changerail-ff`, `changerail-do`,
  `changerail-review`, `changerail-pub` and `changerail-deliver` as available
  lifecycle surfaces
- **AND** it keeps the review-gated `3.inprogress -> 4.done` boundary aligned
  with shared methodology

### Requirement: Orchestrator, worker and reviewer role model
Shared methodology MUST define the operational roles used by supervised
ChangeRail delivery: orchestrator, delivery worker and independent reviewer.

#### Scenario: Agent reads shared methodology
- **WHEN** an agent reads `AGENTS.shared.md`
- **THEN** it can identify which context is responsible for choosing cards,
  running or supervising delivery, fixing scoped blockers and requesting
  review
- **AND** it can identify that the reviewer context is separate from the
  planning and implementation context

### Requirement: Role co-location boundaries
Shared methodology MUST state when orchestrator and delivery worker may be the
same session and when they should be separate, while preserving independent
review as a mandatory separate context.

#### Scenario: Small single-card task is delivered
- **WHEN** a card is small enough for the active supervised session to run
  delivery directly
- **THEN** the methodology permits orchestrator and delivery worker to be the
  same session
- **AND** still requires a fresh reviewer context before publish

#### Scenario: Fresh reviewer is unavailable
- **WHEN** delivery reaches review and no fresh reviewer context is available
- **THEN** the workflow stops at the review gate instead of publishing

### Requirement: Batch guidance separates deliver and runner responsibilities
ChangeRail methodology MUST distinguish between the lifecycle skill that can
process an ordered card queue and the tracked runner that supervises one
non-interactive card invocation.

#### Scenario: Operator plans a bounded batch
- **WHEN** an operator wants to process multiple cards
- **THEN** methodology explains that `$changerail-deliver <board-column>` owns
  one-card-at-a-time queue ordering
- **AND** `bin/changerail-delivery-runner run <card>` is documented as the
  single-card structured-status launcher

### Requirement: Multi-repository workspace delivery default
ChangeRail methodology MUST describe independent child git repositories as the
default delivery unit for aggregator workspaces that contain multiple project
repositories.

#### Scenario: Operator plans parallel work across child repositories
- **WHEN** a workspace root contains multiple independent child git repositories
  with their own `openspec/board/`
- **THEN** methodology treats each child repository as a separate ChangeRail
  consumer and delivery workspace
- **AND** it permits parallel delivery runs across different child repositories
  when each runner uses its own `--workspace`, git scope and runtime status
- **AND** it keeps card delivery sequential inside any one repository

#### Scenario: Root integration remains serialized
- **WHEN** the aggregator root tracks child repositories through submodules,
  gitlinks or a shared integration manifest
- **THEN** root-level integration updates are documented as a separate serialized
  gate after child-repository payloads are published

### Requirement: Deterministic publish finalization helper
ChangeRail methodology MUST allow helper-assisted card finalization after a
reviewed payload commit, as long as the helper changes only deterministic board
metadata and ignored runtime manifest state.

#### Scenario: Payload commit succeeds
- **WHEN** the reviewed payload commit is created for a card in `3.inprogress`
- **THEN** deterministic card metadata may be updated and amended without
  invalidating the reviewed payload
- **AND** the finalization records the final commit/push metadata for the
  operator and future review history

### Requirement: Public-surface scan helper
ChangeRail MUST provide a reusable helper for public-surface scans required by
repository policy.

#### Scenario: Maintainer scans touched public files
- **WHEN** `scripts/public-surface-scan.py` is run against explicit tracked
  paths
- **THEN** it fails on disallowed machine-local `/opt/*` paths
- **AND** it allows documented generic examples such as `/opt/changerail` and
  `/opt/example-project`

#### Scenario: Historical rename references are scanned
- **WHEN** a line contains a documented historical or migration reference to
  `/opt/opsx`
- **THEN** the scanner treats it as allowed
- **AND** non-historical `/opt/opsx` examples remain reviewable findings

#### Scenario: Default public scan covers archived OpenSpec artifacts
- **WHEN** `scripts/public-surface-scan.py` runs without explicit path arguments
- **THEN** it scans the tracked OpenSpec surface including `openspec/changes/archive`
- **AND** a disallowed `/opt/*` path inside an archived change is reported as a
  finding
