# Добавить scoped maintenance fix mode

## Status
1.backlog

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`060-repository-knowledge-maintenance`

## Series Index
`06`

## Planning State
deferred after explicit negative entry-gate decision; audit/triage value is
delivered, but fix authority is not supported by real proposal evidence

## Source
- `060-00-repository-knowledge-maintenance-program-epic.md`
- Quality and accepted/rejected proposal evidence produced by `060-05`.

## Summary
Добавить explicit maintenance `fix` только для allowlisted, scoped,
behavior-preserving transformations с обязательными parity checks и обычным
ChangeRail review/publish flow. Карточка намеренно не входит в MVP.

## Entry Gate
- Cards `060-01`..`060-05` delivered or explicitly replaced.
- Quality rollup содержит достаточно accepted/rejected triage evidence, чтобы
  назвать конкретные safe transformation classes.
- Operator принимает allowlist, required parity contract и deletion policy.
- Если эти условия не выполнены, story остается в `1.backlog`.

## Entry Gate Decision
- Dependency gate: passed. Cards `060-01`..`060-05` are published in `4.done`;
  `060-05` was published as commit `9af145a` after review cycle 2 returned `go`.
- Operational gate: passed. Read-only run `060-06-entry-gate` completed as
  `changerail.maintenance-run.v1` with result `SUCCEEDED`; its lifecycle report
  contains five deterministic detectors, zero findings and no diagnostics.
- Quality gate: not passed. The schema-valid rollup reports 14 catalog records,
  zero open findings and zero board conflicts, but `findings.resolved`,
  `triage.time_to_triage_seconds`, `proposals.accepted` and
  `proposals.rejected` are `unknown`.
- Proposal gate: not passed. No real records exist below
  `.runtime/changerail/maintenance/proposals/`; tracked accepted/rejected
  fixtures prove the contract only and do not count as operational evidence.
- Operator gate: not passed. No allowlist, parity contract or deletion policy
  has been accepted for write-capable maintenance operation.
- Decision: do not admit this card to `2.todo` and do not run `$chrl-deliver`
  for it. The current read-only audit/triage/feedback/quality surface remains the
  supported product boundary.

## Acceptance
- `fix` никогда не является default skill или scheduled mode и требует explicit
  operator invocation in an isolated/clean worktree.
- Initial allowlist ограничен deterministic generated-index refresh и другими
  transformation classes, отдельно одобренными entry gate; arbitrary code
  refactor и semantic rewrite не входят неявно.
- Каждый transformation plan содержит finding fingerprint, exact path scope,
  proposed operations, risk class и concrete parity commands до mutation.
- Helper показывает dry-run plan и не пишет файлы без explicit write flag.
- Mutation ограничена declared repository-relative paths; scope escape,
  symlink escape, unrelated dirty state или missing parity command останавливают
  run fail-closed.
- После write helper не делает commit, push, PR, publish, deployment, issue/card
  transition или external mutation.
- Измененный payload проходит project-declared parity commands, standard
  verification, independent `$changerail-review` и `$changerail-pub`.
- Удаление файлов не входит в initial allowlist. Будущий delete proposal требует
  positive reference scan, owner approval, runtime/packaging checks и reversible
  scoped diff; возраст файла не является основанием.
- Failed parity сохраняет ignored structured evidence и оставляет changes для
  operator review либо безопасного scoped revert текущего fix plan; он не
  маскируется повторным agent verdict.
- Audit/triage behavior и existing consumers остаются совместимыми, если fix
  mode не включен.

## Depends On
- `060-05-connect-feedback-and-quality-rollup`
- Explicit fix-mode readiness decision recorded in this card.

## Change Set
- none yet

## Verify
- Dry-run/default no-mutation fixtures.
- Allowlist, path/symlink escape and unrelated dirty-state negative tests.
- Generated-index scoped fix with pre/post parity evidence.
- Missing/failing parity fail-closed tests.
- No commit/push/external mutation assertions.
- Independent review/publish handoff smoke without performing publish in helper.

## Related
- `openspec/board/1.backlog/060-00-repository-knowledge-maintenance-program-epic.md`
- `openspec/board/4.done/060-05-connect-feedback-and-quality-rollup.md`
- `skills/changerail-review/SKILL.md`
- `skills/changerail-pub/SKILL.md`

## Change 1: `add-scoped-maintenance-fix-mode`

### Why
Only observed, repeatedly accepted maintenance transformations should receive a
write-capable agent surface; audit findings alone are insufficient authority.

### Goal
Add explicit allowlisted fix planning/writes with path scope, parity evidence
and standard ChangeRail review/publish handoff.

### Acceptance
- Entry gate and all safety conditions above are enforced.
- Initial implementation cannot delete files or mutate external systems.
- Failed verification remains visible and cannot auto-publish.

### Depends On
- `060-05-connect-feedback-and-quality-rollup`

### Related
- `openspec/changes/add-scoped-maintenance-fix-mode/`

## Result
Not started by design. The 2026-08-09 readiness gate was evaluated and returned
negative because real accepted/rejected proposal and operator-approval evidence
does not exist.

## Next
- Keep in backlog. Re-evaluate only after real maintenance findings produce
  schema-valid accepted and rejected decisions for a named candidate
  transformation class, retained scope/parity evidence exists, and the operator
  explicitly accepts the allowlist, parity contract and deletion policy.
- Do not count test fixtures, a clean zero-finding scan or a single agent verdict
  as fix-mode authority.

## Log
- `2026-08-09T12:35:25Z` — fix mode separated from MVP and given an explicit
  evidence-based entry gate.
- `2026-08-09T19:40:00Z` — dependency link refreshed after `060-05` admission;
  no fix-mode readiness is inferred before actual accepted/rejected proposal
  evidence exists.
- `2026-08-09T20:56:04Z` — entry gate evaluated after published `060-05`.
  Fresh read-only scan succeeded with five detectors and zero findings, while
  the quality rollup returned proposal, triage-time and resolution metrics as
  `unknown`; no real proposal decisions or operator allowlist approval exist,
  so the story remains in `1.backlog` and was not sent to `$chrl-deliver`.
