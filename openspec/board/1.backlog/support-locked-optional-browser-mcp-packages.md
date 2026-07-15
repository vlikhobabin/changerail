# Поддержать locked optional browser MCP packages у consumers

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Source
- Consumer adoption feedback 2026-07-13.
- `docs/consumer-adoption-runbook.md`
- `docs/compatibility.md`
- `openspec/specs/changerail-project-verification/spec.md`

## Summary
ChangeRail `verify-project` требует, чтобы каждый автоматически запускаемый
через `npx` MCP package имел точную версию, присутствовал в
`mcp-npm-lock.json` и проходил registry integrity check. Existing consumers
могут обоснованно сохранять optional browser tooling, но текущий lock не
содержит `@playwright/mcp@0.0.68` и `chrome-devtools-mcp@0.20.3`, а parser не
распознаёт стандартную форму `npx --package=<package>@<version>`.

Нужно расширить generic supply-chain contract без включения browser MCP в
default bootstrap templates и без ослабления fail-closed проверки unpinned или
unlocked packages.

## Acceptance
- `mcp-npm-lock.json` содержит `@playwright/mcp@0.0.68` и
  `chrome-devtools-mcp@0.20.3` с точными версиями, `source: npm` и актуальными
  SRI integrity values, подтверждёнными trusted npm registry lookup.
- Change не обновляет browser MCP до более новых версий; upgrade остаётся
  отдельной release-задачей вне consumer adoption scope.
- `bin/verify-project` распознаёт exact package pins как в direct package
  argument, так и в стандартных формах `--package=<package>@<version>` и
  `--package <package>@<version>`.
- Unversioned, non-exact, unlocked и integrity-mismatched browser MCP packages
  продолжают завершать verification fail-closed с понятной диагностикой.
- Focused smoke покрывает успешные direct/`--package` forms и негативные случаи
  missing version, missing lock entry и tampered integrity.
- Optional browser MCP packages не добавляются в root `.mcp.json`, root
  `.codex/config.toml` или `templates/project/*`; default ChangeRail consumer
  сохраняет минимальный filesystem/context7 baseline.
- `docs/compatibility.md` и release/supply-chain guidance описывают approved
  optional consumer packages и trusted procedure обновления их pins.
- Public-surface и release gates проходят без consumer names, private paths,
  credentials или runtime artifacts в tracked payload.

## Change Set
- none yet

## Verify
- `npm view @playwright/mcp@0.0.68 version dist.integrity --json`
- `npm view chrome-devtools-mcp@0.20.3 version dist.integrity --json`
- `python3 scripts/smoke-verify-project.py`
- `python3 scripts/smoke-bootstrap-project.py`
- `./bin/openspec validate --all --strict`
- `python3 scripts/public-surface-scan.py`
- `python3 scripts/run-release-baseline.py`
- `git diff --check`
- `git status --short --ignored`

## Archive
- not started

## Related
- `mcp-npm-lock.json`
- `bin/verify-project`
- `scripts/smoke-verify-project.py`
- `scripts/smoke-bootstrap-project.py`
- `docs/compatibility.md`
- `docs/release-discipline.md`
- `openspec/specs/changerail-project-verification/spec.md`

## Result
not started

## Next
- Triage the generic optional-package contract, then fast-forward the accepted
  story into an implementation-sized OpenSpec change.

## Log
- 2026-07-13T00:00:00Z card created from consumer adoption feedback.
