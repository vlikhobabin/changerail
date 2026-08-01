## Context

Bundled skills в `skills/*/SKILL.md` имеют YAML frontmatter, который агентские
runtime читают до загрузки skill body. Текущий `scripts/smoke-wiring-discovery.py`
извлекает только `name` простым `line.partition(":")`, поэтому smoke может
пройти при невалидном YAML в соседнем field. Это уже затронуло canonical
`changerail-deliver`, `changerail-do` и `changerail-pub`, где `description`
содержит `: ` без quotes.

## Goals / Non-Goals

**Goals:**
- Проверять полный YAML frontmatter всех bundled skills в deterministic local
  smoke.
- Сохранить существующую проверку `name == directory skill name`.
- Сделать regression fixture, который падает, если parser случайно снова станет
  string-only.
- Включить проверку в существующий release baseline через already-required
  wiring smoke.

**Non-Goals:**
- Не запускать real `codex exec` или discovery against live credentials.
- Не менять lifecycle prose или фазовое поведение skills.
- Не вводить новый public wire schema.

## Decisions

1. Use `PyYAML` as a pinned release dependency.
   - `yaml.safe_load` matches the needed class of YAML parsing for scalar,
     mapping and nested metadata frontmatter already present in bundled skills.
   - A pinned dependency is clearer than maintaining a partial YAML parser and
     safer than relying on runtime-specific Codex diagnostics.
   - `requirements-dev.txt` is already installed by CI and local release
     baseline virtualenv instructions, so this stays inside release tooling.

2. Keep validation inside `scripts/smoke-wiring-discovery.py`.
   - The script already enumerates all bundled skills for repo-local and
     consumer-example surfaces.
   - Strengthening its `check_skill_contract` path ensures both canonical and
     alias skills are checked wherever discovery wiring is checked.
   - The local release baseline already runs this smoke, so no separate command
     is needed.

3. Add a runtime-only negative fixture check.
   - The smoke will parse a generated `SKILL.md` frontmatter containing an
     unquoted scalar with `: ` and expect a parser failure.
   - The fixture lives only in ignored runtime output and is represented in the
     JSON report as a normal check.

## Risks / Trade-offs

- [Risk] The release baseline may run without installed dev dependencies. ->
  Existing baseline already fails if `ruff` is missing and points maintainers to
  `requirements-dev.txt`; `PyYAML` follows the same dependency contract.
- [Risk] Parser error messages vary between PyYAML versions. -> Smoke checks
  pass/fail and summary text, not exact exception wording.
- [Risk] Full parser validation finds more malformed bundled frontmatter than
  the original three files. -> That is desired fail-closed behavior; all
  bundled skills must be YAML-valid before publish.
