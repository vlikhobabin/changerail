# Добавить maintain skill и scheduler adapters

## Status
1.backlog

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`060-repository-knowledge-maintenance`

## Series Index
`04`

## Planning State
post-MVP story; blocked on `060-03`

## Source
- `060-00-repository-knowledge-maintenance-program-epic.md`
- Codex scheduled tasks, non-interactive mode and GitHub Action docs.
- Symphony scheduler/workflow ownership boundary.

## Summary
Добавить agent-facing `changerail-maintain` modes `audit`/`triage`, bounded
scheduler-neutral runner, least-privilege examples и opt-in consumer wiring.
Fix mode остается отдельной карточкой `060-06`.

## Acceptance
- Skill `changerail-maintain` и Claude wrapper имеют default read-only `audit`
  и explicit bounded `triage`; они не реализуют delivery или publish.
- `audit` запускает deterministic scan и может объяснить ambiguous findings, но
  не меняет repository, baseline, board или external systems.
- `triage` производит schema-bound annotations и card preview; card write
  требует отдельной explicit настройки/команды.
- Skill не заявляет `fix` доступным до delivery `060-06` и направляет mutation
  requests в обычный ChangeRail card flow.
- Scheduler-neutral runner пишет structured run status под ignored runtime
  state, имеет timeout/budget/lock и не скрейпит human prose для control flow.
- Runner различает deterministic scan и optional agent triage; отсутствие Codex
  auth не блокирует scan-only mode.
- GitHub scheduled example использует read-only contents permission, учитывает
  default-branch/at-least-once behavior и публикует report как artifact без
  repository mutation.
- Codex scheduled task example рекомендует isolated worktree и read-only audit;
  local mode документирует риск изменения активного checkout.
- systemd example задает repository cwd, bounded timeout, runtime directory и
  non-overlapping execution без machine-specific tracked paths.
- CI/GitHub Action example отделяет read-only analysis job от любого job с
  write permissions или API credentials.
- Bootstrap/templates предлагают maintenance wiring только по explicit opt-in;
  existing consumers не получают policy автоматически.
- `verify-project` проверяет opt-in helper/schema/config/ignore wiring, но не
  запускает full maintenance scan как часть bootstrap verification.
- POSIX/native Windows helpers и generated-copy refresh покрыты focused smoke.

## Depends On
- `060-03-add-maintenance-findings-lifecycle`

## Change Set
- none yet

## Verify
- Skill frontmatter and path-neutrality validation.
- Audit/triage no-mutation and explicit card-preview smoke.
- Runner timeout, lock, structured status and missing-auth scan-only fixtures.
- Static validation of GitHub/systemd/Codex examples.
- Bootstrap/verify tests for opted-in, absent and stale maintenance wiring.
- Native Windows entrypoint and generated-copy refresh smoke.

## Related
- `openspec/board/1.backlog/060-00-repository-knowledge-maintenance-program-epic.md`
- `openspec/board/1.backlog/060-03-add-maintenance-findings-lifecycle.md`
- `skills/changerail-deliver/SKILL.md`
- `bin/changerail-delivery-runner`
- `templates/project/`

## Change 1: `add-changerail-maintain-audit-and-triage`

### Why
Agents need a stable workflow that consumes deterministic reports without
silently escalating read-only audit into repository mutation.

### Goal
Add canonical skill/command surfaces for audit and bounded triage.

### Acceptance
- Audit and triage follow the safety and output contracts above.
- Skill is explicit that delivery and fix remain separate workflows.
- Codex and Claude discovery/frontmatter checks pass.

### Depends On
- `060-03-add-maintenance-findings-lifecycle`

### Related
- `openspec/changes/add-changerail-maintain-audit-and-triage/`

## Change 2: `add-scheduled-maintenance-runners`

### Why
Recurring scans need a scheduler-neutral bounded execution surface rather than
scheduler-specific behavior embedded in core.

### Goal
Add structured runner status and least-privilege GitHub, systemd, Codex and CI
examples.

### Acceptance
- Runner control flow uses structured records and bounded execution.
- Every example is read-only by default and documents scheduler limitations.
- No example promises exact cron timing or exactly-once execution.

### Depends On
- `add-changerail-maintain-audit-and-triage`

### Related
- `openspec/changes/add-scheduled-maintenance-runners/`

## Change 3: `wire-maintenance-consumer-opt-in`

### Why
Consumers need portable bootstrap/verify integration without making maintenance
mandatory for existing repositories.

### Goal
Add explicit bootstrap/templates, wiring verification and cross-platform helper
coverage for maintenance surfaces.

### Acceptance
- Opted-in consumers receive valid wiring and policy skeletons.
- Non-opted-in consumers remain unchanged and valid.
- POSIX and native Windows refresh/discovery tests pass.

### Depends On
- `add-scheduled-maintenance-runners`
- Relevant bootstrap decisions from card `050` when they affect profiles/wiring.

### Related
- `openspec/changes/wire-maintenance-consumer-opt-in/`

## Result
Not started.

## Next
- Refresh after MVP exit gate and card `050` bootstrap decisions.

## Log
- `2026-08-09T12:35:25Z` — operational story extracted from broad harness card.
