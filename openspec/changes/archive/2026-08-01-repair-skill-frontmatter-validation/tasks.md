## 1. Skill Metadata
- [x] 1.1 Quote or otherwise repair invalid `description` frontmatter in
  `skills/changerail-deliver/SKILL.md`, `skills/changerail-do/SKILL.md` and
  `skills/changerail-pub/SKILL.md`.
- [x] 1.2 Add deterministic full-frontmatter YAML parsing to
  `scripts/smoke-wiring-discovery.py` for every bundled skill contract check.
- [x] 1.3 Add a negative smoke fixture proving `description: invalid: scalar`
  is rejected.

## 2. Release Baseline
- [x] 2.1 Pin the YAML parser dependency used by the release baseline.
- [x] 2.2 Ensure the existing release baseline and CI smoke path exercises the
  strengthened wiring discovery check without requiring networked Codex
  discovery or credentials.

## 3. Specs And Verification
- [x] 3.1 Sync updated `changerail-skill-surface`,
  `changerail-wiring-discovery` and `changerail-release-ci` requirements.
- [x] 3.2 Run YAML parse checks for all bundled skills and the negative fixture.
- [x] 3.3 Run `python3 scripts/smoke-wiring-discovery.py`.
- [x] 3.4 Run `python3 scripts/run-release-baseline.py`.
- [x] 3.5 Run `openspec validate --all --strict` and `git diff --check`.
