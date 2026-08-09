# changerail-project-bootstrap Specification

## Purpose
Зафиксировать command-line bootstrap flow, который создает generic ChangeRail
consumer project из tracked templates, ChangeRail source-of-truth symlink-ов и
немедленно проверяет результат через `verify-project`.
## Requirements
### Requirement: Bootstrap project command
ChangeRail MUST provide `bin/bootstrap-project` to create a new generic consumer
project from tracked templates and ChangeRail source-of-truth symlink-и.
Bootstrap MUST generate public-safe portable tracked configuration by default
and expose local absolute-path configuration only through explicit operator
opt-in.

#### Scenario: Operator bootstraps a generic project
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name
  example-project --kind generic`
- **THEN** the target receives generated project files, ChangeRail symlink-и, helper
  wrappers and an OpenSpec skeleton

#### Scenario: Default bootstrap creates portable tracked config
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name
  example-project --kind generic`
- **THEN** the generated tracked files use portable project scope instead of a
  machine-local absolute target path
- **AND** bootstrap still creates the required ChangeRail symlinks and helper
  wrappers

#### Scenario: Operator explicitly opts into local config
- **WHEN** an operator runs bootstrap with local absolute config mode
- **THEN** bootstrap renders machine-local absolute paths only after explicit
  opt-in
- **AND** it prints a warning before the suggested `git add` command

### Requirement: Refuse existing targets by default
Bootstrap MUST refuse to overwrite an existing non-empty target unless the
operator explicitly requests backup mode.

#### Scenario: Target already contains files
- **WHEN** bootstrap is run for a non-empty existing target without
  `--backup-existing`
- **THEN** bootstrap exits non-zero before changing the target

### Requirement: Dry-run mode
Bootstrap MUST support a dry-run mode that reports planned operations without
creating or modifying the target project.

#### Scenario: Operator previews bootstrap
- **WHEN** bootstrap is run with `--dry-run`
- **THEN** planned file, directory and symlink actions are printed and the
  target project is not created

### Requirement: Bootstrap verification handoff
Bootstrap MUST run `verify-project` after generating a project unless the
operator explicitly skips verification for diagnostics.
Bootstrap verification MUST validate the config model produced by bootstrap
before reporting success.

#### Scenario: Generated project is verified
- **WHEN** bootstrap completes project generation
- **THEN** it runs `bin/verify-project <target>` and fails if verification
  fails

#### Scenario: Portable generated project is verified
- **WHEN** bootstrap completes default portable project generation
- **THEN** it runs `bin/verify-project <target>` and fails if portable scope
  validation fails

### Requirement: Bootstrap smoke evidence
ChangeRail MUST provide smoke coverage that exercises bootstrap end-to-end under
ignored runtime space.

#### Scenario: Bootstrap smoke runs
- **WHEN** `python3 scripts/smoke-bootstrap-project.py` runs
- **THEN** it creates a temporary consumer under `.runtime`, verifies it and
  writes any report under ignored runtime space

### Requirement: Bootstrap creates ChangeRail consumers
Bootstrap MUST generate new generic consumers wired to the ChangeRail source of
truth.

#### Scenario: Operator bootstraps a post-rename project
- **WHEN** an operator runs bootstrap with `/opt/changerail` as the source of
  truth
- **THEN** the generated project uses `/opt/changerail` in generated docs and
  config
- **AND** generated helper symlinks point to ChangeRail helper wrappers

#### Scenario: Existing target is non-empty
- **WHEN** bootstrap is run for a non-empty existing target
- **THEN** bootstrap continues to refuse overwrite unless explicit backup mode
  is requested

### Requirement: Bootstrap installs short ChangeRail aliases
Bootstrap MUST generate new consumer projects with both canonical
`changerail-*` wiring and short `chrl-*` wiring for ChangeRail lifecycle
commands.

#### Scenario: Operator bootstraps a project with alias wiring
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name
  example-project --kind generic`
- **THEN** the target receives `.codex/skills/chrl-*` entries for all generic
  ChangeRail lifecycle skills
- **AND** the target receives `.claude/commands/chrl` for all generic
  ChangeRail lifecycle commands
- **AND** canonical `changerail-*` wiring remains present

#### Scenario: Bootstrap dry-run reports alias wiring
- **WHEN** bootstrap is run with `--dry-run`
- **THEN** the planned operations include the short `chrl-*` Codex skill
  entries and `/chrl:*` Claude command directory

### Requirement: Bootstrap smoke checks workflow guidance
Bootstrap smoke MUST verify that generated consumer files include current
ChangeRail workflow guidance.

#### Scenario: Bootstrap smoke renders a generic consumer
- **WHEN** `python3 scripts/smoke-bootstrap-project.py` runs
- **THEN** it checks generated `AGENTS.md` and `openspec/board/README.md`
- **AND** it fails if lifecycle, role model, fresh review gate or board
  finalization guidance is missing

### Requirement: Bootstrap Codex auth handoff documentation
Bootstrap guidance MUST explain that generated consumers keep Codex auth state
ignored and that delivery runner auth setup is an explicit local operator
handoff.

#### Scenario: Operator reads bootstrap guidance
- **WHEN** an operator bootstraps or adopts a consumer project
- **THEN** the guidance states that `.codex/auth.json` and `.codex/auth.toml`
  must remain ignored and untracked
- **AND** it explains that bootstrap does not silently copy credentials by
  default
- **AND** it points to the manual or opt-in setup path for delivery runner auth
  readiness

### Requirement: Opt-in Codex auth symlink setup
Bootstrap MUST support an explicit operator opt-in for linking a generated
consumer's ignored Codex auth marker to an existing local auth file without
copying credentials.

#### Scenario: Default bootstrap does not link auth
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name
  example-project --kind generic` without an auth link option
- **THEN** bootstrap does not create `.codex/auth.json`
- **AND** generated `.gitignore` keeps supported auth markers such as
  `.codex/auth.json` and `.codex/auth.toml` ignored

#### Scenario: Operator links an existing auth file
- **WHEN** an operator runs bootstrap with `--link-codex-auth
  $HOME/.codex/auth.json`
- **THEN** bootstrap creates `/opt/example-project/.codex/auth.json` as a
  symlink to the supplied source
- **AND** bootstrap does not read or print credential contents

#### Scenario: Auth link source is missing
- **WHEN** an operator supplies `--link-codex-auth` with a missing source path
- **THEN** bootstrap exits non-zero before reporting success
- **AND** it does not create a dangling auth marker by default

#### Scenario: Dry-run reports auth link plan
- **WHEN** an operator runs bootstrap with `--dry-run --link-codex-auth
  $HOME/.codex/auth.json`
- **THEN** bootstrap prints a planned auth symlink operation
- **AND** it writes no target files

### Requirement: Bootstrap renders default verification profile policy
Bootstrap MUST render generated consumer OpenSpec config with an explicit
verification policy that preserves the strict all-surfaces default.
The generated policy MUST be tracked project configuration, not ignored runtime
state.

#### Scenario: Generated project receives strict verification policy
- **WHEN** `bin/bootstrap-project /opt/example-project --name example-project
  --kind generic` renders a consumer project
- **THEN** `openspec/config.yaml` declares the default verification profile as
  strict all-surfaces
- **AND** `bin/verify-project /opt/example-project` treats missing canonical
  ChangeRail surfaces as blocking failures unless the tracked project policy is
  changed

#### Scenario: Bootstrap smoke verifies generated policy
- **WHEN** `python3 scripts/smoke-bootstrap-project.py` runs
- **THEN** it verifies the generated default verification profile policy through
  `bin/verify-project`

### Requirement: Bootstrap guidance documents profile override boundary
Bootstrap guidance MUST explain that consumers may opt into Codex-only or other
profile policies only by editing tracked project policy, and that targeted
card-owned validation cannot be made non-blocking.

#### Scenario: Operator reads generated guidance
- **WHEN** an operator inspects generated consumer guidance
- **THEN** the guidance identifies `required`, `optional` and `forbidden`
  surface states
- **AND** it states that profile policy can produce
  `pass-with-diagnostics` only for non-blocking findings
- **AND** it states that targeted card-owned OpenSpec validation remains
  mandatory

### Requirement: Native Windows generated wiring backend
Bootstrap MUST select generated project-local wiring as the default backend on
native Windows without requiring Developer Mode, administrator elevation,
symlink privileges or junction traversal.

#### Scenario: Native Windows bootstrap selects generated wiring
- **WHEN** an operator runs `bin/bootstrap-project` for a generic consumer on a
  native Windows platform without an explicit wiring override
- **THEN** bootstrap creates generated project-local command, skill and helper
  wiring artifacts
- **AND** it does not create symlinks or junctions for ChangeRail wiring

#### Scenario: Non-Windows bootstrap preserves existing wiring
- **WHEN** an operator runs `bin/bootstrap-project` on a non-Windows platform
  without an explicit wiring override
- **THEN** bootstrap keeps the existing POSIX symlink wiring behavior
- **AND** generated-copy Windows policy does not remove or weaken the existing
  symlink contract

### Requirement: Generated wiring ownership metadata
Bootstrap MUST record verifier-readable generated ownership metadata for
generated Windows wiring artifacts.

#### Scenario: Generated artifact is written
- **WHEN** bootstrap writes a generated command, skill or helper wiring artifact
- **THEN** tracked project policy records the project-relative artifact path
- **AND** it records whether the artifact is file wiring or directory wiring
- **AND** it records ChangeRail source identity and digest data sufficient for
  later stale-copy verification
- **AND** it marks the artifact as generated-owned rather than project-owned

#### Scenario: Portable bootstrap writes ownership metadata
- **WHEN** bootstrap runs in portable config mode
- **THEN** generated ownership metadata avoids machine-local absolute paths
- **AND** source identity is expressed relative to the linked ChangeRail source
  of truth

### Requirement: Wiring backend dry-run reporting
Bootstrap dry-run output MUST report the selected wiring backend, generated
ownership plan and fallback reasons.

#### Scenario: Operator previews native Windows bootstrap
- **WHEN** bootstrap is run with `--dry-run` on native Windows
- **THEN** the plan reports the generated-copy backend
- **AND** it lists generated command, skill and helper wiring artifacts
- **AND** it explains that symlink and junction modes were not selected because
  no explicit fallback opt-in was supplied

### Requirement: Generated Windows wiring refresh
Bootstrap or its refresh surface MUST update only generated-owned Windows
wiring artifacts and MUST NOT silently overwrite project-owned files.

#### Scenario: Generated wiring is refreshed
- **WHEN** an operator runs the generated Windows wiring refresh operation
- **THEN** only artifacts recorded as generated-owned are updated from the
  ChangeRail source of truth
- **AND** refreshed artifacts receive updated digest metadata
- **AND** ignored runtime state and credentials are left untouched

#### Scenario: Project-owned file diverges
- **WHEN** a target path contains project-owned content or lacks generated
  ownership metadata
- **THEN** refresh refuses to overwrite that path silently
- **AND** the output identifies the project-owned divergence and remediation
  path

### Requirement: Partial failure rollback for Windows wiring
Bootstrap MUST roll back only artifacts created by the current run after a
partial Windows wiring failure.

#### Scenario: Generated bootstrap fails partway through
- **WHEN** native Windows generated wiring setup fails after creating some
  artifacts
- **THEN** cleanup removes only artifacts created by the current bootstrap run
- **AND** preexisting project-owned files, ignored runtime state and
  credentials remain untouched

#### Scenario: Cleanup sees a link path
- **WHEN** rollback encounters a symlink or junction path
- **THEN** cleanup removes the link itself when it was created by the current
  run
- **AND** it does not recurse into the link target

### Requirement: Explicit Windows wiring fallback controls
Bootstrap MUST require explicit operator opt-in before creating Windows symlink
or junction fallback wiring.

#### Scenario: Symlink fallback is requested
- **WHEN** an operator explicitly requests Windows symlink fallback
- **THEN** bootstrap verifies symlink privilege or Developer Mode proof before
  reporting success
- **AND** proof reports MUST include schema-valid source metadata and concrete
  per-check evidence, not only passed status names
- **AND** failure to prove the required capability exits non-zero

#### Scenario: Junction fallback is requested
- **WHEN** an operator explicitly requests Windows junction fallback
- **THEN** bootstrap verifies link-aware cleanup and Git-safety preconditions
  before reporting success
- **AND** proof reports MUST include schema-valid source metadata and concrete
  per-check evidence, not only passed status names
- **AND** failure to prove those preconditions exits non-zero

### Requirement: Windows fallback Git proof gate
Bootstrap MUST require concrete Git safety evidence before accepting Windows
junction fallback proof, and MUST preserve the same fail-closed behavior for
symlink fallback fixtures that depend on Git staging safety.

#### Scenario: Junction fallback proof includes Git evidence
- **WHEN** an operator requests Windows junction fallback wiring
- **THEN** bootstrap accepts the fallback proof only when it includes concrete
  passed evidence for Git porcelain status, dry-run add and index inspection
- **AND** missing, status-only or hash-only evidence exits non-zero before
  reporting success
- **AND** each Git proof check MUST explicitly report `safe: true` and
  `unsafe_paths: []`

#### Scenario: Unsafe Git evidence is rejected
- **WHEN** fallback proof evidence indicates that Git would stage ChangeRail
  source, ignored runtime state, credentials or out-of-scope files
- **THEN** bootstrap rejects the fallback before creating or reporting usable
  Windows link wiring
- **AND** diagnostics identify the unsafe path class without printing raw unsafe
  paths or credential-like values

### Requirement: Windows wiring cleanup and ownership negative coverage
Bootstrap smoke MUST cover rename, update, uninstall and partial cleanup
scenarios without hiding project-owned source.

#### Scenario: Partial cleanup is link-aware
- **WHEN** Windows wiring setup fails after creating generated, symlink or
  junction-style artifacts
- **THEN** cleanup removes only current-run-owned or generated-owned paths
- **AND** it does not recurse into link targets or remove project-owned files

#### Scenario: Project-owned source remains visible
- **WHEN** smoke verifies minimal ignore rules for a Windows wiring fixture
- **THEN** project-owned source files remain visible to Git status or dry-run
  evidence
- **AND** ignored runtime/auth files remain ignored or forbidden

#### Scenario: Rename and uninstall boundaries are explicit
- **WHEN** smoke exercises generated Windows wiring rename and uninstall
  ownership fixtures
- **THEN** rename refuses to overwrite a non-manifest-owned target
- **AND** uninstall removes only generated manifest paths
- **AND** project-owned source, auth and runtime files remain untouched

### Requirement: Bootstrap maintenance opt-in
Bootstrap MUST provide an explicit `--with-maintenance` option that adds
repository knowledge maintenance wiring without changing the default generic
consumer output.

#### Scenario: Default bootstrap omits maintenance wiring
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name
  example-project --kind generic` without `--with-maintenance`
- **THEN** bootstrap does not create tracked maintenance policy, catalog,
  baseline, scheduler or helper declarations
- **AND** the generated project remains valid under existing verification
  behavior

#### Scenario: Operator opts into maintenance
- **WHEN** an operator runs `bin/bootstrap-project /opt/example-project --name
  example-project --kind generic --with-maintenance`
- **THEN** the target receives tracked maintenance policy/config skeletons,
  helper wiring and ignore rules required for maintenance runtime output
- **AND** bootstrap still runs `bin/verify-project <target>` unless explicitly
  skipped

### Requirement: Bootstrap maintenance opt-in stays orthogonal
Maintenance bootstrap wiring MUST be orthogonal to project `--kind`, surface
policy and Windows wiring backend decisions.

#### Scenario: Opt-in does not change project kind
- **WHEN** bootstrap renders a generic consumer with `--with-maintenance`
- **THEN** generated project kind remains `generic`
- **AND** maintenance wiring is represented as an additive opt-in surface

#### Scenario: Native Windows opt-in uses generated backend
- **WHEN** native Windows bootstrap selects generated-copy wiring and
  `--with-maintenance` is supplied
- **THEN** maintenance helper copies are included in generated ownership
  metadata
- **AND** no symlink or junction fallback is required solely for maintenance
  helpers
