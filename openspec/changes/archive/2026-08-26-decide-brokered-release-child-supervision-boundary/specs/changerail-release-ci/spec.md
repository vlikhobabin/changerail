## ADDED Requirements

### Requirement: Published brokered supervision decision MUST precede v4 authorization
ChangeRail MUST publish `decide-brokered-release-child-supervision-boundary` as
one clean tracked `4.done` docs-only card after the published terminal v3
decision and authorization, and before creating either
`authorize-bounded-brokered-release-child-supervisor-v4` or
`deliver-brokered-release-child-supervisor-v4`.

The decision MUST block both future cards. The future authorization MUST depend
on this decision and block only the exact implementation. The future
implementation MUST depend on both and use only this exact inline reference:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-brokered-release-child-supervisor-v4.md","authorization_id":"authorize-bounded-brokered-release-child-supervisor-v4"}
```

The future authorization alone MUST contain exactly one object with only the
following six fields in this order and with these exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-brokered-release-child-supervision-boundary.md","investigation_id":"decide-brokered-release-child-supervision-boundary","successor_card":"openspec/board/3.inprogress/deliver-brokered-release-child-supervisor-v4.md","successor_id":"deliver-brokered-release-child-supervisor-v4","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Publication of this decision MUST exhaust and supersede the earlier future
`deliver-psutil-backed-release-child-supervisor-v3` path. The published v3
decision and authorization MUST remain immutable historical sources, but MUST
NOT authorize creation, continuation, repair, rescue, reuse or publication of
v3 after this decision. Exact v4 MUST be the sole conforming future release
child supervisor implementation path.

#### Scenario: Decision creates no future authority or implementation
- **WHEN** maintainers deliver this decision
- **THEN** it retains the exact future six-field and two-field objects plus
  reciprocal blocks/dependencies without creating either future card or code
- **AND** terminal v3 material remains forensic-only and supplies no authority,
  evidence, verdict, history, log, receipt or manifest
- **AND** any attempt to create, continue, repair, rescue, reuse or publish v3,
  or to introduce a supervisor successor other than exact v4, is rejected.

### Requirement: Broker subprocess MUST own the supervised process tree by construction
The future v4 controller MUST launch one dedicated broker in a new session or
equivalent platform containment unit. Before target launch the broker MUST
enable its child-supervision role and emit a bounded readiness message. Only
the broker may launch the target, discover its descendants or perform target
cleanup.

The application caller MUST NOT enable child-subreaper mode, scan caller-global
children, infer ownership from a caller before/after snapshot or claim a
pre-existing bystander and descendants that the bystander creates later. On
Linux the broker MUST become subreaper before target launch and start with no
application workload child other than the target.

#### Scenario: Later bystander descendant remains outside broker ownership
- **WHEN** a pre-existing caller child creates a new descendant after broker
  readiness while the target also forks, creates a session or exits
- **THEN** broker discovery and cleanup include only broker-owned target
  identities, every owned target identity is gone before success, and the
  bystander identities remain alive and unmodified.

### Requirement: Broker protocol and cleanup MUST be bounded and fail closed
The future v4 parent-broker protocol MUST use one closed version, monotonically
increasing sequence numbers, bounded message bytes, bounded total bytes and
bounded message count. It MUST permit exactly one `ready`, exactly one
`started`, bounded observations and exactly one terminal report after cleanup.
Pipe EOF MUST be stream state only.

Malformed UTF-8 or JSON, unknown/duplicate fields or messages, sequence drift,
truncation, premature EOF, multiple terminal reports, broker exception, target
identity error, execution timeout, cleanup timeout, identity/cap error or
missing cleanup proof MUST be terminal and MUST NOT report success. Every
recoverable post-launch broker exception MUST enter bounded broker-owned
cleanup. Successful cleanup MUST require two consecutive empty owned-identity
scans and no live or zombie owned identity.

The parent MUST keep a bounded outer process-group or platform containment path
for an unresponsive broker and MUST report terminal failure without claiming
that a process group contains detached sessions. The future implementation
MUST state and prove its fatal broker-death guarantee precisely.

#### Scenario: Protocol or broker fault cannot manufacture success
- **WHEN** the protocol is malformed, truncated, out of sequence, reaches EOF
  early, exceeds a bound, the broker raises after target launch, or cleanup
  proof is absent
- **THEN** the controller returns one bounded terminal failure and never a
  successful completion
- **AND** recoverable post-launch faults clean the broker-owned tree before the
  terminal report, while fatal broker-death coverage is not overstated.

### Requirement: Brokered v4 MUST use a clean bounded delivery and proof cycle
Future `deliver-brokered-release-child-supervisor-v4` MUST start from the exact
HEAD that publishes its authorization, use only the exact two-field reference,
add at most 499 production LOC and add no external dependency beyond the
already published psutil pin. It MUST NOT reuse terminal v3 code, verdict,
history, logs, receipts, manifests or evidence; generic forensic findings may
inform a fresh implementation and proof only.

The connected proof MUST cover pre-existing bystander plus later descendant,
pre-ready launch rejection, immediate post-launch identity fault, live-leader
pipe EOF, normal/signal/crash/timeout completion, setsid/double-fork, inherited
pipe, TERM-ignore/fork-during-cleanup, output and protocol N/N+1 bounds,
malformed/truncated/duplicate protocol, broker exception, timeout arithmetic,
two-empty cleanup and no-live/no-zombie results. V4 MUST remain dormant outside
focused tests until exact publication, and downstream activation MUST remain
blocked pending a later tracked refresh.

V4 receives one implementation attempt and one fresh Sol/high review. A first
NO-GO permits at most one bounded same-card repair and one final Sol/high
re-review; a third review, rescue, retry or terminal evidence reuse is
forbidden.

#### Scenario: One bounded repair replaces repeated rescue lineages
- **WHEN** the first fresh v4 review returns NO-GO for an in-scope defect
- **THEN** maintainers may perform exactly one bounded same-card repair and one
  final Sol/high re-review
- **AND** any surviving blocker after that re-review is terminal and cannot
  create another repair, rescue, publication or evidence-reuse path.

### Requirement: Brokered decision delivery MUST remain docs-only and dormant
This decision delivery MUST add production, test and runtime LOC `0`, MUST NOT
create either future card or code, and MUST NOT activate release baseline, CI,
review/publish, receipt or downstream work. It MUST NOT run or accept reachable
history, full release baseline or live matrix evidence.

#### Scenario: Decision cannot activate brokered supervision
- **WHEN** the decision is planned, delivered, reviewed or published
- **THEN** only its card, same-slug artifacts, synchronized main spec and
  archive metadata change
- **AND** all executable and downstream activation surfaces remain unchanged.
