## MODIFIED Requirements

### Requirement: Release CI focused smoke inventory
ChangeRail release CI MUST разделять Linux-focused stable admission и тяжёлое
regression coverage. Default push/pull-request workflow MUST владеть только
точным упорядоченным `core` inventory, который выводит
`python3 scripts/run-release-baseline.py --suite core --list`. Отдельный
scheduled/manual workflow MUST вызывать ровно
`python3 scripts/run-release-baseline.py --suite extended` и MUST владеть только
точным упорядоченным `extended` inventory. Оба inventory MUST отклонять
missing, extra, duplicate или overlapping commands, а one-command delivery
regression `python3 scripts/smoke-delivery-runner.py` MUST принадлежать только
`extended`.

Command identity MUST задаваться как exact argv, а не shell-equivalent prose.
Упорядоченный `core` inventory MUST быть ровно таким:

1. `["./bin/openspec", "validate", "--all", "--strict"]`
2. `["python3", "-m", "json.tool", ".mcp.json"]`
3. `["python3", "-c", "import tomllib; tomllib.load(open('.codex/config.toml', 'rb')); print('TOML_OK')"]`
4. `["python3", "scripts/smoke-codex-launcher.py"]`
5. `["python3", "scripts/smoke-contract-schemas.py"]`
6. `["python3", "scripts/compile-python-inventory.py"]`
7. `["python3", "scripts/smoke-python-runtime.py"]`
8. `["ruff", "check", "bin", "scripts"]`
9. `["python3", "scripts/smoke-source-distribution.py"]`
10. `["python3", "scripts/smoke-release-ci.py"]`
11. `["python3", "scripts/public-surface-scan.py", "--self-test"]`
12. `["python3", "scripts/smoke-public-surface-history.py"]`
13. `["python3", "scripts/public-surface-scan.py"]`
14. `["python3", "scripts/public-surface-scan.py", "--history"]`
15. `["python3", "scripts/smoke-wiring-discovery.py"]`
16. `["python3", "scripts/smoke-verify-project.py"]`
17. `["python3", "scripts/smoke-runtime-diagnostics.py"]`
18. `["python3", "scripts/smoke-bootstrap-project.py"]`
19. `["python3", "scripts/smoke-consumer-ci.py"]`
20. `["rm", "-rf", ".runtime/changerail/ci-drift"]`
21. `["./bin/bootstrap-project", ".runtime/changerail/ci-drift/example-project", "--name", "example-project", "--kind", "generic", "--lock-enforcement", "none"]`
22. `["python3", "scripts/smoke-drift.py", "--project", ".runtime/changerail/ci-drift/example-project"]`
23. `["git", "diff", "--check"]`
24. `["git", "status", "--short", "--ignored"]`

Упорядоченный `extended` inventory MUST быть ровно таким:

1. `["python3", "scripts/smoke-review-verdict-validation.py"]`
2. `["python3", "scripts/smoke-review-fingerprint.py"]`
3. `["python3", "scripts/smoke-review-fingerprint-benchmark.py"]`
4. `["python3", "scripts/smoke-review-fingerprint-cache.py"]`
5. `["python3", "scripts/smoke-review-preflight.py"]`
6. `["python3", "scripts/smoke-retained-evidence.py"]`
7. `["python3", "scripts/smoke-maintenance-runner.py"]`
8. `["python3", "scripts/smoke-delivery-manifest.py"]`
9. `["python3", "scripts/smoke-delivery-manifest-derive.py"]`
10. `["python3", "scripts/smoke-delivery-runner.py"]`
11. `["python3", "scripts/smoke-delivery-metrics.py"]`
12. `["python3", "scripts/smoke-openspec-archive-diagnostics.py"]`

Windows entrypoint, wiring Git-safety и aggregate matrix commands MUST
оставаться explicit opt-in diagnostics вне обеих suites.

#### Scenario: Core focused smoke coverage regresses
- **WHEN** tracked default workflow или runner теряет, добавляет, переставляет
  или дублирует required core command
- **THEN** `scripts/smoke-release-ci.py` завершается с ошибкой до принятия
  workflow change

#### Scenario: Default CI invokes core runner
- **WHEN** tracked default push/pull-request workflow запускается после
  dependency setup
- **THEN** он вызывает ровно `python3 scripts/run-release-baseline.py`
- **AND** не вызывает extended suite или принадлежащий ей smoke напрямую

#### Scenario: Extended focused smoke coverage regresses
- **WHEN** tracked extended workflow отсутствует, теряет schedule/manual trigger
  или больше не вызывает exact extended suite command
- **THEN** `scripts/smoke-release-ci.py` завершается с ошибкой
- **AND** default CI не поглощает и не дублирует extended coverage неявно

#### Scenario: Suite command ownership regresses
- **WHEN** command назначена обоим inventory, добавлена undeclared command или
  удалена expected command
- **THEN** CI contract smoke завершается fail-closed

#### Scenario: One-command delivery ownership regresses
- **WHEN** `python3 scripts/smoke-delivery-runner.py` отсутствует в extended или
  появляется в default core
- **THEN** exact inventory oracle завершается с ошибкой
- **AND** release evidence не может утверждать, что какая-либо suite прошла
