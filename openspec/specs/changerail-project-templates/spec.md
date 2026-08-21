# changerail-project-templates Specification

## Purpose
Зафиксировать tracked project template surface, который ChangeRail использует для
создания новых consumer repositories без ручного копирования agent rules,
OpenSpec board и MCP/Codex config.
## Requirements
### Requirement: Project template set
ChangeRail MUST provide a tracked `templates/project/` tree for bootstrapping
generic consumer projects.

#### Scenario: Maintainer inspects project templates
- **WHEN** the `templates/project/` directory is listed
- **THEN** it contains `AGENTS.md.tpl`, `CLAUDE.md.tpl`, `gitignore.tpl`,
  `mcp.json.tpl`, `codex-config.toml.tpl` and an `openspec/` skeleton

### Requirement: Placeholder contract
Project templates MUST document and use stable placeholders for project path,
project name and project kind.
Project templates MUST separate portable tracked scope placeholders from
machine-local absolute path placeholders.

#### Scenario: Bootstrap renders project-local files
- **WHEN** `bootstrap-project` renders templates for `/opt/example-project`
- **THEN** generated project files contain the rendered project path, project
  name and project kind instead of raw placeholder tokens

#### Scenario: Bootstrap renders portable project-local files
- **WHEN** bootstrap renders templates in the default config mode
- **THEN** generated tracked files avoid raw absolute consumer project paths
- **AND** project-local config still scopes filesystem access to the generated
  repository

### Requirement: OpenSpec skeleton
Project templates MUST include a minimal OpenSpec skeleton suitable for a new
consumer repository.

#### Scenario: New project receives OpenSpec layout
- **WHEN** a project is generated from `templates/project/`
- **THEN** it has `openspec/config.yaml`, board columns, `openspec/changes/`
  and `openspec/specs/`

### Requirement: Public-safe template content
Project templates MUST avoid private workspace names, customer data, secrets,
local traces, credentials and runtime reports.
Project templates MUST pin automatically executed npm MCP dependencies to exact
versions represented in a tracked integrity lock that is verified during trusted
setup.

#### Scenario: Public-surface scan covers templates
- **WHEN** templates are prepared for commit
- **THEN** scan output contains only generic examples such as `/opt/changerail` and
  `/opt/example-project`

#### Scenario: Generated MCP dependencies are exact-version pinned
- **WHEN** project templates render `.mcp.json` and `.codex/config.toml`
- **THEN** every automatically executed npm MCP package argument includes an
  exact version
- **AND** the package/version is represented in the tracked MCP npm integrity
  lock
- **AND** `verify-project` can compare that lock entry with npm registry
  `dist.integrity`

### Requirement: Templates render ChangeRail placeholders
Project templates MUST use ChangeRail placeholder names and generated prose
after the rename.

#### Scenario: Template is rendered
- **WHEN** bootstrap renders project templates
- **THEN** placeholders such as `{{CHANGERAIL_ROOT}}` are resolved to the
  configured ChangeRail source-of-truth path
- **AND** generated `AGENTS.md` and `CLAUDE.md` refer to ChangeRail, not OPSX,
  except explicit migration notes

#### Scenario: Claude command list is generated
- **WHEN** `CLAUDE.md` is generated for a consumer project
- **THEN** it lists `/changerail:*` lifecycle commands

### Requirement: Consumer board templates expose current workflow guidance
Project board templates MUST give generated consumers the current ChangeRail
card lifecycle and a canonical pointer to reusable workflow guidance.

#### Scenario: Consumer board README is generated
- **WHEN** `bin/bootstrap-project /opt/example-project` renders the project
  board README
- **THEN** the generated file describes the `1.backlog -> 2.todo ->
  3.inprogress -> 4.done` review-gated lifecycle
- **AND** it points maintainers to the canonical ChangeRail guide or shared
  methodology for the orchestrator, worker and independent reviewer model

#### Scenario: Template content is reviewed for public safety
- **WHEN** project templates are scanned before commit
- **THEN** workflow examples use generic ChangeRail paths such as
  `/opt/changerail` and `/opt/example-project`

### Requirement: Board templates define deliver-ready cards
Project board templates MUST let generated consumer projects prepare
`deliver-ready` cards without creating premature OpenSpec change directories
and without adding another board column.

#### Scenario: Consumer board README is generated
- **WHEN** `bin/bootstrap-project /opt/example-project` renders the project
  board README
- **THEN** the generated file defines `deliver-ready` as an accepted `2.todo`
  card with owner, observable acceptance, ordered change plan, dependencies and
  handoff
- **AND** it states that OpenSpec artifacts are created by `$chrl-deliver` or
  the internal fast-forward phase rather than required before handoff

#### Scenario: Consumer card template is generated
- **WHEN** `bin/bootstrap-project /opt/example-project` renders the board card
  template
- **THEN** the template contains fields and notes sufficient to prepare a
  `deliver-ready` accepted card
- **AND** it does not instruct maintainers to create
  `openspec/changes/<change>/` directories while filling the template

#### Scenario: Board columns are reviewed
- **WHEN** generated board docs describe readiness
- **THEN** the standard board remains five columns from `1.backlog` through
  `5.canceled`
- **AND** no sixth `deliver-ready` column is introduced

### Requirement: Generated workflow guidance remains testable
Project templates MUST render workflow guidance in stable enough terms for
bootstrap smoke to detect lifecycle and review-gated board semantics.

#### Scenario: Consumer project is generated
- **WHEN** bootstrap renders `AGENTS.md` and `openspec/board/README.md`
- **THEN** generated text includes the ChangeRail lifecycle, role model,
  independent review gate and `3.inprogress -> 4.done` finalization boundary

### Requirement: Consumer templates document source classification
Project templates MUST document the optional
`.changerail/source-classification.yaml` review-preflight source classification
file as project-owned tracked configuration. Generated defaults MUST remain
public-safe and MUST NOT declare domain-specific production roots unless the
operator explicitly opts in.

#### Scenario: Consumer guidance is generated
- **WHEN** bootstrap renders a generic consumer project
- **THEN** generated guidance explains that domain-specific production source
  kinds can be declared in `.changerail/source-classification.yaml`
- **AND** the generated content does not hard-code application-specific source
  roots or real customer data

#### Scenario: Consumer does not opt in
- **WHEN** a generated consumer has no source-classification file
- **THEN** review preflight uses the built-in generic classifier
- **AND** bootstrap does not create a false production declaration on behalf of
  the project

### Requirement: Explicit source classification profile lifecycle guidance
Generated project guidance MUST document `detect -> review -> materialize ->
check`, preview-before-write, tracked classification authority, local profile
ownership and explicit migration without hidden stack activation.

#### Scenario: Consumer adds specialized source
- **WHEN** a project or domain integration adds a profile for specialized
  language or structured source
- **THEN** guidance directs maintainers to review candidate signals and preview
  final rules before writing project policy
- **AND** ordinary review and delivery never auto-accept a detected profile

#### Scenario: Existing classification differs
- **WHEN** materialize or check finds an existing divergent project file
- **THEN** guidance requires a separate explicit reviewed migration decision
- **AND** it does not propose force overwrite or automatic Git commit

### Requirement: Generated consumers receive fix-budget recovery guidance
Project templates MUST explain the distinction between implementation fix
cycles and independent-review rescue cycles and MUST retain the shared
autonomous recovery branches.

#### Scenario: Consumer AGENTS guidance is generated
- **WHEN** bootstrap renders `AGENTS.md` for a consumer project
- **THEN** generated guidance identifies `max-fix-cycles` as a pre-review
  implement/verify bound and `max-review-cycles` as a post-review rescue bound
- **AND** it names `fix_budget_exhausted` as a non-delivered handoff

#### Scenario: Generated agent chooses recovery scope
- **WHEN** a generated consumer agent reads the delivery rules after fix-budget
  exhaustion
- **THEN** it is directed to choose bounded same-card micro-fix, linked
  rescue/replacement card or external blocker according to observable scope
- **AND** manual exceptional budget is not described as the default path

### Requirement: Project templates expose verification profile policy
Project templates MUST expose a public-safe verification profile policy in
generated consumer OpenSpec config.
The template MUST preserve strict all-surfaces behavior by default and document
only generic examples for optional or forbidden surfaces.

#### Scenario: Template renders default verification profile
- **WHEN** bootstrap renders `templates/project/openspec/config.yaml.tpl`
- **THEN** the generated `openspec/config.yaml` includes a strict default
  profile for Codex, Claude and legacy MCP surfaces
- **AND** it contains no private workspace names, credentials or runtime state

#### Scenario: Template documents non-blocking diagnostics
- **WHEN** generated consumer guidance is read
- **THEN** it describes that only explicitly non-blocking diagnostics can
  produce `pass-with-diagnostics`
- **AND** it does not describe project-wide baseline debt as silently green

### Requirement: Maintenance template surface is opt-in
Project templates MUST include maintenance policy, catalog and ignore snippets
only through explicit maintenance opt-in rendering.

#### Scenario: Opted-in template is rendered
- **WHEN** bootstrap renders a consumer with `--with-maintenance`
- **THEN** generated tracked maintenance files use public-safe generic
  placeholders and repository-relative paths
- **AND** generated ignored runtime rules cover `.runtime/changerail/maintenance/`

#### Scenario: Non-opted-in template is rendered
- **WHEN** bootstrap renders a consumer without `--with-maintenance`
- **THEN** generated tracked files do not contain maintenance policy skeletons
  or scheduler examples
- **AND** existing template smoke expectations remain valid

### Requirement: Maintenance generated-copy ownership
Project templates MUST allow generated Windows wiring manifests to record
maintenance helper copies as generated-owned artifacts.

#### Scenario: Maintenance helper copy is generated
- **WHEN** native Windows bootstrap writes a maintenance helper copy for an
  opted-in consumer
- **THEN** the generated ownership metadata records the project-relative target
  path, source identity and digest
- **AND** later refresh can update that generated-owned helper without
  overwriting project-owned files

#### Scenario: Maintenance example paths stay public-safe
- **WHEN** template and example files are scanned before commit
- **THEN** maintenance examples use generic paths such as `/opt/changerail` and
  `/opt/example-project`
- **AND** they contain no credentials, local runtime reports or private
  workspace names

### Requirement: Maintenance starter templates cover first scan universe
Opt-in maintenance templates MUST include enough starter catalog and policy
content for the configured initial scan universe to be fully covered.

#### Scenario: Starter catalog covers maintenance configuration
- **WHEN** bootstrap renders a consumer with `--with-maintenance`
- **THEN** `.changerail/knowledge.yaml` contains active catalog records for `.changerail/knowledge.yaml` and `.changerail/maintenance.yaml`
- **AND** those records use repository-relative `source_globs` and public-safe owner metadata

#### Scenario: Starter catalog covers board template
- **WHEN** bootstrap renders a consumer with `--with-maintenance`
- **THEN** `.changerail/knowledge.yaml` contains an active `reference` catalog record for `openspec/board/card-template.md`
- **AND** the record points verification to generic project checks instead of a domain-specific taxonomy

### Requirement: Maintenance starter index is generated
Opt-in maintenance templates or bootstrap rendering MUST provide a current
generated knowledge index matching the rendered starter catalog and policy.

#### Scenario: Generated index matches rendered catalog
- **WHEN** bootstrap renders maintenance starter files
- **THEN** `.changerail/KNOWLEDGE.md` contains deterministic index content for the rendered catalog records
- **AND** `render-index --check` observes no drift before any operator edits

#### Scenario: Starter index remains public-safe
- **WHEN** generated maintenance starter files are scanned before commit
- **THEN** `.changerail/KNOWLEDGE.md` contains only repository-relative paths and generic public-safe text
- **AND** it contains no credentials, runtime report content or private workspace names

### Requirement: Profile-aware consumer templates
Project templates MUST render the selected project topology, surface policy and
Codex authority as observable tracked configuration. Profiles MUST describe
repository ownership and agent authority without generating domain-specific
application code.

#### Scenario: Workspace root profile is rendered
- **WHEN** bootstrap selects `workspace-root`
- **THEN** generated guidance declares aggregator ownership and independent
  child-repository boundaries
- **AND** bootstrap does not create child repositories or application source

#### Scenario: Service profile is rendered
- **WHEN** bootstrap selects `service`
- **THEN** generated guidance declares single-repository delivery ownership
- **AND** no domain framework or deployment configuration is implied

#### Scenario: Codex-only surfaces are rendered
- **WHEN** bootstrap selects `codex-only`
- **THEN** tracked verification policy marks Codex required, Claude optional
  and legacy artifacts forbidden
- **AND** mandatory targeted OpenSpec validation remains required

### Requirement: Explicit Codex authority templates
The Codex config template MUST render `safe-interactive` as
`approval_policy = "on-request"` and `sandbox_mode = "workspace-write"`, and MUST
render `never`/`danger-full-access` only for explicit `trusted-automation`.

#### Scenario: Generic project uses safe authority
- **WHEN** a generic project is rendered with default options
- **THEN** its tracked Codex config does not grant unattended full access

#### Scenario: Automation project records explicit authority
- **WHEN** trusted automation is selected
- **THEN** generated guidance identifies the profile as an explicit operator
  choice and documents its risk boundary

### Requirement: Public-safe consumer CI template
The project template set MUST include an opt-in consumer CI workflow that uses
read-only repository permissions, exact lock-driven ChangeRail checkout and the
same verification commands documented for local consumers.

#### Scenario: CI template is rendered
- **WHEN** bootstrap renders the CI opt-in
- **THEN** `.github/workflows/changerail-consumer-verify.yml` is generated
- **AND** it reads the consumer lock rather than a floating branch

#### Scenario: Workflow authority is inspected
- **WHEN** a maintainer reviews the generated workflow
- **THEN** repository permission is read-only
- **AND** no commit, push, PR, publish or deployment step is present

#### Scenario: Workflow runs without Codex credentials
- **WHEN** baseline CI executes without Codex auth state
- **THEN** static consumer verification can complete
- **AND** no delivery runner is launched

### Requirement: Provider-neutral CI handoff
Generated guidance MUST identify the lock-driven checkout, repair and verify
sequence as the provider-neutral contract even when the initial tracked
template targets GitHub Actions.

#### Scenario: Operator uses another CI provider
- **WHEN** an operator reads generated CI guidance
- **THEN** exact source checkout, disposable wiring repair and verification
  commands are stated independently of GitHub-specific syntax

### Requirement: Optional generated consumer README
The template set MUST provide a minimal public-safe consumer README that is
rendered only through explicit bootstrap opt-in and is never used as an
overwrite source for an existing README.

#### Scenario: README opt-in is rendered
- **WHEN** a new empty consumer selects README generation
- **THEN** the file identifies the project, selected ChangeRail profile and
  local verification command
- **AND** it contains no machine-local path, private remote or credential data

#### Scenario: README already exists
- **WHEN** bootstrap or configure sees an existing README
- **THEN** it preserves the file and reports the ownership conflict rather than
  replacing it

### Requirement: Generated Git handoff guidance
Generated guidance MUST distinguish local Git initialization from commit and
publication and MUST state the exact remaining operator actions.

#### Scenario: Git repository is initialized
- **WHEN** bootstrap performs explicit local Git initialization
- **THEN** completion output states that no files were staged, committed or
  pushed
- **AND** commit/push remain separate operator actions

### Requirement: Instruction-budget-aware templates
Project templates MUST render one explicit instruction budget source of truth
and MUST keep project-specific rules before generated shared methodology so
budget remediation can distinguish the two ownership classes.

#### Scenario: Default template is measured
- **WHEN** bootstrap smoke renders `AGENTS.md`
- **THEN** the UTF-8 byte size is measured against the tracked Codex budget
- **AND** the fixture fails if default content reaches the 85 percent warning
  threshold

#### Scenario: Project rules approach the budget
- **WHEN** a fixture expands project-specific instructions past 85 percent but
  not beyond the budget
- **THEN** verification emits a non-blocking warning naming both measured and
  allowed bytes

### Requirement: Runtime evidence guidance is public-safe
Templates MUST state that raw Codex diagnostic output remains ignored and that
only allowlisted redacted fields may appear in reports, cards or documentation.

#### Scenario: Runtime guidance is scanned
- **WHEN** public-surface checks inspect generated guidance
- **THEN** it contains no example credential, private home path or raw doctor
  output

### Requirement: Board cards declare review risk
Generated and source board card templates MUST provide a concise review section
for risk and rescue-complexity declarations, including a
`Published investigation authorization` field whose default is `none`. The
field MUST document that any non-default value is one inline JSON reference to
a published authorization source; template prose MUST NOT imply that arbitrary
text authorizes a complexity exception.

#### Scenario: Agent creates a card from the template
- **WHEN** a new card is created from a ChangeRail board template
- **THEN** the card exposes risk tier, milestone audit, authority/protocol,
  credential/mutation-authority, repeated-defect, live-admission and
  final-certification and published-investigation authorization fields
- **AND** ordinary is the backward-compatible default risk

### Requirement: Consumer adoption migration guidance
Consumer adoption guidance MUST document the explicit lockless migration flow,
dry-run review, verification command and rollback boundary using only
public-safe generic examples.

#### Scenario: Operator reads lockless migration guidance
- **WHEN** an operator opens the consumer adoption runbook
- **THEN** it describes the difference between lockless compatibility,
  lockless adoption and lock-owned refresh
- **AND** it shows a generic dry-run command before the apply command
- **AND** it states that normal `--refresh-wiring` remains fail-closed without a
  consumer lock

#### Scenario: Rollback guidance is documented
- **WHEN** adoption fails or an operator decides not to keep the migration
- **THEN** the runbook identifies which tracked files may have been created by
  adoption
- **AND** it states that project-owned instructions, config, auth, source,
  board cards and unrelated Git state are outside migration scope

#### Scenario: Guidance stays public-safe
- **WHEN** migration docs and generated guidance are scanned before commit
- **THEN** examples use generic paths such as `/opt/changerail` and
  `/opt/example-project`
- **AND** they contain no private consumer names, raw field-validation logs,
  credentials or machine-local runtime reports

### Requirement: Templates SHALL expose optional execution target declaration
Project templates SHALL документировать schema-valid optional
`.changerail/execution-target.json` без platform-specific defaults, endpoint,
credentials или generated target identity.

#### Scenario: Project adopts target binding
- **WHEN** maintainer добавляет declaration из generic template/example
- **THEN** файл содержит только logical id, fingerprint и forbid policy
- **AND** project-owned process отвечает за значения и oracle evidence

#### Scenario: Project does not need target binding
- **WHEN** declaration не добавлена
- **THEN** bootstrap и verification сохраняют legacy-compatible behavior

### Requirement: Optional verification coverage configuration
Bootstrapped project guidance MUST показывать verification coverage как explicit
optional tracked config reference и MUST описывать map как project-owned policy,
а не ChangeRail global test catalog.

#### Scenario: Новый consumer не включает coverage map
- **WHEN** project bootstrapped без project-specific map
- **THEN** existing strict verification profile и mandatory targeted OpenSpec
  validation не меняются
- **AND** placeholder coverage rule не считается mandatory

#### Scenario: Consumer включает coverage map
- **WHEN** maintainers добавляют tracked map reference и schema-valid entries
- **THEN** guidance объясняет planning/evidence/review flow и namespaced
  extension ownership
- **AND** examples используют только generic project paths и synthetic data
