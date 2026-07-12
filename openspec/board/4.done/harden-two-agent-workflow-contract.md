# Закрепить двухагентный workflow как контракт ChangeRail

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Review of `docs/board-and-two-agent-feature-flow.md` after wording update.
- Repository review of `AGENTS.shared.md`, lifecycle skills, runner, schemas,
  templates and board docs.

## Summary
Привести фактический ChangeRail workflow к тому, что описано в гайде по доскам
и двум агентам: отделить рекомендательную методологию от обязательных
контрактов, явно закрепить границы orchestrator / delivery worker / independent
review, и устранить расхождения между документацией, templates, skills, runner
и machine-readable contracts.

Ключевой риск: сейчас `ff -> do -> review -> pub` и fail-closed publish
закреплены достаточно хорошо, но двухагентная схема и независимость reviewer-а
в значительной части держатся на инструкциях агента. Нужно решить, что можно
сделать machine-checkable, а что должно остаться documented operator protocol.

## Acceptance
- Repository docs, `AGENTS.shared.md`, board docs and project templates agree on
  the same lifecycle semantics for:
  - one card = one story-level delivery unit;
  - `do` leaves review-gated cards in `3.inprogress`;
  - `review` is independent/fresh and writes runtime verdict only;
  - `pub` is fail-closed and performs final `4.done` transition.
- The orchestrator / delivery worker / reviewer model is explicitly represented
  in reusable ChangeRail instructions, not only in
  `docs/board-and-two-agent-feature-flow.md`.
- The review independence contract is audited and either:
  - strengthened with machine-checkable identity/evidence fields and validation
    where feasible; or
  - explicitly documented as an operator-enforced protocol with clear limits of
    what `bin/changerail-review-verdict` can and cannot prove.
- `changerail-deliver`, Claude wrappers and runner docs agree on batch semantics:
  either true bounded queue delivery is implemented and evidenced per card, or
  docs state clearly that `bin/changerail-delivery-runner` is a single-card
  launcher while `$changerail-deliver` owns directory/queue handling.
- Bootstrap templates propagate the current workflow model to new consumers or
  link to the canonical guide so new projects do not receive a weaker process.
- Stale root board text that says delivery/review/publish skills are not yet
  available is removed or replaced with current guidance.
- The final implementation includes focused verification for any touched
  scripts, schemas or templates, plus `openspec validate --all --strict` and
  `git diff --check`.

## Change Set
- `align-board-docs-and-templates`
- `define-agent-role-contract`
- `harden-review-independence-evidence`
- `clarify-runner-batch-semantics`

## Verify
- passed: `python3 -m py_compile scripts/changerail_review_verdict.py scripts/smoke-review-verdict-validation.py bin/changerail-delivery-runner`
- passed: `python3 scripts/smoke-review-fingerprint.py`
- passed: `python3 scripts/smoke-review-verdict-validation.py`
- passed: `python3 scripts/smoke-delivery-runner.py`
- passed: `bin/changerail-delivery-runner run --help`
- passed: `python3 -m json.tool schemas/changerail-review-verdict.schema.json`
- passed: `python3 -m json.tool .mcp.json`
- passed: TOML parse for `.codex/config.toml`
- passed: `./bin/openspec validate align-board-docs-and-templates --strict`
- passed: `./bin/openspec validate define-agent-role-contract --strict`
- passed: `./bin/openspec validate harden-review-independence-evidence --strict`
- passed: `./bin/openspec validate clarify-runner-batch-semantics --strict`
- passed: `./bin/openspec validate --all --strict` before archive (17/17)
- passed: `./bin/openspec validate --all --strict` after archive (13/13)
- passed: `git diff --check`
- passed: targeted public-surface scan for non-generic `/opt/*` paths in
  touched docs/templates/skills/scripts/schemas/specs
- passed: independent review cycle 1 returned fresh `go` with no findings

## Archive
- `openspec/changes/archive/2026-07-12-align-board-docs-and-templates/`
- `openspec/changes/archive/2026-07-12-define-agent-role-contract/`
- `openspec/changes/archive/2026-07-12-harden-review-independence-evidence/`
- `openspec/changes/archive/2026-07-12-clarify-runner-batch-semantics/`

## Related
- `docs/board-and-two-agent-feature-flow.md`
- `docs/how-it-works.md`
- `AGENTS.shared.md`
- `openspec/board/README.md`
- `templates/project/AGENTS.md.tpl`
- `templates/project/openspec/board/README.md.tpl`
- `skills/changerail-deliver/SKILL.md`
- `skills/changerail-review/SKILL.md`
- `skills/changerail-pub/SKILL.md`
- `bin/changerail-delivery-runner`
- `schemas/changerail-review-verdict.schema.json`
- `openspec/specs/changerail-skill-surface/spec.md`
- `openspec/specs/changerail-delivery-runner/spec.md`
- `openspec/specs/changerail-contracts/spec.md`
- `openspec/changes/archive/2026-07-12-align-board-docs-and-templates/`
- `openspec/changes/archive/2026-07-12-define-agent-role-contract/`
- `openspec/changes/archive/2026-07-12-harden-review-independence-evidence/`
- `openspec/changes/archive/2026-07-12-clarify-runner-batch-semantics/`

## Result
Implemented and archived. The reusable methodology, lifecycle skills, Claude
wrappers, board docs, consumer templates, review verdict schema/helper and
runner docs now agree on the orchestrator / delivery worker / independent
reviewer model. Review independence is enforced as a machine-checkable
`reviewer.independence` attestation in `changerail.review-verdict.v1`, with
documented limits that helper validation cannot prove real-world identity or
full memory isolation. Independent review cycle 1 returned fresh `go` with no
findings. Publish committed reviewed payload as `229270e` before this
deterministic board finalization amend; final publish commit is recorded in git
history and publish summary.

## Next
- done

## Change 1: `align-board-docs-and-templates`

### Why
Root board docs and consumer templates must not contradict the current lifecycle
surface or omit the two-agent model entirely.

### Goal
Update reusable docs/templates so new and existing consumers see the same
orchestrator / worker / reviewer boundaries.

### Acceptance
- Root board README no longer claims delivery/review/publish skills are missing.
- Consumer templates reference or embed the current ChangeRail workflow model.
- Docs keep public examples generic.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-12-align-board-docs-and-templates/`

## Change 2: `define-agent-role-contract`

### Why
The two-agent model needs a reusable contract, not only a guide.

### Goal
Define orchestrator, delivery worker and reviewer responsibilities in shared
methodology and lifecycle skills, including when orchestrator and worker may be
the same session and when they must be separate.

### Acceptance
- Shared methodology and lifecycle skills agree on role boundaries.
- Safety stops explain what to do when the required fresh review context is not
  available.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-12-define-agent-role-contract/`

## Change 3: `harden-review-independence-evidence`

### Why
Fresh review is required, but current helper validation proves working-tree
freshness rather than agent/session independence.

### Goal
Decide and implement the strongest practical review-independence evidence:
schema fields, helper validation, runtime metadata, or explicit documented
operator protocol.

### Acceptance
- Review verdict docs and schema clearly state what independence evidence is
  required.
- Helper validation behavior matches the documented guarantee.
- Publish fail-closed semantics remain intact.

### Depends On
- `define-agent-role-contract`

### Related
- `openspec/changes/archive/2026-07-12-harden-review-independence-evidence/`

## Change 4: `clarify-runner-batch-semantics`

### Why
The guide describes batch/queue work, while the tracked runner is currently a
single-card launcher that delegates queue interpretation to `$changerail-deliver`.

### Goal
Make runner, specs and docs agree: either implement explicit bounded queue
status per card, or document the runner as single-card and keep queue handling
inside `changerail-deliver`.

### Acceptance
- `bin/changerail-delivery-runner`, docs and OpenSpec specs describe the same
  accepted inputs and status records.
- If queue support is added, each card has clear per-card terminal evidence.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-12-clarify-runner-batch-semantics/`

## Log
- 2026-07-12T09:34:06Z card created from repository review findings about the
  two-agent workflow and guide/code alignment.
- 2026-07-12T09:45:00Z fast-forward planning created four OpenSpec changes and
  moved the card to `2.todo`.
- 2026-07-12T10:28:00Z delivery implemented docs, templates, skills, Claude
  wrappers, runner wording, review verdict schema/helper and specs; verified
  checks; archived all four OpenSpec changes; moved the card to `3.inprogress`
  for independent review.
- 2026-07-12T09:57:06Z independent review cycle 1 returned fresh `go` with no
  findings in `.runtime/changerail/reviews/harden-two-agent-workflow-contract.json`.
- 2026-07-12T10:35:00Z publish committed reviewed payload as `229270e` and
  finalized this card into `4.done` as deterministic post-publish metadata.
