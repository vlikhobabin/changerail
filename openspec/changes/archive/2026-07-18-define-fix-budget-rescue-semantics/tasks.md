## 1. Canonical Lifecycle Semantics

- [x] 1.1 Update `changerail-do` to emit the structured
  `fix_budget_exhausted` handoff with retained findings and no default manual
  budget request.
- [x] 1.2 Update `changerail-deliver` to classify bounded same-card micro-fix,
  linked rescue/replacement work and external blocker without mixing fix and
  review budgets.
- [x] 1.3 Synchronize `AGENTS.shared.md`, `docs/how-it-works.md` and
  `docs/board-and-two-agent-feature-flow.md` with the canonical branching
  contract.

## 2. Consumer Guidance

- [x] 2.1 Update `templates/project/AGENTS.md.tpl` with stable fix/review budget
  terminology and autonomous recovery branches.
- [x] 2.2 Extend bootstrap and wiring smoke assertions so generated consumers
  retain `fix_budget_exhausted`, `max-fix-cycles` and `max-review-cycles`
  guidance.

## 3. Verification And Specs

- [x] 3.1 Run `python3 scripts/smoke-bootstrap-project.py` and
  `python3 scripts/smoke-wiring-discovery.py`.
- [x] 3.2 Run `openspec validate define-fix-budget-rescue-semantics --strict`,
  `openspec validate --all --strict` and `python3 scripts/public-surface-scan.py`.
- [x] 3.3 Sync delta specs into main specs and archive the completed change.
