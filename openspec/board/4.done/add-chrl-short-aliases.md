# Добавить короткие алиасы `chrl-*` для ChangeRail команд

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Operator request: daily commands like `$changerail-deliver` are too long.
- Exploration decision: keep `changerail-*` as canonical names and add `chrl-*`
  as official ergonomic aliases.

## Summary
Добавить короткую публичную command surface для ежедневного использования:
`$chrl-*` для Codex skills и `/chrl:*` для Claude commands. Длинные
`changerail-*` и `/changerail:*` остаются canonical и поддерживаются без
deprecation.

## Acceptance
- Codex exposes official aliases:
  `$chrl-explore`, `$chrl-ff`, `$chrl-do`, `$chrl-review`, `$chrl-pub`,
  `$chrl-deliver`.
- Claude exposes official aliases:
  `/chrl:explore`, `/chrl:ff`, `/chrl:do`, `/chrl:review`, `/chrl:pub`,
  `/chrl:deliver`.
- Alias wrappers delegate to the canonical `changerail-*` contracts without
  duplicating lifecycle logic.
- Bootstrap templates install both canonical `changerail-*` and short `chrl-*`
  surfaces for new consumers.
- `verify-project` and smoke checks validate the short aliases in generated
  consumers.
- Docs present `chrl-*` as the recommended daily shorthand and `changerail-*`
  as the canonical/reference form.

## Change Set
- `add-chrl-short-aliases`

## Verify
- `./bin/openspec status --change add-chrl-short-aliases --json` -> complete
  before archive (`isComplete: true`).
- `./bin/openspec instructions apply --change add-chrl-short-aliases --json`
  -> apply instructions loaded; all 14 tasks completed.
- `./bin/openspec validate add-chrl-short-aliases --strict` -> passed
  (`Change 'add-chrl-short-aliases' is valid`) before archive.
- `./bin/openspec validate --all --strict` -> passed after spec sync (14 items)
  and after archive (13 items).
- Affected spec validation passed for `changerail-skill-surface`,
  `changerail-project-bootstrap`, `changerail-project-verification`,
  `changerail-wiring-discovery` and `changerail-agent-methodology`.
- `python3 -m json.tool .mcp.json` -> passed.
- `.codex/config.toml` parsed with `tomllib` -> `TOML_OK`.
- `git diff --check` -> passed.
- Untracked whitespace scan -> passed (`UNTRACKED_WHITESPACE_OK`).
- `python3 scripts/smoke-verify-project.py` -> passed (4/4).
- `python3 scripts/smoke-wiring-discovery.py` -> passed (168/168).
- `python3 scripts/smoke-bootstrap-project.py` -> passed (4/4).
- Public-surface scan for private/local names in changed public files ->
  `PUBLIC_SCAN_OK`.

## Archive
- `openspec/changes/archive/2026-07-12-add-chrl-short-aliases/`

## Related
- `skills/`
- `claude/commands/`
- `.codex/skills/`
- `.claude/commands/`
- `bin/bootstrap-project`
- `bin/verify-project`
- `templates/project/`
- `scripts/smoke-verify-project.py`
- `scripts/smoke-wiring-discovery.py`
- `docs/consumer-adoption-runbook.md`
- `docs/how-it-works.md`
- `docs/wiring-discovery.md`

## Result
Implemented short `chrl-*` and `/chrl:*` aliases, updated generated consumer
wiring, verification/smoke coverage, docs and synced specs. Card-owned
OpenSpec change is archived. Independent review cycle 1 returned fresh `go`
with no findings. Publish committed reviewed payload as `bbaadc7` before this
deterministic board finalization amend; final publish commit is recorded in git
history and publish summary.

## Next
- done

## Change 1: `add-chrl-short-aliases`

### Why
Ежедневные команды `changerail-*` и `/changerail:*` слишком длинные для
частого ручного использования, но они остаются canonical/reference surface.

### Goal
Добавить официальные короткие алиасы `chrl-*` и `/chrl:*`, которые делегируют
существующим ChangeRail contracts без дублирования lifecycle logic.

### Scope

- Add alias skill directories `skills/chrl-*` with `SKILL.md` frontmatter names
  matching the aliases.
- Add Claude command wrappers under `claude/commands/chrl/`.
- Wire repo-local and generated consumer symlinks for both alias families.
- Keep all core contracts, schema ids, runtime paths and docs internals under
  the `changerail` namespace; `chrl` is invocation ergonomics only.
- Do not remove or deprecate `changerail-*`.

### Acceptance
- Codex skill aliases `$chrl-explore`, `$chrl-ff`, `$chrl-do`,
  `$chrl-review`, `$chrl-pub` and `$chrl-deliver` are present and point readers
  to the corresponding canonical ChangeRail lifecycle contracts.
- Claude command aliases `/chrl:explore`, `/chrl:ff`, `/chrl:do`,
  `/chrl:review`, `/chrl:pub` and `/chrl:deliver` are present and delegate to
  the corresponding `/changerail:*` command contracts.
- Repo-local Codex symlinks and project bootstrap templates install both
  canonical `changerail-*` and short `chrl-*` command surfaces.
- `verify-project` and smoke coverage fail closed when a generated consumer is
  missing a required short alias.
- User-facing docs describe `chrl-*` as the recommended daily shorthand while
  preserving `changerail-*` as canonical/reference naming.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-12-add-chrl-short-aliases/`

## Log
- 2026-07-12T08:03:53Z card created from operator request for shorter
  ChangeRail commands.
- 2026-07-12T08:07:24Z accepted into `2.todo` with one ordered OpenSpec change:
  `add-chrl-short-aliases`.
- 2026-07-12T08:07:24Z OpenSpec artifacts completed and validated; moved to
  `3.inprogress` for delivery.
- 2026-07-12T08:21:33Z implemented alias surface, synced specs, completed
  verification and archived `add-chrl-short-aliases`.
- 2026-07-12T08:28:32Z independent review cycle 1 returned fresh `go` with no
  findings in `.runtime/changerail/reviews/add-chrl-short-aliases.json`.
- 2026-07-12T08:31:42Z publish committed reviewed payload as `bbaadc7` and
  moved card to `4.done` as deterministic post-publish board finalization.
