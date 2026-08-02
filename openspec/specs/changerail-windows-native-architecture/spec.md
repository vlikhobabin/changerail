# changerail-windows-native-architecture Specification

## Purpose
Зафиксировать durable support contract for the selected native Windows runtime,
wiring, fallback, threat and implementation test model.
## Requirements
### Requirement: Evidence-backed native Windows architecture decision
ChangeRail MUST publish an evidence-backed native Windows architecture decision
before implementing native Windows support.

#### Scenario: Maintainer reads the architecture decision
- **WHEN** a maintainer reads the tracked Windows compatibility documentation
- **THEN** it identifies one default native Windows runtime and wiring path
- **AND** it identifies bounded fallback modes and their required evidence
- **AND** it cites sanitized `030-01` and `030-02` evidence paths without
  committing raw host output

#### Scenario: Research evidence is insufficient for a fallback
- **WHEN** a candidate fallback lacks two-host or least-privilege evidence
- **THEN** the architecture decision MUST record that caveat instead of
  presenting the fallback as a default support path

### Requirement: Native Windows command entrypoints
ChangeRail MUST expose native Windows command entrypoints through tracked
`.cmd` wrappers and MUST NOT require direct execution of extensionless POSIX
shell scripts or implicit Bash for native Windows support.

#### Scenario: Operator invokes a ChangeRail helper on native Windows
- **WHEN** an operator launches a supported helper from a Windows command
  processor
- **THEN** the supported entrypoint is a `.cmd` wrapper that preserves argv,
  cwd, environment and exit code
- **AND** paths containing spaces or non-ASCII characters are passed without
  shell splitting or lossy encoding

#### Scenario: Extensionless or Bash launch is unavailable
- **WHEN** direct extensionless launch or implicit Bash is unavailable on a
  native Windows host
- **THEN** ChangeRail still has a supported native command path through `.cmd`
  wrappers

### Requirement: Least-privilege Windows wiring default
ChangeRail MUST use generated project-local wiring as the native Windows default
so bootstrap and verification do not require Developer Mode, administrator
elevation, symlink privileges or junction traversal.

#### Scenario: Consumer project is bootstrapped on native Windows
- **WHEN** bootstrap runs in native Windows default mode
- **THEN** it creates project-local generated command, skill and helper wiring
  artifacts
- **AND** it records generated ownership in a verifier-readable manifest or
  equivalent tracked project policy
- **AND** it does not create symlinks or junctions unless the operator
  explicitly selects that fallback

#### Scenario: Operator selects a link fallback
- **WHEN** an operator selects symlink or junction wiring on native Windows
- **THEN** ChangeRail MUST verify the required privilege, Developer Mode or
  junction capability before reporting success
- **AND** verification MUST fail closed when the selected fallback cannot be
  proven safe for the target project

### Requirement: Generated wiring drift and upgrade semantics
ChangeRail MUST make generated Windows wiring refreshable, drift-aware and
safe to clean up.

#### Scenario: Generated wiring is stale
- **WHEN** generated wiring content no longer matches the ChangeRail source of
  truth recorded for that generated artifact
- **THEN** `verify-project` or the drift gate MUST report a blocking stale
  generated-wiring finding
- **AND** it MUST identify the refresh command or remediation path without
  overwriting project-owned files silently

#### Scenario: ChangeRail refreshes generated wiring
- **WHEN** a refresh or upgrade operation updates Windows generated wiring
- **THEN** it updates only manifest-owned generated artifacts
- **AND** it leaves project-owned files, ignored runtime state and credentials
  untouched

#### Scenario: Cleanup runs after partial failure
- **WHEN** Windows wiring setup fails partway through
- **THEN** cleanup removes only artifacts created by that run or explicitly
  marked generated-owned
- **AND** cleanup treats symlink and junction paths as links instead of
  recursing into their targets

### Requirement: Native Windows wiring threat model
ChangeRail MUST document and test the native Windows threat model for junction
traversal, accidental staging, credentials, command quoting and untrusted
repository content.

#### Scenario: Git safety is evaluated
- **WHEN** Windows wiring verification or smoke evaluates a generated, symlink
  or junction path
- **THEN** it checks Git porcelain status, dry-run staging and index evidence
  before recommending staged paths
- **AND** it fails closed on any path that would stage ChangeRail source,
  ignored runtime state, credentials or other out-of-scope content

#### Scenario: Commands are built from untrusted paths
- **WHEN** ChangeRail constructs Windows commands using project paths, source
  paths or user-supplied arguments
- **THEN** it passes arguments through structured argv or equivalent safe
  quoting
- **AND** it does not concatenate untrusted values into shell commands that can
  reinterpret metacharacters

#### Scenario: Credentials exist near agent runtime state
- **WHEN** Windows bootstrap, verify, drift or smoke inspects Codex, Claude,
  MCP or SSH-adjacent paths
- **THEN** it MUST NOT copy, print, commit or embed credential contents in
  tracked files or runtime reports

### Requirement: Native Windows implementation test matrix
ChangeRail MUST require a native Windows implementation test matrix that covers
both Windows lab hosts and deterministic local fixtures before claiming support.

#### Scenario: Windows implementation is verified
- **WHEN** native Windows support is implemented
- **THEN** verification covers `windows-host-a` and `windows-host-b` with
  sanitized live evidence or an explicit blocker
- **AND** deterministic local fixtures cover `.cmd` entrypoints, generated
  wiring, drift/refresh, Git safety, cleanup, spaces and non-ASCII paths
- **AND** the primary Linux release baseline remains green

#### Scenario: Least-privilege proof is unavailable
- **WHEN** lab execution cannot prove the default path without Developer Mode
  or elevation
- **THEN** ChangeRail MUST record the missing proof as a blocker or caveat
  before claiming least-privilege native Windows support

### Requirement: Concrete generated Windows wiring ownership
The native Windows generated-copy default MUST use a concrete ownership model
that can be audited by bootstrap, verification, drift and future refresh logic.

#### Scenario: Generated copy ownership is inspected
- **WHEN** a maintainer inspects a generated Windows consumer
- **THEN** each generated wiring artifact has a tracked ownership record
- **AND** the record identifies artifact kind, project-relative destination,
  ChangeRail source identity, digest and generated owner state

#### Scenario: Generated default avoids link prerequisites
- **WHEN** generated-copy wiring is selected as the native Windows default
- **THEN** support does not depend on Developer Mode, administrator elevation,
  symlink privilege or junction traversal
- **AND** symlink and junction behavior remains outside the default path

### Requirement: Fail-closed Windows link fallbacks
Native Windows symlink and junction wiring modes MUST remain explicit
fail-closed fallbacks rather than defaults.

#### Scenario: Symlink fallback is evaluated
- **WHEN** a consumer requests Windows symlink fallback
- **THEN** ChangeRail requires explicit operator opt-in and positive
  Developer Mode or privilege proof
- **AND** the proof includes source metadata and concrete per-check evidence,
  not only passed status names
- **AND** the fallback is rejected when that proof is unavailable or negative

#### Scenario: Junction fallback is evaluated
- **WHEN** a consumer requests Windows junction fallback
- **THEN** ChangeRail requires explicit operator opt-in, link-aware cleanup
  behavior and Git-safety preconditions
- **AND** the proof includes source metadata and concrete per-check evidence,
  not only passed status names
- **AND** the fallback is rejected when Git status, dry-run add or index
  evidence would include out-of-scope content

### Requirement: Generated wiring cleanup boundary
Windows wiring cleanup MUST be bounded to generated-owned or current-run-owned
artifacts.

#### Scenario: Cleanup runs after setup failure
- **WHEN** setup or refresh fails during Windows wiring
- **THEN** cleanup removes only artifacts created by the current run or
  explicitly marked generated-owned for the requested operation
- **AND** cleanup does not remove project-owned files or recurse through
  symlink or junction targets

### Requirement: Generated Windows wiring verification matrix
The native Windows generated-copy default MUST have deterministic verification
coverage for fresh, stale, missing, diverged and refreshed generated artifacts
before ChangeRail claims the generated wiring model is enforced.

#### Scenario: Generated wiring enforcement is verified locally
- **WHEN** the local release baseline runs generated wiring verifier smoke
- **THEN** deterministic fixtures cover valid generated content, stale copies,
  missing generated files, project-owned divergence and successful refresh

#### Scenario: Generated wiring diagnostics are sanitized
- **WHEN** verifier or drift diagnostics report generated Windows wiring
  failures
- **THEN** they avoid credential values, private hostnames and private Windows
  absolute paths

### Requirement: Windows wiring Git safety fixture matrix
The native Windows support model MUST include deterministic Git safety fixture
coverage for generated, symlink and junction wiring modes before those modes
are treated as safe to publish.

#### Scenario: Git safety matrix runs locally
- **WHEN** release baseline runs focused Windows wiring safety smoke
- **THEN** fixtures cover generated-copy, symlink fallback and junction fallback
  path classes
- **AND** each fixture records porcelain status, dry-run add and index
  inspection evidence
- **AND** junction Git proof checks include explicit `safe: true` and
  `unsafe_paths: []` classifications

#### Scenario: Unsafe staging fails closed
- **WHEN** a fixture shows that Git would stage ChangeRail source, ignored
  runtime state, credentials or out-of-scope files
- **THEN** the smoke fails closed and reports the unsafe path class without
  exposing secret values or raw unsafe paths

#### Scenario: Rename and uninstall remain bounded
- **WHEN** Windows wiring is renamed, refreshed, uninstalled or partially
  cleaned up in a fixture
- **THEN** only manifest-owned generated artifacts or current-run-owned link
  paths are modified
- **AND** project-owned files remain untouched and visible to Git safety checks

### Requirement: Final clean-clone support proof
The native Windows implementation MUST pass an end-to-end clean-clone proof on
both Windows lab hosts, or record an explicit support blocker, before the
architecture decision is presented as implemented support.

#### Scenario: Maintainer reads final support evidence
- **WHEN** native Windows implementation is claimed as supported
- **THEN** tracked docs cite a retained ignored clean-clone lifecycle report
- **AND** the report covers both `windows-host-a` and `windows-host-b`
- **AND** the report includes generated-copy bootstrap, verification, discovery,
  refresh/update and scoped no-push staging outcomes

#### Scenario: Support proof has a blocker
- **WHEN** either Windows host cannot complete the clean-clone lifecycle proof
- **THEN** ChangeRail records the blocker or caveat with sanitized evidence
- **AND** docs do not present the blocked path as full native Windows support
