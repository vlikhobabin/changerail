## ADDED Requirements

### Requirement: Phase-routed delivery authorization investigation decision
ChangeRail MUST publish a tracked investigation decision before replacing the
rejected phase-routed aggregate/child dirty-worktree authorization payload. The
decision MUST select one contract for repair budget, card identity, blocked
resume, aggregate runtime root and parent-status authority, and MUST bind one
exact replacement with a production regression floor and separate bounded
authorization source.

#### Scenario: Decision requires an explicit repair budget
- **WHEN** a delivery plan opts into phase routing
- **THEN** `max_repair_cycles` is a required schema-valid integer and value 0
  explicitly disables repair
- **AND** omission is rejected during plan admission before aggregate status,
  workspace lock, single-card preflight or child launch
- **AND** aggregate transitions and child authorization use only the declared
  value without separate defaults

#### Scenario: Decision separates card lookup from declared id
- **WHEN** a phase child is authorized for a plan card whose declared id differs
  from the card filename stem
- **THEN** the parent card is selected uniquely by workspace identity and
  canonical resolved card path
- **AND** the selected entry's declared id remains the plan wire identity used
  to derive and validate child run/status identity
- **AND** duplicate or ambiguous workspace/card-path matches fail closed before
  child launch

#### Scenario: Decision materializes resume authority before child preflight
- **WHEN** `resume-plan` retries an unchanged phase payload after a real child
  `BLOCKED` receipt
- **THEN** it allocates a new aggregate run id and incremented phase attempt
- **AND** it atomically writes a schema-valid parent status under the canonical
  new aggregate path before invoking production single-card preflight
- **AND** the new parent binds the expected new child run/status identity and
  previous aggregate run id, canonical status path and status fingerprint
- **AND** the previous parent and child receipts remain immutable lineage

#### Scenario: Decision limits blocked-phase retry
- **WHEN** a new aggregate parent requests same-phase retry
- **THEN** the immediately preceding canonical child receipt and child status
  both match the same phase and attempt and terminate as `BLOCKED`
- **AND** plan fingerprint, payload fingerprint, workspace, card, repair count
  and phase remain unchanged while the new attempt and child identity differ
- **AND** terminal `DELIVERED`, review `GO`, exhausted-budget `NO-GO`, invalid or
  missing child status, pre-child aggregate failure, plan drift and payload
  drift do not grant this dirty-worktree authority

#### Scenario: Decision rejects alternate aggregate runtime root
- **WHEN** a phase-routed plan supplies an aggregate `--runtime-root` that does
  not normalize to
  `<consumer-root>/.runtime/changerail/delivery-plans`
- **THEN** admission terminates `BLOCKED` before single-card preflight, workspace
  lock or child launch
- **AND** public CLI documentation does not promise alternate-root support for
  phase routing
- **AND** monolithic plan mode retains its existing runtime-root behavior

#### Scenario: Decision defines authority and provenance
- **WHEN** production single-card preflight evaluates a dirty phase child
- **THEN** authority is limited to validated plan id/path/fingerprint,
  aggregate run/path, workspace alias/root, declared and canonical card
  identity, phase, attempt, expected child run/status path, payload fingerprint
  and the transition-specific repair or resume fields
- **AND** timestamps, display reasons, summaries, checks, progress, locks and
  non-predecessor history do not independently grant dirty-worktree authority
- **AND** effective child routing is re-derived from the validated tracked plan
  rather than trusted from provenance fields

#### Scenario: Inconsistent same-user tampering fails closed
- **WHEN** a parent is relocated or schema-invalid, an authority field is
  altered, a card/path match is duplicated, plan or payload has drifted, a
  child identity is reused, resume lineage is stale or the requested transition
  is terminal or unsupported
- **THEN** production preflight rejects the dirty workspace before lock or child
  launch
- **AND** the contract states that fully coordinated replacement of the tracked
  plan, payload and every ignored runtime record by the same user is outside
  this non-cryptographic trust boundary

#### Scenario: Decision binds exact replacement and authorization
- **WHEN** the investigation is ready for publication
- **THEN** it binds successor id
  `implement-phase-routed-delivery-authorization-boundary` and initial path
  `openspec/board/2.todo/implement-phase-routed-delivery-authorization-boundary.md`
- **AND** it binds authorization source id
  `authorize-bounded-phase-routed-delivery-payload`
- **AND** the later clean published authorization binds this investigation to
  the successor's exact `3.inprogress` path with production LOC ceiling 500 and
  `allow_new_authority_or_wire_protocol: true`
- **AND** work above that ceiling stops for a new investigation or split instead
  of weakening verification or raising the ceiling

#### Scenario: Successor verifies the production authorization boundary
- **WHEN** the exact replacement is prepared for independent review
- **THEN** production aggregate-to-child probes cover explicit repair budgets,
  omitted-budget rejection, aliased card id, real `BLOCKED` receipt, new resume
  aggregate/child ids, canonical-root success and alternate-root rejection
- **AND** negative probes cover each plan, aggregate, workspace, card, phase,
  attempt, child path, payload, repair and resume-lineage authority field
- **AND** aggregate start, transition and resume claims invoke production
  single-card preflight at the authorization boundary
- **AND** fake child fixtures are used only for tests that do not claim coverage
  of that boundary

#### Scenario: Investigation remains decision-only
- **WHEN** this investigation change is delivered
- **THEN** it changes only its board card and OpenSpec artifacts
- **AND** production runner, schemas, smoke implementation, CLI, public runtime
  documentation and runtime behavior remain unchanged
