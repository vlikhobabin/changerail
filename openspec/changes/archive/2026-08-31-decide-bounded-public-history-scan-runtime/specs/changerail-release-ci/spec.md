## ADDED Requirements

### Requirement: Bounded release-reachable public history scan
ChangeRail release baseline MUST scan every unique public blob reachable from
the single fully resolved release `HEAD` commit, MUST preserve commit/path
attribution for findings and MUST keep Git process launches constant with
respect to commit, path and blob cardinality. The history scan MUST NOT include
unrelated local refs and MUST fail closed when full reachable history or valid
Git framing cannot be proven. Raw history MUST use config-independent
`--format=tformat:%x1e%H` commit markers with NUL-terminated raw fields and MUST
validate marker, header and path states before accepting a history pass.

#### Scenario: Release checkout contains unrelated local refs
- **WHEN** history mode runs in a complete checkout whose `HEAD` has reachable
  public history and another local ref contains unrelated history
- **THEN** the scanner checks every unique public blob reachable from resolved
  `HEAD`
- **AND** it does not make the release result depend on the unrelated ref

#### Scenario: A public blob is reused across commits and paths
- **WHEN** the same blob object is reachable at multiple public commit/path
  occurrences
- **THEN** the scanner reads and applies public-safety rules to that blob once
- **AND** any finding retains existing structured commit/path attribution

#### Scenario: Git framing or lifecycle is incomplete
- **WHEN** raw history or batch-object framing is malformed, truncated,
  unexpected or a required Git process fails
- **THEN** history mode returns a structured redacted history finding and a
  non-zero result
- **AND** it does not emit a pass or expose raw blob or token-like content

#### Scenario: Release history verification is bounded
- **WHEN** the public-safe 250-commit regression fixture is scanned
- **THEN** history enumeration uses no more than three Git process launches and
  completes within 30 seconds
- **AND** the complete clean-checkout release baseline completes within 300
  seconds

#### Scenario: Existing scanner safety behavior is retained
- **WHEN** current-tree, history, binary, invalid UTF-8 and secret-redaction
  regression fixtures run
- **THEN** current public roots and every release-reachable unique text blob are
  checked with the existing detection rules
- **AND** binary/invalid UTF-8 handling remains unchanged while secret-redaction
  failures remain fail closed at the release gate
