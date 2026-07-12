# Защитить публичные данные и supply chain ChangeRail

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Комплексное ревью кода, документации и public-safety controls ChangeRail от
  2026-07-12.
- `AGENTS.md`
- `AGENTS.shared.md`
- `skills/changerail-do/references/changerail-delivery-manifest.md`

## Summary
Устранить пути, по которым ChangeRail может записать credentials или
machine-local identity в runtime и tracked artifacts, а также укрепить защиту
от выполнения плавающих third-party dependencies в профиле с полным доступом.

Текущая tracked-поверхность и reachable git history не показали очевидных
секретов или private home paths при выполненном ревью. Однако существующие gates
не дают достаточной гарантии: delivery manifest сохраняет raw remote URL,
connectivity diagnostics сохраняют raw URL, bootstrap рендерит абсолютный путь
consumer-проекта в предлагаемые к commit файлы, public-surface scan проверяет
только `/opt/*`, а filesystem MCP запускается через unpinned `npx -y` при
`approval_policy = "never"` и `sandbox_mode = "danger-full-access"`.

## Findings
- `scripts/changerail_delivery_manifest.py` записывает
  `git config --get remote.origin.url` как repository identity без удаления
  userinfo, tokens или sensitive query data.
- `bin/changerail-delivery-runner` записывает полный `--connectivity-url` и
  exception text в structured preflight status.
- Generated `AGENTS.md`, `.mcp.json`, `.codex/config.toml` и
  `openspec/config.yaml` содержат абсолютные `PROJECT_PATH` и
  `CHANGERAIL_ROOT`, после чего bootstrap предлагает добавить эти файлы в git.
- `.mcp.json`, `.codex/config.toml` и consumer templates запускают
  `@modelcontextprotocol/server-filesystem` без версии через `npx -y`; GitHub
  Actions используют mutable major tags вместо immutable commit SHA.
- `scripts/public-surface-scan.py` обнаруживает только non-allowlisted
  `/opt/<name>` и не является secret, home-path или history scanner.
- В репозитории нет tracked vulnerability reporting policy для публичных
  пользователей.

## Acceptance
- Repository identity и connectivity diagnostics никогда не сохраняют raw
  credentials, URL userinfo, access tokens или sensitive query values; focused
  tests покрывают HTTPS remote с user/password, token-like query parameters,
  SCP-style SSH remote и connectivity success/failure diagnostics.
- Runtime records сохраняют только минимально необходимую sanitized identity и
  endpoint metadata; документация явно описывает redaction guarantee и остаточный
  риск raw child logs.
- Bootstrap имеет документированный public-safe способ генерировать переносимые
  tracked файлы без private username, customer name или machine-local absolute
  path. Неизбежные machine-local значения находятся в ignored local override
  или требуют явного opt-in с предупреждением до предложенного `git add`.
- `verify-project` умеет проверить выбранную portable/local config model и не
  вынуждает публичный consumer коммитить private absolute paths.
- Все автоматически исполняемые npm MCP dependencies закреплены точной версией
  и воспроизводимым integrity/lock mechanism либо устанавливаются через
  документированный trusted setup step. CI actions закреплены immutable SHA с
  читаемым version comment и процессом обновления.
- Public security gate включает специализированный secret scan и проверки
  распространенных Linux/macOS/Windows home paths. Safe test fixtures
  доказывают, что token-like assignment, private path и historical leak
  обнаруживаются, а generic examples остаются разрешены.
- Reachable git history проверяется отдельным documented release command или CI
  mode; scanner не печатает найденный secret целиком в публичный log.
- Добавлен публичный `SECURITY.md` или эквивалентный документ с supported
  versions, private disclosure channel и правилами для security reports.
- Public-safety verification подтверждает отсутствие реальных secrets, private
  workspace names и machine-local paths в итоговом tracked payload.

## Change Set
- `redact-runtime-identities`
- `add-portable-bootstrap-config`
- `pin-executable-supply-chain`
- `expand-public-surface-secret-scan`
- `add-security-disclosure-policy`

## Verify
- passed: `python3 -m py_compile scripts/changerail_delivery_manifest.py bin/changerail-delivery-runner scripts/smoke-delivery-manifest.py scripts/smoke-delivery-runner.py`
- passed: `python3 scripts/smoke-delivery-manifest.py`
- passed: `python3 scripts/smoke-delivery-runner.py`
- passed: `python3 -m py_compile bin/bootstrap-project bin/verify-project scripts/smoke-bootstrap-project.py scripts/smoke-verify-project.py`
- passed: `python3 -m py_compile bin/verify-project scripts/public-surface-scan.py scripts/smoke-verify-project.py scripts/smoke-bootstrap-project.py scripts/smoke-release-ci.py`
- passed: `python3 scripts/smoke-bootstrap-project.py` (5/5)
- passed: `python3 scripts/smoke-verify-project.py` (8/8)
- observed: `./bin/verify-project . --json` returned non-zero as expected for
  the source repository while confirming the live `MCP npm pins` registry
  integrity check passed.
- passed: `npm view @modelcontextprotocol/server-filesystem@2026.7.10 dist.integrity --json`
- passed: `npm view @upstash/context7-mcp@2.1.6 dist.integrity --json`
- passed: `python3 -m json.tool .mcp.json`
- passed: `python3 -m json.tool mcp-npm-lock.json`
- passed: TOML parse for `.codex/config.toml`
- passed: `python3 scripts/smoke-release-ci.py` (31/31)
- passed: `python3 -m py_compile scripts/public-surface-scan.py scripts/smoke-release-ci.py`
- passed: `python3 scripts/public-surface-scan.py --self-test` (includes a
  default-root fixture proving root `.mcp.json` token-like assignments are
  detected and redacted)
- passed: `python3 scripts/public-surface-scan.py --json` (0 findings across
  394 default public-root files, including root config and policy files)
- passed: `python3 scripts/public-surface-scan.py --history --json` (0 findings
  across reachable history for the same default roots)
- passed: `./bin/openspec validate --all --strict`
- passed: `git diff --check`

## Archive
- `openspec/changes/archive/2026-07-12-redact-runtime-identities/`
- `openspec/changes/archive/2026-07-12-add-portable-bootstrap-config/`
- `openspec/changes/archive/2026-07-12-pin-executable-supply-chain/`
- `openspec/changes/archive/2026-07-12-expand-public-surface-secret-scan/`
- `openspec/changes/archive/2026-07-12-add-security-disclosure-policy/`

## Related
- `AGENTS.md`
- `AGENTS.shared.md`
- `.mcp.json`
- `.codex/config.toml`
- `.github/workflows/changerail-ci.yml`
- `bin/bootstrap-project`
- `bin/changerail-delivery-runner`
- `bin/verify-project`
- `scripts/changerail_delivery_manifest.py`
- `scripts/public-surface-scan.py`
- `templates/project/AGENTS.md.tpl`
- `templates/project/mcp.json.tpl`
- `templates/project/codex-config.toml.tpl`
- `templates/project/openspec/config.yaml.tpl`
- `skills/changerail-do/references/changerail-delivery-manifest.md`
- `openspec/changes/archive/2026-07-12-redact-runtime-identities/`
- `openspec/changes/archive/2026-07-12-add-portable-bootstrap-config/`
- `openspec/changes/archive/2026-07-12-pin-executable-supply-chain/`
- `openspec/changes/archive/2026-07-12-expand-public-surface-secret-scan/`
- `openspec/changes/archive/2026-07-12-add-security-disclosure-policy/`
- `openspec/board/1.backlog/close-release-gate-and-docs-drift.md`

## Result
Implemented. Runtime repository/connectivity identities are sanitized;
bootstrap defaults to portable tracked config with explicit local opt-in;
MCP npm packages and CI actions are pinned, and MCP lock integrity is compared
against npm registry metadata during trusted setup verification; public-surface
scan covers token-like assignments, home paths, reachable history and narrow
placeholder allowlisting; `SECURITY.md` is tracked and linked from public docs.

Published reviewed payload as `4b099e0acf569c71034a07a7db05ff6f664a090d`; push status `pending` on `main`/`origin`.

## Next
- done

## Change 1: `redact-runtime-identities`

### Why
Runtime handoff records and runner preflight diagnostics are useful to
reviewers, but raw remotes and connectivity URLs can contain credentials,
tokens, private usernames or sensitive query values.

### Goal
Sanitize repository identity and connectivity diagnostics before they enter
structured runtime records, while documenting the remaining risk of raw child
logs.

### Scope
- `scripts/changerail_delivery_manifest.py`
- `bin/changerail-delivery-runner`
- `scripts/smoke-delivery-manifest.py`
- `scripts/smoke-delivery-runner.py`
- `docs/changerail-contracts.md`
- `skills/changerail-do/references/changerail-delivery-manifest.md`

### Acceptance
- HTTPS remotes with user/password or token-like query values are recorded
  without raw credentials.
- SCP-style SSH remotes keep useful host/repository identity without recording
  userinfo as a credential-bearing identity.
- Connectivity pass/fail preflight records include only sanitized endpoint
  metadata and exception class, not the submitted URL or sensitive query.
- Docs describe the redaction guarantee and residual raw child log risk.

### Depends On
- none

### Related
- `openspec/changes/redact-runtime-identities/`

## Change 2: `add-portable-bootstrap-config`

### Why
Generated consumer files are proposed for commit, but current templates render
absolute project paths and ChangeRail root paths into tracked files.

### Goal
Make portable tracked consumer config the default, reserve machine-local
absolute paths for explicit local opt-in, and teach verification to validate
the selected config model.

### Scope
- `bin/bootstrap-project`
- `bin/verify-project`
- `templates/project/AGENTS.md.tpl`
- `templates/project/CLAUDE.md.tpl`
- `templates/project/mcp.json.tpl`
- `templates/project/codex-config.toml.tpl`
- `templates/project/openspec/config.yaml.tpl`
- `templates/project/README.md`
- `scripts/smoke-bootstrap-project.py`
- `scripts/smoke-verify-project.py`

### Acceptance
- Default bootstrap output contains no private username, customer name or
  machine-local absolute project path in tracked files.
- Any local absolute-path config mode requires explicit opt-in and prints a
  warning before the suggested `git add`.
- `verify-project` accepts the portable model and rejects missing or unsafe
  project scope.

### Depends On
- `redact-runtime-identities`

### Related
- `openspec/changes/add-portable-bootstrap-config/`

## Change 3: `pin-executable-supply-chain`

### Why
The local profile has full filesystem access and no approval prompts, so
floating executable dependencies in MCP config and CI action tags are too much
ambient trust.

### Goal
Pin automatically executed npm MCP packages and CI actions to immutable,
auditable versions with a documented update path.

### Scope
- `.mcp.json`
- `.codex/config.toml`
- `.github/workflows/changerail-ci.yml`
- `templates/project/mcp.json.tpl`
- `templates/project/codex-config.toml.tpl`
- `bin/verify-project`
- `scripts/smoke-release-ci.py`
- `docs/compatibility.md`
- `docs/release-discipline.md`

### Acceptance
- Filesystem and Context7 MCP npm packages are exact-version pinned and covered
  by a tracked integrity lock or documented trusted setup contract.
- Generated consumers inherit the same pinning model.
- Release CI actions use immutable commit SHAs with readable version comments
  and docs explain how to update them.

### Depends On
- `add-portable-bootstrap-config`

### Related
- `openspec/changes/pin-executable-supply-chain/`

## Change 4: `expand-public-surface-secret-scan`

### Why
The current public-surface scanner catches only non-generic `/opt/*` paths and
does not search for token-like assignments, home paths or historical leaks.

### Goal
Add a public safety gate that detects common secret and machine-local path
patterns in current tracked files and reachable git history without printing
secret values in logs.

### Scope
- `scripts/public-surface-scan.py`
- `.github/workflows/changerail-ci.yml`
- `AGENTS.md`
- `AGENTS.shared.md`
- `docs/release-discipline.md`

### Acceptance
- Safe fixtures prove token-like assignment, Linux/macOS/Windows home path and
  historical leak detection.
- Generic examples remain allowed.
- Findings redact secret values and do not print full matched secrets.
- A documented release command or CI mode scans reachable git history.

### Depends On
- `pin-executable-supply-chain`

### Related
- `openspec/changes/expand-public-surface-secret-scan/`

## Change 5: `add-security-disclosure-policy`

### Why
Public users need a tracked, non-public disclosure path for suspected
vulnerabilities, especially because ChangeRail operates agent tooling with
filesystem and supply-chain impact.

### Goal
Publish a security policy and connect it to release/public-safety verification.

### Scope
- `SECURITY.md`
- `README.md`
- `docs/release-discipline.md`
- `openspec/specs/changerail-release-discipline/spec.md`

### Acceptance
- `SECURITY.md` describes supported versions, private disclosure channel,
  report content guidelines and what not to include in public issues.
- Public docs link to the policy without adding private contact details or
  local workspace names.
- Public-safety verification confirms the final tracked payload has no real
  secrets, private workspace names or machine-local paths.

### Depends On
- `expand-public-surface-secret-scan`

### Related
- `openspec/changes/add-security-disclosure-policy/`

## Log
- 2026-07-12T15:05:13Z card created from repository review findings about data
  minimization, public bootstrap safety, secret scanning and supply-chain risk.
- 2026-07-12T16:00:00Z fast-forward planned five apply-ready changes and moved
  card to `2.todo`.
- 2026-07-12T16:58:00Z implemented, verified, synced and archived all five
  card-owned changes; card moved to `3.inprogress` for independent review.
- 2026-07-12T17:26:33Z review cycle 1 returned `no-go`; fixed MCP npm
  trusted setup integrity verification and narrowed scanner placeholder
  allowlisting, then reran focused verification for re-review.
- 2026-07-12T18:05:24Z review cycle 2 returned `no-go` on incomplete default
  public-surface scanner root coverage; included tracked root config/policy
  files in default roots, added a root `.mcp.json` token-like fixture, and
  reran focused release/OpenSpec verification for re-review.
- 2026-07-12T18:16:27Z publish finalized card into `4.done` with commit `4b099e0acf569c71034a07a7db05ff6f664a090d` and push status `pending`.
