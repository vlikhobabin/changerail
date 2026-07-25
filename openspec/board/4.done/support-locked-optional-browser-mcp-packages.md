# Поддержать locked optional browser MCP packages у consumers

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

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
- `support-locked-optional-browser-mcp-packages`

## Verify
- `npm view @playwright/mcp@0.0.68 version dist.integrity --json` -> passed;
  returned version `0.0.68` and
  `sha512-oP9I9ghXKuQEBo4xaC7HgsS2gRTxyMzlBm3UEhYj4VqqrqbPQUX2shATPaNA/am9joBzq9v0OXISzeIgP+zmHA==`.
- `npm view chrome-devtools-mcp@0.20.3 version dist.integrity --json` ->
  passed; returned version `0.20.3` and
  `sha512-6MlNKlKa+J1FX9w4SUnFERF4MRGWLlrnZvIJGhhsuuMPM7qUG0F4SwheRyjwl0+tsTemxMCBHiib8mXkg5j6og==`.
- `python3 -m json.tool mcp-npm-lock.json` -> passed.
- `python3 -m py_compile bin/verify-project scripts/smoke-verify-project.py`
  -> passed.
- `python3 scripts/smoke-verify-project.py` -> passed with 17/17 checks,
  including direct, `--package=`, `--package <package>` and optional browser
  MCP fail-closed fixtures.
- `python3 scripts/smoke-bootstrap-project.py` -> passed with 8/8 checks.
- `./bin/openspec validate support-locked-optional-browser-mcp-packages --strict`
  -> passed before archive.
- `./bin/openspec validate --all --strict` -> passed before archive with 14/14
  items and after archive with 13/13 items.
- `python3 scripts/public-surface-scan.py` -> passed with 523 files scanned and
  0 findings.
- `python3 scripts/run-release-baseline.py` -> passed with 25/25 steps.
- Post-review rescue rerun of `python3 scripts/run-release-baseline.py` ->
  passed with 25/25 steps after restoring omitted scenarios.
- `git diff --check` -> passed before archive and after archive.

## Archive
- `openspec/changes/archive/2026-07-25-support-locked-optional-browser-mcp-packages/`

## Related
- `openspec/changes/archive/2026-07-25-support-locked-optional-browser-mcp-packages/`
- `mcp-npm-lock.json`
- `bin/verify-project`
- `scripts/smoke-verify-project.py`
- `scripts/smoke-bootstrap-project.py`
- `docs/compatibility.md`
- `docs/release-discipline.md`
- `openspec/specs/changerail-project-verification/spec.md`

## Result
implemented, verified, synced and archived; awaiting independent review

Published reviewed payload as `7dd7984`; push status `pending` on `main`/`origin`.

## Next
- done

## Change 1: `support-locked-optional-browser-mcp-packages`

### Why
Consumer projects can keep optional browser MCP tooling, but ChangeRail needs
the same exact-version lock and registry-integrity gate for those packages as it
uses for default MCP packages.

### Goal
Support locked optional browser MCP package verification without adding browser
MCP packages to default ChangeRail config or bootstrap templates.

### Scope
- Add lock metadata for `@playwright/mcp@0.0.68` and
  `chrome-devtools-mcp@0.20.3`.
- Update `bin/verify-project` package parsing for direct and `--package` npx
  forms.
- Add smoke coverage for successful optional package forms and fail-closed
  package/version/integrity defects.
- Update compatibility and release supply-chain guidance.

### Acceptance
- Card acceptance criteria are covered by
  `openspec/changes/support-locked-optional-browser-mcp-packages/`.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-25-support-locked-optional-browser-mcp-packages/`

## Log
- 2026-07-13T00:00:00Z card created from consumer adoption feedback.
- 2026-07-25T00:00:00Z fast-forwarded into
  `support-locked-optional-browser-mcp-packages`.
- 2026-07-25T06:20:19Z trusted npm registry lookup confirmed exact browser MCP
  SRI values.
- 2026-07-25T06:27:00Z implemented parser, lock, smoke and docs changes;
  release baseline passed; OpenSpec change archived.
- 2026-07-25T06:35:51Z independent review cycle 1 returned `no-go` with
  blocker `R1`: synced specs omitted pre-existing scenarios outside card scope.
- 2026-07-25T06:42:00Z restored omitted scenarios in synced main specs and
  archived delta specs.
- 2026-07-25T06:42:20Z post-review rescue verification passed:
  `python3 scripts/run-release-baseline.py` 25/25.
- 2026-07-25T06:51:31Z publish finalized card into `4.done` with commit `7dd7984` and push status `pending`.

