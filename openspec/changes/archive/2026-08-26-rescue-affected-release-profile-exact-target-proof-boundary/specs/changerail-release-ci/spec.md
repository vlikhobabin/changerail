## ADDED Requirements

### Requirement: Exact target/proof rescue MUST replace terminal unpublished affected v2
ChangeRail MUST publish
`rescue-affected-release-profile-exact-target-proof-boundary` as one docs-only
decision from exact corrected published
`authorize-bounded-affected-release-profile-v2` tip
`042c68ebc7f621646cba550ae59450b36e17afa3`.

The unpublished `implement-bounded-affected-release-profile-v2` path MUST be
terminal, non-conforming and forensic-only. Its payload, card, manifest,
verdicts, logs and evidence MUST NOT satisfy any dependency, authorization,
implementation, review or publication gate. Published cards and archives MUST
remain unchanged. After this decision is published the v2 implementation
successor MUST be exhausted and superseded by the exclusive v3 lineage.

The only conforming order MUST be this decision, docs-only
`authorize-bounded-affected-release-profile-v3`, clean
`implement-bounded-affected-release-profile-v3`, then
`certify-accelerated-release-loop-v1`. The v3 authorization MUST contain exactly
one object with only these fields and values:

```json
{"investigation_card":"openspec/board/4.done/rescue-affected-release-profile-exact-target-proof-boundary.md","investigation_id":"rescue-affected-release-profile-exact-target-proof-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v3.md","successor_id":"implement-bounded-affected-release-profile-v3","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Its `Depends On` relation MUST contain exactly
`rescue-affected-release-profile-exact-target-proof-boundary`,
`decide-accelerated-release-loop-integration-boundary`,
`implement-bounded-release-semantic-scheduler-v1` and
`authorize-bounded-affected-release-profile-v2`. It MUST block only
`implement-bounded-affected-release-profile-v3`.

The v3 implementation MUST use only:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v3.md","authorization_id":"authorize-bounded-affected-release-profile-v3"}
```

It MUST depend exactly on those four published predecessors plus published v3
authorization, block only `certify-accelerated-release-loop-v1`, start from the
authorization-publishing HEAD, add at most 499 production LOC and reconstruct
from published sources without copying or cherry-picking terminal work.

#### Scenario: Rescue leaves one published-source successor path
- **WHEN** maintainers publish this decision
- **THEN** unpublished v2 is exhausted and exact v3 lineage is exclusive
- **AND** authorization, implementation and certification successors remain absent.

### Requirement: Affected v3 MUST close Git grammar and every target before semantics
Future v3 MUST preserve exact 35-ID digest, complete 35→30 physical resolution,
bounded aggregate NUL selection, sole scheduler v1 activation and full-only
authority without changing published broker/scheduler supervision or cleanup.

Each of the three Git name-status streams MUST accept only exact `A`, `M`, `D`,
or `R`/`C` followed by exactly three ASCII decimal digits with numeric value in
`000..100`. A/M/D MUST consume one operand and R/C MUST consume old+new operands.
Any other width, sign, case, score, status, framing, operand or bound MUST fail
closed to the full inventory. Untracked input MUST remain NUL-framed paths only.

The profile MUST contain one closed machine-readable target descriptor inventory
covering every frozen command token that names an executable, repository input
file, repository input directory or runtime output. Each target/token MUST map
exactly once. Effective-PATH executables and repository input type, root,
read/search/execute availability MUST be proven; runtime outputs MUST declare an
exact bounded repository-local parent. Missing, duplicate, unknown, ambiguous,
unavailable, wrong-type/access or root-escaping targets MUST be aggregate
admission failures with `semantic_started: 0` before Git selection and semantics.

#### Scenario: Status or target uncertainty selects no narrow authority
- **WHEN** a Git token or frozen command target violates its exact grammar or descriptor
- **THEN** selector uncertainty expands to full and admission uncertainty launches zero semantics
- **AND** release authority remains false.

### Requirement: Affected v3 MUST close scheduler types and connected proof
Scheduler summary `jobs` MUST have exact JSON integer type and equal requested
`1` or `4`; booleans, floats, strings and null MUST fail. Every published exact
summary field/status/order/size and pass, terminal, outer and synthetic row tuple
MUST remain unchanged and invalid data MUST NOT authorize.

Connected fixtures MUST be finite, non-noop and counterfactual. They MUST cover:

- all three Git diff streams and untracked input; valid A/M/D/R/C old+new;
  base/nonancestor/stderr/nonzero/timeout/framing/status/path/count/per-path/
  aggregate/self/unknown faults, including every R/C width/range/case class;
- every target descriptor kind and missing/extra/duplicate/unknown/ambiguous/
  type/access/root/symlink fault, with runner zero-launch for each admission class;
- every valid scheduler row plus exact typed cross-field mutations, missing/
  extra/reordered/duplicate/cross-ID rows, independent summary-size guard and
  jobs boolean/float/string/null faults for requested 1 and 4;
- every canonical CI top-level/job/step field and name, each trigger key/value,
  permission, literal action SHA, exact `with` maps and run scalars, order,
  workflow/job/step env, one/multiple matrix, condition, continue-on-error,
  timeout, shell/working-directory and direct/chained/wrapped/indirect surfaces.

Each fixture MUST assert that it changed the intended source and MUST fail if
the corresponding production guard is removed or weakened. Requested affected
MUST remain non-authoritative for subset and full fallback; only admitted exact
full pass MAY authorize. V3 MUST create and accept no receipt, capture, marker
or cache.

#### Scenario: Disconnected or incomplete proof cannot pass review
- **WHEN** a required branch lacks a connected counterfactual or a fixture mutates the wrong surface
- **THEN** focused verification and review fail
- **AND** no affected/focused result can satisfy certification authority.

### Requirement: Exact target/proof rescue MUST remain docs-only
This decision MUST modify only its card, same-slug OpenSpec artifacts,
synchronized `changerail-release-ci` specification and archive metadata. It
MUST add production/test/runtime LOC 0 and MUST NOT create successor cards,
code, dependencies, schemas, CI or runtime authority.

It MUST NOT run or accept reachable history, real full baseline, affected
benchmark, live matrix, certification or unpublished prototype evidence. One
fresh Sol/high review and one same-card docs repair are available.

#### Scenario: Decision cannot claim executable closure
- **WHEN** this decision is delivered or reviewed
- **THEN** only lineage and exact future trust boundaries change
- **AND** executable closure remains absent until separately published v3 work.
