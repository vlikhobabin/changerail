## MODIFIED Requirements

### Requirement: Published investigation authorization for deterministic preflight
The deterministic preflight SHALL accept a successor card's inline JSON
`Published investigation authorization` only when it contains exact
`authorization_card` and `authorization_id` values for a clean, tracked
`HEAD` artifact under `4.done`. That source, rather than the successor, MUST
declare exact `investigation_card`, `investigation_id`, `successor_card`,
`successor_id`, `production_loc_ceiling` and
`allow_new_authority_or_wire_protocol` values. Preflight MUST verify the
current successor path/id, a readable published `4.done` investigation path/id,
the successor's `Depends On` reference, the investigation's `Blocks` reference
and the authorization source's `Depends On` reference. A relation reference
MUST match its exact card id as bare `<id>`, `<id>.md`, or canonical
`openspec/board/<lane>/<id>.md`; `<id>` MAY be a lowercase slug or the exact
sortable UTC form `YYYY-MM-DDTHH-MM-SSZ-<lowercase-slug>`. Other mixed-case
ids, malformed timestamps, stems, paths and ambiguous values MUST not match.
The authorization ceiling MUST be an integer from 301 through 500, and the
preflight result MUST retain its machine-verifiable state. A valid
authorization MUST apply only to its exact successor and SHALL satisfy that
successor's repeated-defect investigation requirement while leaving the
declared LOC ceiling and protocol allowance independent and fail-closed.

#### Scenario: Published investigation authorizes its exact successor
- **WHEN** an ordinary successor references a valid published authorization
  source, declares a repeated defect, remains within the source ceiling and
  obeys its protocol allowance, and its published investigation has the exact
  card links
- **THEN** preflight permits the bounded repeated, LOC and protocol decisions
- **AND** returns `ready-for-llm-review` with the ordinary `high` route

#### Scenario: Published card uses a filename reference
- **WHEN** the investigation `Blocks` relation uses exact `<successor-id>.md`
  or canonical board path ending in that filename
- **THEN** preflight treats it as the exact successor id
- **AND** a different stem or noncanonical path does not match

#### Scenario: Published cards use sortable UTC timestamp ids
- **WHEN** all exact authorization-chain ids use
  `YYYY-MM-DDTHH-MM-SSZ-<lowercase-slug>` and reciprocal relations use an
  admitted exact reference form
- **THEN** preflight validates the chain and follows its declared risk route
- **AND** arbitrary mixed-case or malformed timestamp ids remain non-matches

#### Scenario: Repeated defect has no valid authorization
- **WHEN** a successor declares a repeated defect and its authorization is
  absent, unreadable, stale, unpublished or does not bind the exact successor
- **THEN** preflight returns `investigation-required`
- **AND** it does not launch an LLM or infer a waiver from prose

#### Scenario: Successor exceeds the published ceiling
- **WHEN** a valid authorization declares a ceiling of 500 but the successor
  adds more than 500 production LOC
- **THEN** preflight returns `investigation-required`
- **AND** its result identifies the explicit ceiling that was exceeded

#### Scenario: Successor lacks protocol allowance
- **WHEN** a valid authorization binds the exact successor but its boolean
  protocol allowance is false and the successor declares a new protocol
- **THEN** preflight returns `investigation-required`
- **AND** repeated-defect authorization does not override the protocol decision
