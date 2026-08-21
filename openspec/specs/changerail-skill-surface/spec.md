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
`changerail-pub` MUST fail closed for review-gated cards when a fresh
risk-appropriate payload gate is absent or stale. Deterministic/process payloads
may use a fresh `machine-reviewed` preflight receipt; ordinary and critical
payloads require a fresh valid `go` verdict.

#### Scenario: Publish runs without a valid review gate
- **WHEN** publish is invoked for a delivered card without its risk-appropriate
  fresh machine receipt or `go` verdict
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
- **THEN** the default autonomous policy allows two bounded same-card rescue
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

### Requirement: Deliver accepts artifact-pending accepted cards
`changerail-deliver` MUST accept a scoped accepted card with an ordered change
plan as the normal start point even when card-owned OpenSpec artifacts do not
exist yet.

#### Scenario: Deliver starts from planned todo card
- **WHEN** an operator invokes `$changerail-deliver <card>` for a card in
  `2.todo` that has ordered `## Change N:` sections but no active
  `openspec/changes/<change>/` directory
- **THEN** the deliver workflow runs its fast-forward phase to create or
  complete apply-ready artifacts
- **AND** it does not stop solely because artifacts were absent before
  invocation

#### Scenario: Fast-forward remains planning-only
- **WHEN** the deliver workflow invokes or performs the fast-forward phase
- **THEN** that phase creates or updates board/card and OpenSpec artifacts only
- **AND** implementation, archive, review and publish remain responsibilities
  of the later lifecycle phases

### Requirement: Phase skills remain explicit recovery surfaces
ChangeRail lifecycle skill wording MUST distinguish the normal one-command
handoff from explicit phase command usage.

#### Scenario: Skill guidance names the normal path
- **WHEN** an agent reads `changerail-deliver` or `changerail-ff` guidance
- **THEN** the guidance identifies `$changerail-deliver <card>` as the normal
  operator handoff for an accepted ordered card
- **AND** it keeps `$changerail-ff`, `$changerail-do`, `$changerail-review` and
  `$changerail-pub` available for repair, debug or manual resume

#### Scenario: Fast-forward completes independently
- **WHEN** `$changerail-ff <card>` is invoked directly
- **THEN** its output hands off to `$changerail-do <card>` for explicit phase
  continuation
- **AND** it does not imply that direct fast-forward was required before
  `$changerail-deliver <card>` could have started

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

### Requirement: Reviewer protects parent-owned active runner evidence
`changerail-review` and the fresh-review launch contract MUST treat an active
runner directory identified by `CHANGERAIL_ACTIVE_RUN_DIR` as parent-owned
evidence until the child delivery run terminates.

#### Scenario: Reviewer runs inside a live delivery child
- **WHEN** an independent reviewer is launched while the parent delivery run is
  still active
- **THEN** the reviewer excludes the active runner directory from discovery
- **AND** it does not read, search, tail, cite or summarize `status.json`, raw
  runtime logs or other files under that directory
- **AND** it audits the card, manifest, preflight, reviewed tree and retained
  card-owned evidence outside the protected directory
- **AND** a mandatory claim backed only by protected active-run output is
  recorded as unbacked rather than justified from that output

### Requirement: Publish finalizes board metadata deterministically
`changerail-pub` MUST define deterministic board finalization behavior for
review-gated cards after the reviewed payload commit succeeds, while keeping
tracked card metadata stable and storing exact mutable publication details in
ignored runtime manifest evidence.

#### Scenario: Publish commits reviewed payload
- **WHEN** `changerail-pub` commits a reviewed card payload
- **THEN** it finalizes the board card into `4.done`, records stable completion
  metadata, and amends only card metadata when required by board protocol
- **AND** it does not make substantive code, docs, specs, schema, script or
  test edits after the fresh `go` verdict
- **AND** it does not write the card's own exact final commit hash or mutable
  push status into tracked done-card text
- **AND** it records payload commit, final published commit, remote, branch,
  status and timestamps in the ignored delivery manifest when available

### Requirement: Bundled skill frontmatter is valid YAML
ChangeRail bundled skills MUST have YAML-valid frontmatter metadata before they
are published as part of the generic skill surface.

#### Scenario: Maintainer validates bundled skills
- **WHEN** release verification inspects `skills/*/SKILL.md`
- **THEN** every skill frontmatter parses as a YAML mapping
- **AND** each parsed `name` value matches the bundled skill directory name

#### Scenario: Lifecycle skill description contains colon
- **WHEN** a lifecycle skill description needs text containing `: `
- **THEN** the frontmatter represents that value in a YAML-valid form such as a
  quoted scalar

### Requirement: Skill metadata validation is local and deterministic
ChangeRail skill metadata validation MUST NOT depend on networked Codex
discovery, live credentials or external agent runtime diagnostics.

#### Scenario: Release gate checks skills without Codex credentials
- **WHEN** the local release baseline validates skill metadata
- **THEN** it runs a repository-local parser check
- **AND** it can fail invalid frontmatter before any networked `codex exec`
  discovery attempt would be needed

### Requirement: Maintain skill surface
ChangeRail MUST provide tracked generic source skills for canonical
`changerail-maintain` and short alias `chrl-maintain`, plus Claude command
wrappers for `/changerail:maintain` and `/chrl:maintain`.

#### Scenario: Codex discovers maintain skills
- **WHEN** Codex skill discovery reads the repository skill surface
- **THEN** it finds `changerail-maintain` and `chrl-maintain`
- **AND** `chrl-maintain` delegates to the canonical `changerail-maintain`
  contract without introducing a separate runtime namespace

#### Scenario: Claude discovers maintain commands
- **WHEN** Claude command discovery reads the repository command surface
- **THEN** it finds `/changerail:maintain` and `/chrl:maintain`
- **AND** the short wrapper delegates to the canonical maintain command

### Requirement: Maintain modes preserve lifecycle boundaries
`changerail-maintain` MUST expose only `audit` and `triage` modes, and MUST NOT
perform delivery, publish or fix work.

#### Scenario: Audit mode is invoked
- **WHEN** an agent follows `changerail-maintain audit`
- **THEN** it runs or consumes deterministic repository maintenance scan/report
  output
- **AND** it does not write tracked files, board cards, baseline files,
  delivery manifests, publish records or external systems

#### Scenario: Triage mode is invoked
- **WHEN** an agent follows `changerail-maintain triage`
- **THEN** it may write only schema-valid annotations and previews below ignored
  maintenance runtime state
- **AND** it does not commit, push, publish or mutate tracked board cards by
  default

### Requirement: Maintain mutation requests route through card flow
`changerail-maintain` MUST treat requests to fix findings, publish changes or
perform tracked repository mutation as a handoff to normal ChangeRail card
delivery until an explicit fix mode is delivered.

#### Scenario: User requests fix through maintain
- **WHEN** a user asks `changerail-maintain` to fix a maintenance finding
- **THEN** the skill states that fix mode is not available yet
- **AND** it routes the work to a normal ChangeRail board card and
  `$changerail-deliver` handoff

#### Scenario: User requests card writes during triage
- **WHEN** a user explicitly supplies a tracked card-write intent such as
  `--write-cards`
- **THEN** the skill may delegate only to `bin/changerail-maintenance cards
  --write`
- **AND** it still does not commit, push or publish the resulting board change
  without the normal delivery/review/publish flow

### Requirement: Review skill runs deterministic preflight first
The canonical review and deliver skills MUST run deterministic review preflight
before launching an independent LLM payload reviewer.

#### Scenario: Preflight returns a process blocker
- **WHEN** preflight reports a manifest, board, archive, scope, freshness or
  locally available strict-check defect
- **THEN** the lifecycle returns the machine blocker to delivery
- **AND** it does not launch an LLM or consume implementation review budget

#### Scenario: Preflight routes semantic review
- **WHEN** machine gates pass and semantic payload review is required
- **THEN** the lifecycle uses `high` for ordinary risk or `xhigh` for critical
  risk
- **AND** no generic model-launch layer is required

### Requirement: Delivery discovery output remains bounded
ChangeRail delivery skills MUST instruct delivery agents to start repository
discovery with scoped, low-output commands before reading broad command output.

#### Scenario: Delivery child searches implementation evidence
- **WHEN** a delivery child needs to inspect implementation state
- **THEN** the delivery skill directs it to prefer scoped paths, file-name
  discovery, counts or bounded excerpts before broad content searches
- **AND** the skill directs the child to narrow follow-up reads to files or
  ranges needed for the current card-owned change

#### Scenario: Search scope is not yet known
- **WHEN** a delivery child cannot identify the relevant paths from the card,
  OpenSpec artifacts or project context
- **THEN** the delivery skill directs it to perform bounded discovery such as
  top-level file lists, targeted spec references or `rg -l` before requesting
  full matching-line output

### Requirement: Truncated discovery output is inconclusive evidence
ChangeRail delivery skills MUST forbid using truncated command output as proof
that implementation is present or absent.

#### Scenario: Search output is truncated
- **WHEN** a command exits because output was truncated or produces an
  incomplete excerpt
- **THEN** the delivery skill directs the agent to treat the result as
  inconclusive
- **AND** the agent must collect narrower structured evidence before recording
  an acceptance, verification or absence claim

#### Scenario: Truncated output includes apparent matches
- **WHEN** truncated output contains some matching lines
- **THEN** the delivery skill directs the agent to verify the relevant files
  directly instead of inferring full implementation coverage from the truncated
  stream

### Requirement: Lifecycle skills MUST enforce target identity handoff
Canonical `ff`, `do`, `review`, `pub` и `deliver` skills MUST требовать
captured target identity и matching evidence при наличии project declaration и
MUST запрещать implicit substitution.

#### Scenario: Planning and delivery handoff target identity
- **WHEN** project объявил execution target
- **THEN** planning фиксирует identity в delivery scope
- **AND** delivery сохраняет matching evidence или structured blocker

#### Scenario: Reviewer видит mismatch
- **WHEN** manifest, current declaration и evidence target identities не
  совпадают
- **THEN** deterministic preflight блокирует semantic review/publish
- **AND** remediation не предлагает создать substitute target

### Requirement: Lifecycle skill coverage responsibilities
Canonical skills `changerail-ff`, `changerail-do` и `changerail-review` MUST
обрабатывать project coverage map через единый plan/ledger contract и MUST NOT
копировать raw evidence или создавать alternative acceptance verdict.

#### Scenario: Fast-forward планирует configured coverage
- **WHEN** `changerail-ff` обрабатывает card в project с valid map
- **THEN** он пишет schema-valid per-change coverage reference после определения
  proposal/design scope
- **AND** selected ids/hash references соответствуют map/card sources

#### Scenario: Review получает incomplete ledger
- **WHEN** independent review видит applicable rule с missing/invalid evidence
  или oracle, не наблюдающий claimed boundary
- **THEN** skill записывает blocker evidence/test-adequacy finding
- **AND** не отмечает acceptance pass только по наличию path/command
