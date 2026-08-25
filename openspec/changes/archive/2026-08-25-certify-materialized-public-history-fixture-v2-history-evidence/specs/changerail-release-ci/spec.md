## ADDED Requirements

### Requirement: Repaired fixture history certification MUST be one-shot and precommitted
ChangeRail MUST permit exactly one separate reachable-history certification
attempt for repaired `history-fixture-v2` only after the tracked certification
policy is finalized and precommitted, and MUST treat every observed outcome as
terminal. The precommitment MUST NOT claim that the governed capture was
already reviewed or published; one fresh critical final-certification review
MUST occur after capture and before publication.

#### Scenario: Certification policy is finalized before capture
- **WHEN** DO prepares the certification payload for its only history capture
- **THEN** the board/OpenSpec/spec policy already fixes capture id
  `public-history-certification`, timeout 1200 seconds, source identities,
  before/after byte hashes, output oracle and no-retry rule
- **AND** the exact tracked policy fingerprint is retained before execution
- **AND** independent Sol/`xhigh` review and publication remain pending until
  terminal capture evidence exists

#### Scenario: Exact repaired source enters the capture
- **WHEN** certification checks the source immediately before and after
  `python3 scripts/public-surface-scan.py --history --json`
- **THEN** both review fingerprints are
  `sha256:ac7a7dad192e227a734f7ef715f8e57b1369f21a54b890e1bbf323c27ebcf88d`
- **AND** both fixture fingerprints are
  `sha256:59f686b634dd16a443894995e6a05c6630688263f3335b24c3c116fdf5e0d128`
- **AND** both exact-byte SHA-256 values for `authority.json` are
  `6b02ffd9f6af7f4d18afb18ff11a34ac88add48bba41b66e5cc990725a0bbe79`
- **AND** the seven authority paths match their predeclared exact SHA-256 values
  before and after execution

#### Scenario: Sole capture produces PASS
- **WHEN** the absent capture id is used once with timeout 1200 and the command
  completes with exit 0 before timeout
- **THEN** stdout is exactly one complete `changerail.public-surface-scan.v1`
  JSON report with `history: true`, `summary.status: pass`,
  `summary.findings: 0` and `findings: []`
- **AND** all pre/post source identities are unchanged
- **AND** the `changerail.evidence-index.v1` entry and ignored manifest retain
  the command identity, timing, exit, timeout, output and findings metadata

#### Scenario: Sole capture does not produce PASS
- **WHEN** the command reports findings, exits nonzero, times out, cannot start,
  emits incomplete or schema-invalid output, contradicts its exit status or the
  source identity changes
- **THEN** the observed FAIL or TIMEOUT is terminal and source review/publish is
  forbidden
- **AND** no retry, replacement id, upsert, diagnostic promotion, benchmark
  sample-selection rule or same-card repair/rescue is allowed

#### Scenario: Prior source timeout is retained independently
- **WHEN** certification evidence is evaluated
- **THEN** source evidence `public-history-final` remains a separate 300-second
  timeout with empty output, no exit code and no PASS claim
- **AND** the authentic 627.163-second prior duration is calibration only and
  cannot count as this certification attempt or outcome

#### Scenario: Published certification permits source review-only continuation
- **WHEN** the certification capture passed, its fresh critical Sol/`xhigh`
  review returned GO and the certification revision is remote-reachable
- **THEN** the unchanged source may receive exactly one fresh cycle-2
  Sol/`xhigh` review without another source scan or implementation edit
- **AND** the link remains one-way from certification to source with no source
  card edit
- **AND** source GO may proceed to publish while source NO-GO is terminal with
  no repair

#### Scenario: Fast-forward prepares certification policy
- **WHEN** `$changerail-ff` prepares
  `certify-materialized-public-history-fixture-v2-history-evidence`
- **THEN** it creates exactly one apply-ready board/OpenSpec/spec
  documentation/evidence-policy change with zero production/test/runtime LOC
- **AND** no evidence capture, reachable-history scan, fixture materialization,
  benchmark, full baseline, archive, review, commit or push occurs
