## ADDED Requirements

### Requirement: Published affected authorization MUST bind exact activation scope
ChangeRail MUST publish `authorize-bounded-affected-release-profile-v1` как одну
clean tracked `4.done` docs-only card после published
`decide-accelerated-release-loop-integration-boundary` commit
`0de81cf7e578335c728466b81c1c60b6d447dab7` и published
`implement-bounded-release-semantic-scheduler-v1` commit
`1414fd744eab565258d590a18fe687e39461b9af`, до создания
`implement-bounded-affected-release-profile-v1`.

Authorization MUST зависеть от decision и scheduler implementation, блокировать
только exact affected implementation и содержать ровно один object только с
этими six fields в этом порядке и с exact values:

```json
{"investigation_card":"openspec/board/4.done/decide-accelerated-release-loop-integration-boundary.md","investigation_id":"decide-accelerated-release-loop-integration-boundary","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v1.md","successor_id":"implement-bounded-affected-release-profile-v1","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Future implementation MUST зависеть от всех трех published sources и
использовать только:

```json
{"authorization_card":"openspec/board/4.done/authorize-bounded-affected-release-profile-v1.md","authorization_id":"authorize-bounded-affected-release-profile-v1"}
```

Она MUST начинаться от exact authorization-publishing HEAD, добавлять не более
499 production LOC, импортировать published scheduler v1 только в release
runner и не переопределять broker/scheduler supervision, cleanup либо result
contracts. Terminal unpublished prototypes, cards, verdicts, manifests, logs и
evidence MUST NOT удовлетворять implementation или review.

#### Scenario: Exact authorization leaves successor absent
- **WHEN** maintainers deliver эту authorization
- **THEN** exact object, reciprocal lineage, future reference, clean-start и
  LOC boundaries остаются machine-checkable
- **AND** successor card/code, executable activation и expensive evidence
  остаются absent.

### Requirement: Affected authorization MUST freeze selection and authority
Future affected profile v1 MUST владеть canonical semantic inventory, exact
physical resolution, bounded NUL Git selector и sole runner activation
published scheduler v1. Selector MUST aggregate committed, staged, unstaged и
untracked paths, сохраняя old+new operands rename/copy.

Zero arguments MUST оставаться compatibility alias requested `full-release`, а
explicit `--profile full-release` MUST быть identical. Requested `affected`
MUST требовать ровно один `--base`; invalid, missing, repeated или unknown CLI
combinations MUST fail before admission или semantic launch.

Invalid/non-ancestor base, malformed framing, unknown status, invalid path,
unknown/ambiguous ownership, selector/authority self-change, Git
nonzero/stderr/timeout или declared path/count/byte bound breach MUST выбирать
exact full inventory с bounded deterministic fallback reason.

Requested `affected` MUST всегда возвращать `authoritative:false`, включая
успешный full fallback. Только admitted requested `full-release`, выполнивший и
прошедший exact full inventory, MAY вернуть `authoritative:true`. Review,
publish, receipt и certification gates MUST отвергать affected output как full
evidence.

#### Scenario: Known input selects required semantics once
- **WHEN** affected получает valid docs-only или owned-Python Git state
- **THEN** invariant safety floor и каждый exact functional owner выбираются в
  deterministic inventory order
- **AND** scheduler выполняет только resolved plan, каждый task ровно один раз.

#### Scenario: Uncertainty falls back without authority
- **WHEN** input unknown, ambiguous, self-referential, malformed или over-bound
- **THEN** affected выбирает exact full inventory и bounded fallback reason
- **AND** requested affected остается non-authoritative.

### Requirement: Affected authorization MUST preserve canonical full runner
Canonical CI MUST содержать ровно один active exact explicit full-release
runner и MUST NOT отдельно запускать affected, scheduler, broker или individual
semantic commands. Parsed YAML/Python-AST ownership proof MUST отвергать
inactive, duplicate, chained, wrapped, indirect, reordered или additional
execution surfaces.

Authorization MUST оставаться docs-only: только card, same-slug OpenSpec
artifacts, synchronized `changerail-release-ci` spec и archive metadata.
Production/test/runtime LOC MUST быть 0. Successor, dependencies, schemas, code,
CI, baseline, receipts и review/publish activation MUST оставаться absent.

Она MUST NOT запускать или принимать reachable-history, full release baseline,
affected execution, live matrix либо terminal prototype evidence. Требуется один
fresh Sol/high review с одной доступной same-card docs repair.

#### Scenario: Authorization cannot execute affected work
- **WHEN** maintainers plan, deliver, review или publish authorization
- **THEN** меняются только exact lineage и bounded future contracts
- **AND** ни один semantic task, selector, history, full baseline, affected или
  live matrix не запускается и не принимается.
