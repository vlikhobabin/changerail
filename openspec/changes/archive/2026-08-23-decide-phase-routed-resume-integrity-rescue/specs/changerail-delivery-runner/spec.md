## ADDED Requirements

### Requirement: Phase-routed resume-integrity rescue investigation decision
ChangeRail MUST publish a tracked decision-only investigation before replacing
the rejected phase-routed resume payload. The decision MUST define exact
effective no-push authority, derive repair usage from complete ordered history,
preserve recursive resume ownership, reject duplicate canonical Git workspace
roots, bind a connected production regression matrix and authorize only one
exact bounded successor through a separate six-field source.

#### Scenario: Decision requires exact parsed no-push authority
- **WHEN** direct phase child admission or a retained terminal receipt is
  validated
- **THEN** the canonical delivery argument vector contains exactly one distinct
  `--no-push` token and no other push or delivery argument
- **AND** retained `command.argv` is re-derived from the validated plan, phase,
  card, route, launcher and canonical prompt and compared element-for-element
- **AND** omitted, duplicate, reordered, separate or combined conflicting push
  arguments fail closed without substring matching
- **AND** a retained mismatch on resume is rejected before new resume authority,
  child preflight, lock or model launch

#### Scenario: Decision derives repair usage from ordered history
- **WHEN** aggregate transition, terminal-parent admission, resume or dirty child
  preflight evaluates a phase card
- **THEN** one deterministic state-machine replay validates every ordered
  receipt from declared start phase and computes repair usage only from valid
  `review/NO-GO -> repair` transitions
- **AND** same-phase `BLOCKED` retries do not independently consume repair cycles
- **AND** retained `repair_cycles_used` MUST equal the replayed value and remain
  within `max_repair_cycles`
- **AND** mismatch or exhausted/terminal continuation is rejected before a new
  running resume parent, child preflight, lock or model launch

#### Scenario: Decision preserves recursive resume ownership
- **WHEN** an aggregate status has one or more `resume_from` ancestors
- **THEN** validation traverses the full chain to the initial aggregate and
  validates every canonical path, run id, status fingerprint, plan identity,
  immutable history prefix and absence of cycles
- **AND** each history segment is owned by the aggregate that first appended it
  and every child `phase_authority.parent_status` matches that actual owner
- **AND** two consecutive real `BLOCKED` resumes preserve the first and second
  receipt owners and allow the third aggregate to retry the same phase at
  `N+1`
- **AND** truncated, reordered, forked, cyclic, stale or rebound lineage fails
  closed before model launch

#### Scenario: Decision rejects duplicate canonical Git workspace roots
- **WHEN** plan semantics resolve declared workspace paths and aliases
- **THEN** each operational identity is the filesystem-normalized Git
  `rev-parse --show-toplevel` root
- **AND** two aliases resolving through equal paths, symlinks or repository
  subdirectories to one canonical root are rejected before aggregate status,
  child preflight, workspace lock or model launch
- **AND** distinct canonical Git roots continue to pass

#### Scenario: Decision uses existing v1 fields for residual integrity
- **WHEN** the replacement implements command, repair, lineage and workspace
  decisions
- **THEN** it uses the unpublished candidate's existing v1 `phase_routing`,
  `resume_from`, workspace root, phase history, repair usage, payload,
  `workflow`, `phase_authority` and `command.argv` fields
- **AND** no additional lineage-owner field, repair wire version or schema id is
  introduced
- **AND** cross-record derivations are enforced by production semantic
  validation while schemas retain structural required fields and ranges
- **AND** the successor still declares the overall new authority/wire boundary
  because that candidate protocol has not been published

#### Scenario: Decision binds one exact bounded replacement
- **WHEN** this investigation is ready for publication
- **THEN** it binds successor id
  `replace-phase-routed-resume-integrity-boundary`, initial path
  `openspec/board/2.todo/replace-phase-routed-resume-integrity-boundary.md` and
  authorization/review path
  `openspec/board/3.inprogress/replace-phase-routed-resume-integrity-boundary.md`
- **AND** it binds authorization id
  `authorize-bounded-phase-routed-resume-integrity-payload`, initial path
  `openspec/board/2.todo/authorize-bounded-phase-routed-resume-integrity-payload.md`
  and published path
  `openspec/board/4.done/authorize-bounded-phase-routed-resume-integrity-payload.md`
- **AND** the source contains exactly one authorization object bound to
  published investigation path
  `openspec/board/4.done/investigate-phase-routed-resume-integrity-rescue.md`,
  the exact successor `3.inprogress` path, production LOC ceiling 500 and
  `allow_new_authority_or_wire_protocol` true
- **AND** the prior phase-routed authorization is not accepted for this new
  investigation or successor identity

#### Scenario: Atomic replacement remains inside the hard ceiling
- **WHEN** the successor rebuilds the measured 488 added-production-line
  candidate
- **THEN** schema writer, aggregate transition, semantic validator and connected
  production probes are delivered atomically
- **AND** residual fixes replace or consolidate rejected logic so total added
  production LOC does not exceed 500 without weakening source classification,
  invariants or tests
- **AND** a measured result of 501 or more stops for a new investigation and
  split authorization rather than raising the ceiling or publishing a partial
  protocol

#### Scenario: Connected matrix observes every cycle-3 boundary
- **WHEN** the successor is prepared for fresh independent review
- **THEN** each R1, R2 and R4 negative probe first proves its unmodified
  canonical base passes the same production boundary, mutates only the named
  input and asserts the exact rejection reason and `model_launch_delta: 0`
- **AND** R1 covers direct and retained omitted, duplicate, reordered, separate
  and combined push arguments
- **AND** R2 covers independent repair-count/history mutations, budgets 0 and
  greater than 0, exhaustion and repeated blocked retries of one repair cycle
- **AND** R4 covers equal literal roots, symlink aliases and separate
  subdirectories of one Git top-level as well as distinct-root success
- **AND** the positive R3 probe performs two consecutive real `BLOCKED` resumes,
  asserts per-receipt aggregate owners, resumes FF at attempt 3 and reaches DO
  attempt 4 through production aggregate and single-card preflight
- **AND** fake launchers control deterministic child outcomes only and do not
  replace the production authority validator

#### Scenario: Investigation remains planning-only
- **WHEN** this investigation change is delivered
- **THEN** it changes only its board card and OpenSpec artifacts
- **AND** production code, schemas, tests, synced main specs, public runtime docs,
  CLI and runtime behavior are unchanged during fast-forward planning
