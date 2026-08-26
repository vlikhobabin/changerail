## Context

Published connected broker supervisor v5 is a dormant Linux primitive that
owns one child process tree and proves bounded cleanup through public
`supervise`. The public release baseline is still a sequential canonical list;
it has no affected profile and no reviewed scheduler. Historical private
prototypes suggest a large acceleration opportunity, but their code, results
and runtime evidence are not valid inputs to this public lineage.

The next work must keep three distinct questions independently reviewable:
safe concurrent execution, correct affected selection/activation and final
end-to-end certification.

## Goals / Non-Goals

**Goals:**

- Define exact future authorization lineages for a dormant scheduler and a
  later affected-profile activation.
- Make their ownership disjoint and preserve v5 as the only child-supervision
  primitive.
- Keep full release authority separate from fast developer feedback.
- Reserve expensive history/full evidence for one final certification.

**Non-Goals:**

- Do not implement or create any successor card in this decision.
- Do not reuse unpublished integration prototypes or their runtime evidence.
- Do not alter current runner, CI, registry, receipt, review or publish paths.
- Do not run history, full release baseline or live matrix evidence.

## Decisions

### 1. Scheduler v1 is a dormant execution primitive

The decision first authorizes
`authorize-bounded-release-semantic-scheduler-v1`, followed by exact
`implement-bounded-release-semantic-scheduler-v1`. The authorization alone
contains:

```json
{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-release-semantic-scheduler-v1.md","successor_id":"implement-bounded-release-semantic-scheduler-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The implementation uses only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-release-semantic-scheduler-v1.md","authorization_id":"authorize-bounded-release-semantic-scheduler-v1"}
```

Scheduler v1 starts from the authorization-publishing HEAD, adds at most 499
production LOC and imports only published v5 for process ownership. It accepts
one prevalidated immutable plan of 1..64 unique task IDs, commands and bounded
timeouts; validates the entire plan and runtime-root allocation before launch;
uses jobs 1..4; executes each task exactly once through v5; cancels outstanding
work on terminal failure; and emits exactly one ordered bounded result per
task. Each child retains v5's 8192-byte combined-output cap. The scheduler
summary is at most 64 KiB and contains no raw child output.

Scheduler v1 does not know Git selection, release profiles, semantic ownership,
receipts or publication authority. It stays structurally dormant outside its
focused tests until the exact affected-profile implementation imports it.

### 2. Affected profile v1 owns selection and the sole activation

Only after scheduler v1 is published may maintainers authorize
`authorize-bounded-affected-release-profile-v1` and then implement exact
`implement-bounded-affected-release-profile-v1`. The authorization alone
contains:

```json
{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v1.md","successor_id":"implement-bounded-affected-release-profile-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

The implementation uses only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v1.md","authorization_id":"authorize-bounded-affected-release-profile-v1"}
```

Affected profile v1 starts from its authorization-publishing HEAD, adds at
most 499 production LOC and depends on the published scheduler and v5. It owns
the canonical semantic inventory, exact physical-step resolution, bounded NUL
Git selector and the sole production import/activation of scheduler v1 in the
release runner. It cannot redefine scheduler supervision or cleanup.

The CLI preserves zero arguments as the compatibility alias for requested
`full-release`; explicit `--profile full-release` is identical. Requested
`affected` requires exactly one `--base`. Invalid combinations fail before
admission or semantic launch. Affected selection includes committed, staged,
unstaged and untracked paths with rename/copy old+new operands. Unknown status,
unknown or ambiguous ownership, self-authority changes, invalid/non-ancestor
base, malformed framing, Git error/timeout/stderr or a breached path/count/byte
bound selects all semantics with a deterministic fallback reason.

Requested profile determines authority. Requested `affected` always reports
`authoritative:false`, even when fallback executes every semantic task. Only an
admitted requested `full-release` that completes the exact full semantic
inventory may report `authoritative:true`. Review, publish, receipt and final
certification gates reject affected output as full evidence.

Canonical CI uses exactly one explicit full-release runner and never invokes
affected mode, scheduler, v5 or individual semantic commands directly. A
parsed YAML/AST ownership oracle rejects inactive, duplicate, chained, wrapped
or indirect alternatives.

### 3. Certification is evidence-only and last

`certify-accelerated-release-loop-v1` is created only after both exact
implementations are published. It changes production/test/runtime LOC 0 and is
the sole place in this lineage that may run reachable-history or full-release
evidence.

Certification first obtains one fresh critical Sol/xhigh pre-capture audit.
Only on GO it runs exactly one reachable-history scan and exactly one requested
full-release baseline, with retry/repair/rescue 0/0/0. It also runs one clean
docs-only affected scenario, one owned-Python affected scenario and one unknown
path fallback in disposable clean worktrees. Docs-only must complete within 15
seconds with at most 15 selected semantic IDs; owned Python must complete
within 120 seconds; unknown input must select the exact full semantic inventory
while remaining non-authoritative. Timing is monotonic diagnostic evidence and
never changes selection, pass/fail, authority, ordering or receipt eligibility.

The certification fails closed on any correctness, authority, parity,
performance, RSS, evidence-freshness or no-retry violation. It does not repair
production code.

### 4. Publication order is strict

The only conforming order is:

1. publish this decision;
2. publish scheduler authorization;
3. publish scheduler implementation;
4. publish affected-profile authorization;
5. publish affected-profile implementation;
6. run and publish final certification.

No later card may exist before its predecessor is published and remotely
reachable. Private prototype branches and terminal unpublished candidates are
forensic-only and cannot satisfy dependencies or evidence.

## Risks / Trade-offs

- **Two implementation lineages add lifecycle overhead** -> disjoint authority
  prevents another broad payload and makes review failures local.
- **Parallel execution can expose hidden shared-state dependencies** -> the
  scheduler prevalidates isolated roots and exact task ownership, while unsafe
  groups remain ordered single tasks or fail closed.
- **Affected selection can omit required work** -> unknown, ambiguous, self or
  bounded-input faults expand to full semantics but remain non-authoritative.
- **Single-shot certification has no statistical averaging** -> absolute
  thresholds are deliberately generous and correctness/authority are evaluated
  independently of timing.

## Migration Plan

1. Validate, review and publish this docs-only decision.
2. Deliver and publish scheduler authorization and dormant implementation.
3. Deliver and publish affected-profile authorization and activation.
4. Run the separate single-shot final certification.

Before step 3, current release baseline and CI remain unchanged. Before final
certification, affected output remains developer diagnostics only.

## Open Questions

None. Any receipt protocol, Windows-native supervisor, adaptive timing cache,
retry policy or change to final thresholds requires a separate decision.
