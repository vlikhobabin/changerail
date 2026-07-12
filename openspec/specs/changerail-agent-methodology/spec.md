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

#### Scenario: Ревью публичного репозитория
- **WHEN** `AGENTS.shared.md` reviewed before commit
- **THEN** file contains only generic ChangeRail rules and documented example paths
  such as `/opt/changerail` and `/opt/example-project`

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
