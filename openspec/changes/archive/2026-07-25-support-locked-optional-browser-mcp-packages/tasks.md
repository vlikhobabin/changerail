## 1. Lock And Parser

- [x] 1.1 Confirm trusted npm registry integrity for `@playwright/mcp@0.0.68`
  and `chrome-devtools-mcp@0.20.3`.
- [x] 1.2 Add both exact package entries to `mcp-npm-lock.json` with `source:
  npm` and SRI integrity values.
- [x] 1.3 Update `bin/verify-project` to discover direct `npx` package args,
  `--package=<package>@<version>` and `--package <package>@<version>`.

## 2. Smoke Coverage

- [x] 2.1 Extend `scripts/smoke-verify-project.py` with passing direct and
  `--package` optional browser MCP fixtures.
- [x] 2.2 Cover fail-closed negative fixtures for missing version, missing lock
  entry and tampered integrity.
- [x] 2.3 Confirm optional browser MCP packages are absent from root `.mcp.json`,
  root `.codex/config.toml` and `templates/project/*`.

## 3. Docs And Specs

- [x] 3.1 Update `docs/compatibility.md` with the approved optional browser MCP
  package pins and trusted verification procedure.
- [x] 3.2 Update `docs/release-discipline.md` with release guidance for default
  and optional executable MCP pin changes.
- [x] 3.3 Sync delta specs into `openspec/specs/` before archive.

## 4. Verification

- [x] 4.1 Run `npm view @playwright/mcp@0.0.68 version dist.integrity --json`.
- [x] 4.2 Run `npm view chrome-devtools-mcp@0.20.3 version dist.integrity --json`.
- [x] 4.3 Run `python3 scripts/smoke-verify-project.py`.
- [x] 4.4 Run `python3 scripts/smoke-bootstrap-project.py`.
- [x] 4.5 Run `./bin/openspec validate support-locked-optional-browser-mcp-packages --strict`.
- [x] 4.6 Run `./bin/openspec validate --all --strict`.
- [x] 4.7 Run `python3 scripts/public-surface-scan.py`.
- [x] 4.8 Run `python3 scripts/run-release-baseline.py`.
- [x] 4.9 Run `git diff --check`.

## Verification Notes

- RED evidence is not applicable for the lock/doc portion of this change. The
  verifier smoke fixtures provide negative coverage for parser and
  supply-chain regressions.
- `npm view @playwright/mcp@0.0.68 version dist.integrity --json` returned
  version `0.0.68` with matching `sha512-oP9I9...P+zmHA==` SRI.
- `npm view chrome-devtools-mcp@0.20.3 version dist.integrity --json` returned
  version `0.20.3` with matching `sha512-6MlN...g5j6og==` SRI.
- `python3 -m json.tool mcp-npm-lock.json` passed.
- `python3 -m py_compile bin/verify-project scripts/smoke-verify-project.py`
  passed.
- `python3 scripts/smoke-verify-project.py` passed with 17/17 checks, including
  direct, `--package=`, `--package <package>` and optional browser MCP
  fail-closed fixtures.
- Synced delta specs into `openspec/specs/changerail-project-verification/spec.md`
  and `openspec/specs/changerail-release-discipline/spec.md`.
- `./bin/openspec validate changerail-project-verification --strict` passed.
- `./bin/openspec validate changerail-release-discipline --strict` passed.
- `./bin/openspec validate support-locked-optional-browser-mcp-packages --strict`
  passed.
- `python3 scripts/smoke-bootstrap-project.py` passed with 8/8 checks.
- `./bin/openspec validate --all --strict` passed with 14/14 items.
- `python3 scripts/public-surface-scan.py` passed with 523 files scanned and
  0 findings.
- `git diff --check` passed.
- `python3 scripts/run-release-baseline.py` passed with 25/25 steps.
- Independent review cycle 1 returned `no-go` with blocker `R1`: synced specs
  omitted pre-existing scenarios outside card scope.
- Restored omitted scenarios in
  `openspec/specs/changerail-project-verification/spec.md`,
  `openspec/specs/changerail-release-discipline/spec.md` and the archived delta
  specs before requesting fresh re-review.
- Post-review rescue rerun of `python3 scripts/run-release-baseline.py` passed
  with 25/25 steps after restoring omitted scenarios.
