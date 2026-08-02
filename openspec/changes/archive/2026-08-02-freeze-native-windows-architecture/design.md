## Context

`030-01` proved that both operator-managed Windows lab hosts can run bounded
non-interactive probes in disposable roots. `030-02` then reproduced native
Windows runtime, wiring and Git behavior on both hosts.

Relevant observed inputs:

- Direct Win32 launch of extensionless `bin/openspec` failed on both hosts.
- `.cmd`, PowerShell and Python wrapper launch variants passed on both hosts.
- Explicit Bash was not portable across the two-host lab.
- Directory and file symlinks passed only under current SSH tokens that reported
  `elevated=true`; non-elevated Developer Mode behavior remains unproven.
- Directory junctions passed, but Git porcelain, dry-run add and index checks
  observed linked/generated paths.
- Generated copies avoided link privileges, made drift observable after source
  update and refreshed deterministically when the generator owned refresh.

Current bootstrap and verification are symlink-centric:

- `bin/bootstrap-project` renders tracked consumer files and creates symlinks
  to ChangeRail `skills/`, `claude/commands/` and helper wrappers.
- `bin/verify-project` validates those symlinks and project-local config.
- `docs/wiring-discovery.md` describes POSIX-style symlink wiring and only
  mentions Codex generated copies as an exception.

## Goals / Non-Goals

**Goals:**
- Select one native Windows default for runtime entrypoints and project wiring.
- Define bounded fallback modes and the conditions under which each is allowed.
- Define tracked, generated and ignored ownership for Windows wiring artifacts.
- Define bootstrap, verify, drift, upgrade and cleanup semantics for the chosen
  architecture.
- Record a threat model and mandatory test matrix for series `040`.

**Non-Goals:**
- Implement `.cmd` wrappers, generated-copy backend, verifier checks or smoke
  automation in this card.
- Promise unsupported Windows editions, shells or non-elevated symlink behavior
  without evidence.
- Replace the current POSIX symlink model for Linux, macOS or WSL.

## Decisions

1. Native Windows command default is tracked `.cmd` entrypoints.
   - `bin/*.cmd` wrappers become the native Windows operator surface for
     OpenSpec and ChangeRail helper commands.
   - `.cmd` wrappers must preserve argv, cwd, environment and exit code, and
     must use safe quoting for spaces and non-ASCII paths.
   - Python-backed helpers call the shared ChangeRail Python runtime selector;
     OpenSpec launch must not depend on direct execution of extensionless POSIX
     shell scripts.
   - Alternatives rejected:
     - extensionless `bin/openspec` direct launch, because it failed on both
       hosts with a Win32 application error;
     - implicit Bash, because one host had no Bash and the other failed through
       its Bash/WSL environment;
     - PowerShell as the primary operator default, because it adds execution
       policy and quoting surface better kept for diagnostics or explicit
       fallback.

2. Native Windows wiring default is generated project-local copies.
   - Bootstrap/adoption on Windows must generate project-local command, skill
     and helper wiring artifacts instead of relying on symlink or junction
     creation.
   - Generated files are owned by a wiring manifest with logical source ids,
     source content digests and refresh policy; raw machine-local source roots
     remain ignored runtime/operator state unless an operator explicitly chooses
     local config.
   - Consumer-tracked generated files are acceptable only when verifier and
     drift checks can prove they still match the ChangeRail source of truth or
     report deliberate project-owned divergence.
   - Alternatives rejected:
     - symlink default, because current two-host evidence only proved elevated
       tokens and did not prove Developer Mode least-privilege behavior;
     - junction default, because Git sees junction paths and accidental staging
       can traverse source-owned content without stricter guardrails;
     - untracked generated wiring default, because clean clones must be
       verifiable and reproducible without hidden local state.

3. Fallbacks are explicit and bounded.
   - POSIX symlink wiring remains the default outside native Windows where it is
     already supported by current contracts.
   - Windows symlink mode is allowed only after verifier proves the required
     privilege or Developer Mode condition for that target and the operator
     explicitly chooses it.
   - Windows junction mode is a compatibility fallback only; it requires
     explicit opt-in, link-aware cleanup and Git-safety evidence before any
     staging suggestion.
   - Python and PowerShell launch paths are diagnostic or helper-specific
     fallbacks, not equal runtime defaults.

4. Bootstrap, verify, drift, upgrade and cleanup share one wiring
   classification.
   - Bootstrap must write the same ownership model that verify/drift consumes.
   - Verify must fail closed on stale, missing, unexpected or project-modified
     generated wiring unless the project policy explicitly classifies the
     divergence as project-owned.
   - Upgrade/refresh must update only manifest-owned generated files and must
     not overwrite project-owned files.
   - Cleanup must remove only artifacts created by the current run or listed as
     generated-owned by the manifest, and must treat junctions/symlinks as
     links instead of recursing into targets.

5. Git safety is mandatory before staging.
   - Windows wiring checks must inspect `git status --porcelain`,
     `git add --dry-run` and index information for generated, symlink and
     junction paths.
   - Publish/review workflows still stage explicit paths only and never rely on
     broad `git add .`.

## Risks / Trade-offs

- [Risk] Generated copies can drift after ChangeRail source updates.
  Mitigation: make drift detection and explicit refresh part of
  `verify-project`, smoke and upgrade semantics.
- [Risk] Generated tracked files increase consumer diff size.
  Mitigation: keep generated artifacts limited to command, skill and helper
  wiring surfaces and avoid copying ChangeRail source wholesale.
- [Risk] `.cmd` quoting bugs can be platform-specific.
  Mitigation: require automated fixtures for spaces, non-ASCII paths, argv
  preservation, cwd/env forwarding and exit-code propagation.
- [Risk] Junction fallback can traverse into ChangeRail source during Git
  operations.
  Mitigation: keep junction mode opt-in and require Git dry-run/index evidence
  plus link-aware cleanup before staging.
- [Risk] Lab hosts currently report elevated tokens.
  Mitigation: do not treat symlink success as least-privilege proof; the
  generated-copy default must pass without Developer Mode or elevation.

## Migration Plan

1. Publish this architecture decision and sync it into `openspec/specs/`.
2. Refresh the `040` backlog so implementation starts with native entrypoints,
   then generated-copy wiring, verifier/drift/Git safety, smoke automation and
   end-to-end proof.
3. Implement `.cmd` entrypoints and runtime selector integration.
4. Implement Windows generated-copy wiring backend and manifest ownership.
5. Extend verifier/drift/Git safety checks, then automate the Windows smoke
   matrix and prove clean-clone end-to-end support.

## Open Questions

- Whether future non-elevated Developer Mode evidence is strong enough to
  promote symlink mode from explicit fallback to supported optional mode.
- Exact manifest filename and field schema for Windows generated wiring; this
  belongs to `040-02` implementation.
