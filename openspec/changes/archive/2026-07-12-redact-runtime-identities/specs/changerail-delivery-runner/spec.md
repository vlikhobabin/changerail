## MODIFIED Requirements

### Requirement: Delivery runner preflight
Delivery runner preflight MUST sanitize connectivity diagnostics before writing
structured runtime status.

#### Scenario: Connectivity success is sanitized
- **WHEN** an operator supplies a connectivity URL containing URL userinfo or
  token-like query values and the request succeeds
- **THEN** the structured preflight check records only sanitized endpoint
  metadata and response status
- **AND** it does not include the raw submitted URL, userinfo or query value

#### Scenario: Connectivity failure is sanitized
- **WHEN** an operator supplies a connectivity URL containing URL userinfo or
  token-like query values and the request fails
- **THEN** the structured preflight check records sanitized endpoint metadata
  and the exception class
- **AND** it does not include the raw submitted URL or raw exception text
