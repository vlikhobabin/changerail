# Защитить публичные данные и supply chain ChangeRail

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

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
- none yet

## Verify
- not started

## Archive
- not started

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
- `openspec/board/1.backlog/close-release-gate-and-docs-drift.md`

## Result
not started

## Next
- Triage security severity, select the portable consumer config model and split
  the story into 2-5 apply-ready changes.

## Log
- 2026-07-12T15:05:13Z card created from repository review findings about data
  minimization, public bootstrap safety, secret scanning and supply-chain risk.
