## 1. Bootstrap And Templates

- [x] 1.1 Update `bin/bootstrap-project` to use ChangeRail source names, placeholders and symlink targets.
- [x] 1.2 Update `templates/project/**` to render `/opt/changerail`, `/changerail:*`, `changerail-*` and `bin/changerail-*` defaults.
- [x] 1.3 Preserve bootstrap refusal for non-empty existing targets and document adoption flow for existing projects.

## 2. Verification And Smoke

- [x] 2.1 Update `bin/verify-project` to validate ChangeRail consumer wiring and fail stale OPSX defaults.
- [x] 2.2 Update wiring, bootstrap, verify, drift and release smoke scripts for generated ChangeRail fixtures.
- [x] 2.3 Rename/update CI workflow references for ChangeRail release gates.

## 3. Docs And Migration

- [x] 3.1 Update wiring discovery, compatibility, migration and consumer adoption runbooks.
- [x] 3.2 Document the operator sequence for GitHub repository rename and local `origin` update.
- [x] 3.3 Keep real consumer project names and paths out of tracked docs.

## 4. Verification

- [x] 4.1 Run `python3 scripts/smoke-release-ci.py`.
- [x] 4.2 Run `python3 scripts/smoke-bootstrap-project.py`.
- [x] 4.3 Run `python3 scripts/smoke-verify-project.py`.
- [x] 4.4 Run `python3 scripts/smoke-wiring-discovery.py`.
- [x] 4.5 Run drift smoke against a generated ChangeRail fixture.
- [x] 4.6 Run `./bin/openspec validate update-bootstrap-consumer-migration --strict`.
- [x] 4.7 Run `git diff --check`.
