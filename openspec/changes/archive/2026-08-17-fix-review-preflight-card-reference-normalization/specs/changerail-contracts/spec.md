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
`openspec/board/<lane>/<id>.md`; other stems, paths and ambiguous values MUST
not match. The authorization ceiling MUST be an integer from 301 through 500,
and the preflight result MUST retain its machine-verifiable state.

#### Scenario: Published investigation authorizes its exact successor
- **WHEN** an ordinary successor references a valid published authorization
  source with ceiling 500 and protocol allowance, has at most 500 added
  production LOC and its published investigation has the exact card links
- **THEN** preflight permits the bounded LOC and declared protocol
- **AND** returns `ready-for-llm-review` with the ordinary `high` route

#### Scenario: Published card uses a filename reference
- **WHEN** the investigation `Blocks` relation uses exact `<successor-id>.md`
  or canonical board path ending in that filename
- **THEN** preflight treats it as the exact successor id
- **AND** a different stem or noncanonical path does not match

#### Scenario: Authorization is missing or stale
- **WHEN** added production LOC exceeds the default ceiling or a protocol is
  declared but the authorization reference/source is absent, unreadable,
  unpublished, untracked at `HEAD` or does not bind both exact card identities
  and required links
- **THEN** preflight returns `investigation-required`
- **AND** it does not launch an LLM or treat the condition as a free CLI waiver

#### Scenario: Successor exceeds the published ceiling
- **WHEN** a valid authorization declares a ceiling of 500 but the successor
  adds more than 500 production LOC
- **THEN** preflight returns `investigation-required`
- **AND** its result identifies the explicit ceiling that was exceeded
