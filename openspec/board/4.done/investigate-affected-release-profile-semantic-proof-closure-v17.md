# Исследовать semantic proof closure affected profile v17

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 44

## Source
- Последний safe published executable authorization boundary:
  `authorize-bounded-affected-release-profile-v16`, exact commit
  `8b8bb21a39c9ece4d4cb621dc59f34efa1a9b702`.
- Terminal unpublished implementation v16 завершил fresh cycle 1 `NO-GO`
  с `4/10` и пятью blockers, использовал единственный same-card repair и
  завершил cycle 2 `NO-GO` с `7/10`, двумя blockers, одним minor и budget
  `1/1/0` exhausted.
- Только validated counters и finding summaries переходят в эту decision.
  V16 card/OpenSpec/code/tests/CI/spec mutation/manifest/verdict files/logs/raw
  evidence являются forensic-only и не читаются, не копируются и не
  cherry-pick-ятся.

## Summary
Опубликовать clean docs-only simplification decision для v17: разделить
грамматическую `R/C 000` boundary и реально достижимые Git scores, а scheduler
proof нормализовать как независимую many-cases-to-one-guard модель с одним
каноническим semantic AST mutant на guard.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Lineage escalation: terminal v16 исчерпал единственный repair; selector и
  scheduler proof повторили blocker class через v15/v16 и требуют нового
  design budget до clean successor.
- Independent review: one fresh `gpt-5.6-sol`/`high`
- Same-card repair budget limit/used/remaining: `1/0/1`, exhausted `false`

## Depends On
- `authorize-bounded-affected-release-profile-v16`
- `investigate-affected-release-profile-public-proof-closure-v16`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`

## Blocks
- `authorize-bounded-affected-release-profile-v17`
- `implement-bounded-affected-release-profile-v17`
- `certify-accelerated-release-loop-v1`

## Authorization
- Future v17 implementation authorization:
  `{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-semantic-proof-closure-v17.md","investigation_id":"investigate-affected-release-profile-semantic-proof-closure-v17","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v17.md","successor_id":"implement-bounded-affected-release-profile-v17","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Decision создаётся docs-only из exact published authorization v16 SHA;
  local/upstream/remote investigation branch до mutation указывают на этот
  SHA, а terminal v16 executable payload/evidence не импортируются.
- Terminal chronology сохраняет cycles `4/10 → 7/10`, пять blockers → два
  blockers и один minor, repair `1/1/0`; remaining blockers классифицированы
  как недостижимая real-Git `R/C 000` fixture и payload-specific early-return
  scheduler mutants.
- Public selector contract разделяет две независимые границы: pure bounded
  NUL grammar/ownership принимает и проверяет `R/C 000..100`, включая оба
  owner-distinct operand, а disposable real-Git fixtures доказывают collector
  только на реально emitted non-zero `R/C` scores, A/M/D и всех четырёх
  streams. Real Git не обязан синтезировать `R000/C000`; отсутствие или
  coercion score всё равно fail closed.
- Scheduler proof имеет отдельно authored requirement guard catalog, case
  catalog и semantic-mutant catalog. Каждый case ссылается ровно на один
  guard, множество referenced guard IDs bidirectionally равно requirement и
  mutant IDs, но case IDs не обязаны равняться mutant IDs; несколько data
  neighbors могут честно проверять один guard.
- Каждый scheduler mutant меняет ровно один существующий canonical AST
  operator или operand на exact node path, сохраняет before/after canonical
  digests и убивается public boundary case. Generated payload predicates,
  inserted early return/raise, marker-only/no-op/reused edits и
  earlier-fault masking запрещены.
- Future authorization зависит ровно от этой investigation, integration
  decision, scheduler v1 и authorization v16 и блокирует только implementation
  v17. Future implementation зависит ровно от тех же predecessors плюс
  authorization v17, блокирует только certification, начинает с authorization
  publishing HEAD и добавляет максимум `499` production LOC.
- Investigation сохраняет весь уже закрытый v16 floor: single typed registry,
  aggregate pre-Git admission, independent ledgers, exact 35→30/Unicode,
  closed execution graph, full-only authority, protocol non-authority,
  source-safe four-step CI и original-RED requirement для будущего successor.
- Investigation меняет только card, same-slug OpenSpec, synchronized main spec
  и archive metadata; production/test/runtime LOC `0`, successors отсутствуют.
  History, real full/affected execution/benchmark, live matrix и certification
  checks не запускаются.

## Change Set
- `investigate-affected-release-profile-semantic-proof-closure-v17`

## Verify
- Required: exact safe base/remote, terminal chronology/forensic boundary,
  split Git grammar/emission boundary, guard-relative scheduler model,
  semantic mutant constraints, exact future lineage/ceiling, successor
  absence, strict OpenSpec, JSON/TOML, classification, current-only public
  scan, sync, whitespace and scope.
- RED: not applicable; docs-only investigation.
- Prohibited: terminal v16 payload/evidence access, history, release/affected
  execution or benchmark, live matrix and certification.

## Archive
- `openspec/changes/archive/2026-08-29-investigate-affected-release-profile-semantic-proof-closure-v17/`

## Related
- `openspec/changes/archive/2026-08-29-investigate-affected-release-profile-semantic-proof-closure-v17/`
- `openspec/board/4.done/authorize-bounded-affected-release-profile-v16.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
DO complete: docs-only selector/scheduler proof decision synchronized and
archived with zero production/test/runtime LOC; ready for fresh ordinary/high
review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `investigate-affected-release-profile-semantic-proof-closure-v17`

### Why
Terminal v16 proved that one impossible real-Git observation and one
case-equals-mutant cardinality rule can force test-shaped counterfeits instead
of independent public proof.

### Goal
Publish a feasible selector and scheduler evidence architecture before any new
authorization or executable successor exists.

### Scope
- this card;
- same-slug docs-only OpenSpec artifacts;
- synchronized release-CI decision contract and archive metadata.

### Acceptance
- Every card acceptance criterion is machine-checkable without terminal
  payload access or prohibited release/certification execution.

### Depends On
- `authorize-bounded-affected-release-profile-v16`
- `investigate-affected-release-profile-public-proof-closure-v16`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`

### Related
- `openspec/changes/investigate-affected-release-profile-semantic-proof-closure-v17/`

## Log
- 2026-08-29 created in a clean worktree and remote branch from exact published
  authorization v16 SHA; only validated terminal counters/finding summaries
  crossed the forensic boundary.
- 2026-08-29 an ignored disposable Git diagnostic confirmed that a zero-content
  pair remains add/delete even with a zero-percent rename/copy threshold;
  `R/C 000` therefore stays a pure grammar boundary, not a fabricated real-Git
  emission claim.
- 2026-08-29 FF prepared one docs-only change with feasible split Git
  grammar/emission boundaries, guard-relative scheduler mutants, exact v17
  lineage and zero executable scope; strict OpenSpec passed `24/24`.
- 2026-08-29 DO synchronized the release-CI delta byte-exactly, archived the
  change and passed exact-base, strict OpenSpec `23/23`, JSON/TOML, source
  classification, current-only public scan `1655/0`, successor absence and
  whitespace gates with zero executable LOC; prohibited checks were not run.
- 2026-08-29T09:22:13Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
