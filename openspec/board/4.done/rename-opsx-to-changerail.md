# Переименование OPSX в ChangeRail

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
published

## Source
- Operator decision: rename OPSX to ChangeRail to avoid collision with
  OpenSpec `opsx` terminology and reduce onboarding confusion.
- Discussion: OpenSpec remains the artifact/spec workflow dependency;
  ChangeRail becomes the product/toolchain name.

## Summary
Переименовать публичный продукт, репозиторий, agent command surface, contracts,
runtime paths и consumer wiring с OPSX на ChangeRail. OpenSpec остается
отдельной зависимостью и форматом артефактов, поэтому `openspec-*` lifecycle
skills и `bin/openspec` не переименовываются.

## Acceptance
- Публичная идентичность использует `ChangeRail`, `changerail` и
  `/opt/changerail` вместо `OPSX`, `opsx` и `/opt/opsx`, кроме явно
  разрешенных history/migration mentions.
- Claude command surface переехал с `/opsx:*` на `/changerail:*`.
- Codex lifecycle skills переехали с `$opsx-*` на `$changerail-*`.
- Contract namespace и schema filenames используют `changerail.*` и
  `changerail-*`.
- Bootstrap, verify, smoke, CI и runbooks генерируют/проверяют новый
  ChangeRail consumer wiring.
- GitHub repository rename и local `origin` update описаны как отдельный
  operator step.
- Delivery stops after repository-local ChangeRail tooling is verified and
  before known consumer migration unless the operator has renamed the GitHub
  repository to `changerail` and local `origin` points at the new URL.
- Known local consumer rewiring is verified one at a time from ignored
  operator inventory; session restart and project-local consumer publication
  that cannot be completed safely now are tracked in a separate follow-up card.

## Change Set
- `rename-public-identity`
- `rename-agent-command-surface`
- `rename-contracts-helpers-runtime`
- `update-bootstrap-consumer-migration`
- `migrate-known-consumers-to-changerail`

## Verify
- passed: `python3 -m py_compile bin/bootstrap-project bin/verify-project bin/changerail-delivery-runner bin/changerail-delivery-metrics bin/changerail-review-verdict scripts/changerail_review_verdict.py scripts/changerail_delivery_manifest.py scripts/smoke-bootstrap-project.py scripts/smoke-delivery-manifest.py scripts/smoke-delivery-metrics.py scripts/smoke-delivery-runner.py scripts/smoke-drift.py scripts/smoke-release-ci.py scripts/smoke-review-fingerprint.py scripts/smoke-verify-project.py scripts/smoke-wiring-discovery.py`
- passed: `python3 -m json.tool` for all `schemas/changerail-*.schema.json`
  and `.mcp.json`
- passed: TOML parse for `.codex/config.toml`
- passed: `./bin/openspec validate rename-public-identity --strict`
- passed: `./bin/openspec validate rename-agent-command-surface --strict`
- passed: `./bin/openspec validate rename-contracts-helpers-runtime --strict`
- passed: `./bin/openspec validate update-bootstrap-consumer-migration --strict`
- passed: `./bin/openspec validate --all --strict` after archive (14/14)
- passed: `python3 scripts/smoke-release-ci.py`
- passed: `python3 scripts/smoke-wiring-discovery.py` (118/118)
- passed: `python3 scripts/smoke-verify-project.py` (3/3, including stale
  OPSX wiring negative case)
- passed: `python3 scripts/smoke-bootstrap-project.py` (4/4)
- passed: generated-fixture drift smoke with
  `python3 scripts/smoke-drift.py --project .runtime/changerail/ci-drift/example-project`
- passed: `python3 scripts/smoke-delivery-manifest.py`
- passed: `python3 scripts/smoke-delivery-metrics.py`
- passed: `python3 scripts/smoke-review-fingerprint.py`
- passed: `python3 scripts/smoke-delivery-runner.py`
- passed: `git diff --check`
- passed: public-surface scan for known local consumer paths in tracked files
  outside ignored `internal/`
- passed: `git remote -v` points to
  `git@github.com:vlikhobabin/changerail.git`
- passed: consumer migration wiring completed for all selected consumers from
  ignored operator inventory
- passed: `/opt/changerail/bin/verify-project <project>` for every selected
  consumer; concrete project list and results are recorded in ignored
  `internal/changerail-consumer-inventory.md`
- passed: consumer stale wiring scan found no generic `/opt/opsx`,
  `.claude/commands/opsx`, `$opsx-*`, `/opsx:*`, `.codex/skills/opsx-*` or
  `bin/opsx-*` defaults in migrated root surfaces; frozen project-specific
  compatibility ids are documented in the owning consumer
- deferred: active agent processes were detected in one selected consumer after
  rewiring, so session restart/fresh-context checks and consumer repository
  publication are tracked in
  `openspec/board/1.backlog/finalize-known-consumer-migration-after-restart.md`

## Archive
- `openspec/changes/archive/2026-07-12-rename-public-identity/`
- `openspec/changes/archive/2026-07-12-rename-agent-command-surface/`
- `openspec/changes/archive/2026-07-12-rename-contracts-helpers-runtime/`
- `openspec/changes/archive/2026-07-12-update-bootstrap-consumer-migration/`
- `openspec/changes/archive/2026-07-12-migrate-known-consumers-to-changerail/`

## Related
- `README.md`
- `AGENTS.md`
- `AGENTS.shared.md`
- `docs/`
- `skills/`
- `claude/commands/`
- `schemas/`
- `bin/`
- `templates/project/`
- `scripts/`
- `.github/workflows/`
- `openspec/changes/rename-public-identity/`
- `openspec/changes/rename-agent-command-surface/`
- `openspec/changes/rename-contracts-helpers-runtime/`
- `openspec/changes/update-bootstrap-consumer-migration/`
- `openspec/changes/archive/2026-07-12-migrate-known-consumers-to-changerail/`
- `openspec/board/1.backlog/finalize-known-consumer-migration-after-restart.md`
- `internal/changerail-consumer-inventory.md` (machine-local, ignored)

## Result
Repository-local ChangeRail rename is implemented, verified, synced into main
specs and archived for all five changes. The GitHub rename gate passed, and
selected consumers were rewired and verified. Session-dependent restart and
consumer repository publication are deferred to a separate follow-up card.
Independent review returned `go`; the payload was committed as
`0625f93b13cdd988d9937db15b16fb26d0c97f8d` before this deterministic card-only
publish finalization.

## Next
- Follow up with
  `openspec/board/1.backlog/finalize-known-consumer-migration-after-restart.md`
  when active consumer sessions can be restarted safely.

## Change 1: `rename-public-identity`

### Why
`OPSX` collides with OpenSpec-related `opsx` terminology and makes onboarding
ambiguous.

### Goal
Rename the public product/repository identity to ChangeRail while keeping a
short migration note that OPSX was the previous name.

### Scope
- README, durable docs and architecture documents.
- Root repository policy docs.
- Versioning/changelog/release discipline references.
- Public examples and recommended contract path.

### Acceptance
- Product name is `ChangeRail`.
- Repository/path examples use `changerail` and `/opt/changerail`.
- Legacy `OPSX` mentions in active docs are limited to explicit migration
  notes.

### Depends On
- none

### Related
- `README.md`
- `docs/`
- `AGENTS.md`
- `AGENTS.shared.md`

## Change 2: `rename-agent-command-surface`

### Why
The command/skill namespace is the user-facing point where the OpenSpec
collision is most visible.

### Goal
Rename generic lifecycle skills and Claude wrappers from `opsx-*` and
`/opsx:*` to `changerail-*` and `/changerail:*`.

### Scope
- `skills/opsx-*` -> `skills/changerail-*`.
- `claude/commands/opsx/` -> `claude/commands/changerail/`.
- Repo-local `.codex/skills` and `.claude/commands` symlink wiring.
- Skill descriptions, handoff prompts and docs references.

### Acceptance
- New Claude commands are `/changerail:explore`, `/changerail:ff`,
  `/changerail:do`, `/changerail:review`, `/changerail:pub` and
  `/changerail:deliver`.
- New Codex skills are `$changerail-explore`, `$changerail-ff`,
  `$changerail-do`, `$changerail-review`, `$changerail-pub` and
  `$changerail-deliver`.
- `openspec-*` skills remain unchanged.
- No new project defaults install `/opsx:*` aliases.

### Depends On
- `rename-public-identity`

### Related
- `skills/`
- `claude/commands/`
- `.codex/skills/`
- `.claude/commands/`

## Change 3: `rename-contracts-helpers-runtime`

### Why
Machine-readable contracts and helper names need to match the new product
namespace, otherwise runtime evidence and review gates keep leaking the old
identity.

### Goal
Rename contract schema ids, helper wrappers, runtime directories and related
scripts to the ChangeRail namespace.

### Scope
- `schemas/opsx-*.schema.json` -> `schemas/changerail-*.schema.json`.
- `opsx.*.v1` schema ids -> `changerail.*.v1`.
- `bin/opsx-review-verdict`, `bin/opsx-delivery-runner`,
  `bin/opsx-delivery-metrics`.
- `scripts/opsx_*` helpers and smoke references.
- `.runtime/opsx/...` defaults and environment variable names.

### Acceptance
- Review verdict, delivery manifest, evidence index, delivery run and review
  history contracts validate with `changerail.*` schema ids.
- Helper names and generated runtime paths use `changerail`.
- Compatibility/migration docs identify the contract rename as a breaking
  namespace change.

### Depends On
- `rename-public-identity`

### Related
- `schemas/`
- `bin/`
- `scripts/`
- `docs/changerail-contracts.md`

## Change 4: `update-bootstrap-consumer-migration`

### Why
New consumers and existing consumers must be wired to ChangeRail directly, not
through stale OPSX paths or command names.

### Goal
Update bootstrap, verify, smoke, CI and runbooks for canonical ChangeRail
consumer wiring.

### Scope
- `bin/bootstrap-project` and `bin/verify-project`.
- `templates/project/`.
- `scripts/smoke-*` and release CI workflow.
- Wiring docs, migration guide, compatibility notes and adoption runbook.
- Generated placeholders such as `{{CHANGERAIL_ROOT}}`.

### Acceptance
- Fresh bootstrap creates `.claude/commands/changerail`,
  `.claude/skills`, `.codex/skills/changerail-*`, `bin/changerail-*`
  and `bin/openspec`.
- `verify-project` passes for a generated ChangeRail consumer.
- Release CI smoke passes with generated generic fixtures.
- Docs explain GitHub repo rename and local `origin` update.

### Depends On
- `rename-agent-command-surface`
- `rename-contracts-helpers-runtime`

### Related
- `bin/bootstrap-project`
- `bin/verify-project`
- `templates/project/`
- `scripts/`
- `.github/workflows/`
- `docs/consumer-adoption-runbook.md`

## Change 5: `migrate-known-consumers-to-changerail`

### Why
The rename is not complete operationally until existing local consumers stop
using `/opt/opsx`, `/opsx:*`, `$opsx-*` and `bin/opsx-*`.

### Goal
Provide a planned one-project-at-a-time migration protocol for the known local
consumer set, record completed rewiring/verification, and defer
session-dependent finalization to a separate card while keeping real project
names and paths in ignored operator inventory instead of this public board
card.

### Scope
- Before touching consumers, check that the GitHub repository has been renamed
  to `changerail` and local `origin` points to the new URL; otherwise stop and
  request the operator action.
- Stop or finish active agent sessions in each consumer before rewiring when
  possible.
- Update project-local `.claude`, `.codex`, `bin`, `AGENTS.md`, `CLAUDE.md`,
  `.mcp.json`, `.codex/config.toml` and runbooks.
- Remove stale OPSX wiring after ChangeRail verification is green.
- Record project-local verification in each consumer repository or ignored
  operator notes.
- Create a follow-up card when session restart or consumer repository
  publication must wait for active work.

### Acceptance
- Each known consumer is rewired independently from `/opt/opsx` to
  `/opt/changerail`.
- Each rewired consumer passes `/opt/changerail/bin/verify-project <project>`.
- Claude/Codex sessions in migrated consumers are restarted before using
  `/changerail:*` or `$changerail-*`, or an explicit follow-up card tracks that
  remaining operator action.
- No real consumer project names or paths are committed to the public
  ChangeRail repository.

### Depends On
- `update-bootstrap-consumer-migration`
- operator GitHub repository rename and local `origin` update

### Related
- `internal/changerail-consumer-inventory.md` (machine-local, ignored)
- `/opt/example-project` (generic example)

## Log
- 2026-07-12T05:55:02Z card created with consumer migration as a separate
  planned change; real local consumer list stored in ignored `internal/`.
- 2026-07-12T06:00:00Z `$opsx-ff` created apply-ready artifacts for
  `rename-public-identity`, `rename-agent-command-surface`,
  `rename-contracts-helpers-runtime`, `update-bootstrap-consumer-migration`
  and `migrate-known-consumers-to-changerail`; moved card to `3.inprogress`.
- 2026-07-12T06:00:00Z validation passed: all five changes strict-valid,
  `openspec validate --all --strict` 18/18, `git diff --check`, and tracked
  public-surface scan for known local consumer paths.
- 2026-07-12T06:24:00Z `$changerail-do` implemented repository-local
  ChangeRail rename, updated docs/templates/skills/commands/helpers/schemas,
  added stale OPSX verification gates and ran smoke checks.
- 2026-07-12T06:26:00Z archived `rename-public-identity`,
  `rename-agent-command-surface`, `rename-contracts-helpers-runtime` and
  `update-bootstrap-consumer-migration`; `openspec validate --all --strict`
  passed 14/14 after archive.
- 2026-07-12T06:27:00Z reached `migrate-known-consumers-to-changerail` gate:
  `git remote -v` still points to `git@github.com:vlikhobabin/opsx.git`, so
  delivery stopped before touching consumer repositories.
- 2026-07-12T06:35:00Z operator confirmed GitHub rename to
  `git@github.com:vlikhobabin/changerail.git`; local checkout moved to
  `/opt/changerail` and `origin` updated.
- 2026-07-12T06:41:00Z rewired all selected consumers from ignored inventory to
  ChangeRail/OpenSpec surfaces under `/opt/changerail`; project-specific domain
  overlays were preserved.
- 2026-07-12T06:41:00Z `/opt/changerail/bin/verify-project <project>` passed
  for every selected consumer; concrete results are recorded in ignored
  `internal/changerail-consumer-inventory.md`.
- 2026-07-12T06:42:00Z detected active agent processes in one selected
  consumer; delivery stopped at the session restart gate instead of terminating
  external sessions.
- 2026-07-12T07:35:47Z operator decided not to interrupt active work in other
  projects; created
  `openspec/board/1.backlog/finalize-known-consumer-migration-after-restart.md`
  for restart/fresh-context checks and consumer repository publication.
- 2026-07-12T07:40:00Z independent `$changerail-review` returned fresh `go`;
  only non-blocking minor finding was an outdated historical validation count
  in the card.
- 2026-07-12T07:41:00Z `$changerail-pub` committed reviewed payload as
  `0625f93b13cdd988d9937db15b16fb26d0c97f8d`; card moved to `4.done` as
  deterministic post-publish finalization before push.
