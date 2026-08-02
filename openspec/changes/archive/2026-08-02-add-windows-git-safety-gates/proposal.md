## Why

Windows generated, symlink и junction wiring могут раскрыть ChangeRail source,
ignored runtime state или credentials, если staging behavior выводится из
путей, а не из Git evidence. Fallback proof contract уже называет Git
preconditions, но нужны deterministic checks, которые реально упражняют
porcelain status, dry-run add и index inspection.

## What Changes

- Добавить Git safety fixtures для generated-copy, symlink и junction-style
  Windows wiring paths.
- Доказывать safe paths через `git status --porcelain`, `git add --dry-run` и
  index inspection до того, как wiring считается stageable.
- Добавить negative fixtures для unsafe dry-run/index results, ignored runtime
  state, credential-like files, project-owned divergence,
  rename/update/uninstall и partial cleanup cases.
- Держать ignore rules minimal, чтобы project-owned source оставался видимым
  для Git safety checks.
- Сохранять diagnostics sanitized: без credential values, private hostnames и
  private Windows paths.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `changerail-project-verification`: Git safety evidence и fail-closed checks
  для Windows generated, symlink и junction wiring.
- `changerail-project-bootstrap`: fallback proof и cleanup behavior, которые
  должны быть backed by Git status, dry-run add и index evidence.
- `changerail-windows-native-architecture`: concrete Git safety test model для
  generated, symlink и junction paths.
- `changerail-release-ci`: focused smoke coverage для Windows wiring Git safety
  в release baseline.

## Impact

- `bin/bootstrap-project`.
- `bin/verify-project`.
- `scripts/smoke-bootstrap-project.py`.
- `scripts/smoke-verify-project.py`.
- `scripts/run-release-baseline.py` и `.github/workflows/changerail-ci.yml`,
  если добавляются новые focused smoke commands.
- `docs/wiring-discovery.md`.
- OpenSpec specs для bootstrap, project verification, Windows architecture и
  release CI.
