# changerail-skill-surface Specification

## Purpose
Зафиксировать минимальный public source surface для generic ChangeRail skills и
Claude command wrappers: какие skills поставляются первыми, какие boundaries у
planning-only flow и какие path-neutrality требования должны соблюдаться до
подключения bootstrap/adoption wiring.
## Requirements
### Requirement: Minimal generic ChangeRail skills
ChangeRail MUST provide tracked generic source skills for `changerail-explore`, `changerail-ff`,
`changerail-do`, `changerail-review`, `changerail-pub` and `changerail-deliver`.

#### Scenario: Consumer project links ChangeRail lifecycle skills
- **WHEN** consumer project symlinks or copies ChangeRail skill source files
- **THEN** all generic ChangeRail lifecycle skills are available from `skills/`

### Requirement: Path-neutral skill content
ChangeRail skill source files MUST avoid private workspace names, machine-specific
fallback paths, customer data, secrets and domain-specific provider policy.

#### Scenario: Public-surface scan runs before publication
- **WHEN** skill files are scanned for private local paths and workspace names
- **THEN** no private machine-local source path appears in the generic skill
  surface

### Requirement: Explore remains non-implementation mode
`changerail-explore` MUST describe an exploration workflow that reads relevant project
context and helps shape the problem without implementing product/runtime
changes.

#### Scenario: User invokes explore for an unclear requirement
- **WHEN** agent follows `changerail-explore`
- **THEN** agent investigates, compares options and recommends next artifacts
  without applying code changes

### Requirement: Fast-forward remains planning-only
`changerail-ff` MUST describe a card planning workflow that decomposes stories and
creates apply-ready OpenSpec artifacts without implementing, archiving or
publishing.

#### Scenario: User invokes fast-forward for a board card
- **WHEN** agent follows `changerail-ff`
- **THEN** agent updates the card and OpenSpec change artifacts while leaving
  implementation to a later delivery workflow

### Requirement: Claude wrappers for minimal commands
ChangeRail MUST provide Claude command wrapper source files for `/changerail:explore`,
`/changerail:ff`, `/changerail:do`, `/changerail:review`, `/changerail:pub` and `/changerail:deliver`.

#### Scenario: Consumer project wires Claude commands
- **WHEN** consumer project links `claude/commands/changerail/`
- **THEN** source wrappers exist for the generic ChangeRail lifecycle commands

### Requirement: Claude wrappers use skill discovery
Claude command wrappers MUST load ChangeRail skills by name or by the consumer's
Claude skill discovery mechanism, not by assuming a root-level `skills/` path in
the consumer repository.

#### Scenario: Consumer project links commands and skills through documented wiring
- **WHEN** consumer project exposes ChangeRail commands under `.claude/commands/changerail`
  and skills under `.claude/skills`
- **THEN** `/changerail:explore` and `/changerail:ff` do not require a separate
  `<consumer-root>/skills` symlink

### Requirement: Fast-forward handoff is conditional
`changerail-ff` MUST hand off to the delivery workflow without requiring `changerail-do` to
be installed by the minimal skill surface.

#### Scenario: Minimal skill surface is installed without delivery commands
- **WHEN** `changerail-ff` finishes planning a card
- **THEN** it may name `$changerail-do` or `/changerail:do` only as the delivery command to
  use when that surface is installed

### Requirement: Delivery skill implements generic do flow
`changerail-do` MUST describe a supervised delivery workflow that implements ordered
card-owned OpenSpec changes, verifies them, syncs specs and archives completed
changes without committing or publishing.

#### Scenario: Agent invokes delivery for a planned card
- **WHEN** agent follows `changerail-do` for a card with apply-ready changes
- **THEN** the agent processes each card-owned change through implementation,
  verification, spec sync and archive before handing off to review

### Requirement: Review skill enforces independent gate
`changerail-review` MUST require a fresh context that did not plan or implement the
card and MUST write only an ignored runtime verdict file.

#### Scenario: Implementing session attempts self-review
- **WHEN** the current session produced the diff under review
- **THEN** `changerail-review` stops before writing a verdict

### Requirement: Publish skill requires review gate by default
`changerail-pub` MUST fail closed for review-gated cards when a fresh valid `go`
verdict is absent or stale.

#### Scenario: Publish runs without a valid review verdict
- **WHEN** publish is invoked for a delivered card without a fresh `go` verdict
- **THEN** publish stops before staging, committing or pushing files

### Requirement: Deliver skill orchestrates the lifecycle
`changerail-deliver` MUST orchestrate the card-level flow `ff -> do -> review -> pub`
while preserving phase safety stops, scoped publish behavior and autonomous
repeated-`NO-GO` escalation.

#### Scenario: Deliver reaches an external review stop
- **WHEN** an operator requires external review instead of self-launched review
- **THEN** `changerail-deliver` stops at the review gate and prints the review and
  resume commands without publishing

#### Scenario: Deliver uses the default review rescue budget
- **WHEN** `changerail-deliver` receives consecutive `no-go` review verdicts
- **THEN** the default autonomous policy allows five bounded same-card rescue
  attempts after the first `no-go`
- **AND** each rescue attempt still requires a fresh independent re-review
  before publish

#### Scenario: Deliver exhausts the same-card rescue budget
- **WHEN** the default same-card rescue budget is exhausted and review still
  returns `no-go`
- **THEN** `changerail-deliver` MUST stop publishing that payload
- **AND** the lifecycle instructions MUST direct the orchestrator to create a
  linked rescue/replacement card with prior cycle history instead of requesting
  manual exceptional authorization

#### Scenario: Deliver detects repeated lineage blockers
- **WHEN** linked replacement/rescue cards repeatedly return the same blocker
  class or unresolved invariant
- **THEN** lifecycle instructions MUST direct the orchestrator to create an
  investigation/design card before further implementation rescue work

### Requirement: Delivery skills hand off fix-budget exhaustion structurally
`changerail-do` and `changerail-deliver` MUST use a shared structured handoff
when the pre-review fix budget is exhausted, while keeping the independent
review rescue budget separate.

#### Scenario: Do exhausts its fix budget
- **WHEN** `changerail-do` reaches `--max-fix-cycles` without completing
  verification
- **THEN** it MUST stop the phase with `terminal_outcome: BLOCKED` and
  `terminal_reason: fix_budget_exhausted`
- **AND** it MUST report remaining findings and evidence without requesting an
  exceptional manual budget as the default continuation

#### Scenario: Deliver receives fix-budget exhaustion
- **WHEN** supervising `changerail-deliver` receives the structured
  `fix_budget_exhausted` handoff
- **THEN** it MUST classify the remaining work as bounded same-card micro-fix,
  linked rescue/replacement work or external blocker
- **AND** it MUST NOT count that handoff as an independent-review `NO-GO`

#### Scenario: Bounded continuation still cannot verify
- **WHEN** a bounded same-card micro-fix does not reach its concrete
  verification target
- **THEN** the lifecycle MUST stop or create a linked recovery card according
  to scope instead of extending the local loop without a bound

### Requirement: Delivery skills preserve review-gated lifecycle
ChangeRail lifecycle skills MUST keep implementation, independent review and publish
as separate gates with explicit card-state responsibilities.

#### Scenario: Delivery hands off without done move
- **WHEN** `changerail-do` completes and archives all card-owned changes
- **THEN** it records verification and archive evidence but does not move the
  card to `4.done`

#### Scenario: Publish performs final board transition
- **WHEN** `changerail-pub` has a fresh valid `go` verdict and publishes the scoped
  payload
- **THEN** it performs only the documented board finalization needed to mark the
  story done

### Requirement: Delivery and review audit mandatory verification
`changerail-do` MUST collect mandatory verification from local rules and artifacts,
and `changerail-review` MUST audit whether mandatory verification claims are backed by
concrete evidence.

#### Scenario: Delivery hands off evidence
- **WHEN** `changerail-do` completes a change with mandatory checks
- **THEN** the card, tasks or delivery manifest contains command/outcome
  evidence for those checks

#### Scenario: Review finds an unbacked mandatory claim
- **WHEN** `changerail-review` sees a mandatory verification claim without concrete
  command/outcome evidence
- **THEN** it records a finding instead of treating the claim as proven

### Requirement: ChangeRail lifecycle skill namespace
The generic lifecycle skill surface MUST use `changerail-*` skill names and
`/changerail:*` Claude commands as the canonical invocation namespace.

#### Scenario: Codex discovers lifecycle skills
- **WHEN** Codex skill discovery reads the repository skill surface
- **THEN** it finds `changerail-explore`, `changerail-ff`, `changerail-do`,
  `changerail-review`, `changerail-pub` and `changerail-deliver`
- **AND** it does not require `opsx-*` lifecycle skill names for new defaults

#### Scenario: Claude discovers lifecycle commands
- **WHEN** Claude command discovery reads the repository command surface
- **THEN** it finds `/changerail:explore`, `/changerail:ff`,
  `/changerail:do`, `/changerail:review`, `/changerail:pub` and
  `/changerail:deliver`
- **AND** new generated projects do not install `/opsx:*` command defaults

### Requirement: OpenSpec lifecycle namespace is preserved
ChangeRail MUST keep OpenSpec lifecycle skills under the `openspec-*`
namespace.

#### Scenario: OpenSpec skills are discovered after rename
- **WHEN** Codex or Claude loads ChangeRail project skills
- **THEN** OpenSpec artifact lifecycle skills remain named `openspec-*`
- **AND** `bin/openspec` remains the pinned OpenSpec CLI wrapper

### Requirement: Short ChangeRail lifecycle aliases
ChangeRail MUST provide official short `chrl-*` Codex skill aliases and
`/chrl:*` Claude command aliases for every canonical generic ChangeRail
lifecycle command.

#### Scenario: Codex discovers short lifecycle aliases
- **WHEN** Codex skill discovery reads the repository skill surface
- **THEN** it finds `chrl-explore`, `chrl-ff`, `chrl-do`, `chrl-review`,
  `chrl-pub` and `chrl-deliver`
- **AND** canonical `changerail-explore`, `changerail-ff`, `changerail-do`,
  `changerail-review`, `changerail-pub` and `changerail-deliver` remain
  available

#### Scenario: Claude discovers short lifecycle aliases
- **WHEN** Claude command discovery reads the repository command surface
- **THEN** it finds `/chrl:explore`, `/chrl:ff`, `/chrl:do`,
  `/chrl:review`, `/chrl:pub` and `/chrl:deliver`
- **AND** canonical `/changerail:explore`, `/changerail:ff`,
  `/changerail:do`, `/changerail:review`, `/changerail:pub` and
  `/changerail:deliver` remain available

### Requirement: Short aliases delegate to canonical contracts
Short `chrl-*` and `/chrl:*` aliases MUST delegate to the matching canonical
`changerail-*` lifecycle contract without duplicating lifecycle logic or
introducing a separate runtime namespace.

#### Scenario: Agent opens a short alias skill
- **WHEN** an agent reads `skills/chrl-do/SKILL.md`
- **THEN** the file identifies `chrl-do` as an alias for `changerail-do`
- **AND** it directs the agent to follow the canonical `changerail-do` contract

#### Scenario: User invokes a short Claude command
- **WHEN** a Claude user invokes `/chrl:review`
- **THEN** the wrapper delegates to the canonical `/changerail:review`
  contract
- **AND** review verdict schema ids and runtime paths remain under the
  `changerail` namespace

### Requirement: Lifecycle skills expose role boundaries
ChangeRail lifecycle skills MUST make the orchestrator, delivery worker and
reviewer boundaries visible in the phase where they matter.

#### Scenario: Deliver orchestrates a card
- **WHEN** an agent follows `changerail-deliver`
- **THEN** the skill describes itself as the supervised orchestrator for the
  card pipeline
- **AND** it states that implementation may run in the same active context
  while review must run in a fresh context

#### Scenario: Delivery hands off to review
- **WHEN** `changerail-do` completes a review-gated card
- **THEN** the skill output and handoff instructions send the card to
  `changerail-review` rather than self-review or publish

#### Scenario: Review is invoked
- **WHEN** an agent follows `changerail-review`
- **THEN** the skill requires a fresh reviewer context and stops on
  self-review

### Requirement: Review skill writes independence evidence
`changerail-review` MUST instruct reviewers to include the required
independence attestation in the canonical review verdict.

#### Scenario: Fresh reviewer writes a verdict
- **WHEN** `changerail-review` produces a verdict
- **THEN** the verdict includes machine-readable independence attestation
- **AND** the skill output identifies the reviewer context as fresh or stops
  before writing a verdict

### Requirement: Deliver provides fresh-review launch contract
`changerail-deliver` MUST provide a standard fresh-review launch contract for
the independent review phase.

#### Scenario: Deliver reaches review gate
- **WHEN** `changerail-deliver` reaches a card's review phase without an
  existing fresh verdict
- **THEN** the skill provides a ready-to-run reviewer prompt or invocation
  contract that includes scope, forbidden writes, verdict path and
  `reviewer.independence` requirements
- **AND** the orchestrator validates the resulting verdict with `--check-fresh`
  before continuing to publish

### Requirement: Publish finalizes board metadata deterministically
`changerail-pub` MUST define deterministic board finalization behavior for
review-gated cards after the reviewed payload commit succeeds.

#### Scenario: Publish commits reviewed payload
- **WHEN** `changerail-pub` commits a reviewed card payload
- **THEN** it finalizes the board card into `4.done`, records commit/push
  metadata, and amends only card metadata when required by board protocol
- **AND** it does not make substantive code, docs, specs, schema, script or
  test edits after the fresh `go` verdict
