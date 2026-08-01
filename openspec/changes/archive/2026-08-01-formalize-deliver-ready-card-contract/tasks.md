## 1. Methodology And Board Guidance

- [x] 1.1 Update shared methodology to define `deliver-ready` as an accepted
  `2.todo` card predicate and `$chrl-deliver` as the normal handoff.
- [x] 1.2 Update root board docs and practical workflow docs to keep five board
  columns and explain that OpenSpec artifacts are created by `deliver`/`ff`.

## 2. Lifecycle Skill Wording

- [x] 2.1 Update `changerail-deliver` guidance so accepted ordered cards can be
  handed to one-command delivery before artifacts exist.
- [x] 2.2 Update `changerail-ff` handoff wording so direct `ff` remains an
  explicit planning/repair surface, not a required pre-step for `deliver`.

## 3. Project Templates

- [x] 3.1 Update generated board README template to define `deliver-ready`
  without adding a sixth column.
- [x] 3.2 Update generated card template so maintainers can prepare a
  deliver-ready card without creating premature OpenSpec change directories.

## 4. Verification

- [x] 4.1 Run `openspec validate "formalize-deliver-ready-card-contract" --strict`.
- [x] 4.2 Run `openspec validate --all --strict`.
- [x] 4.3 Run docs/template consistency smoke for `deliver-ready`,
  `$chrl-deliver` and board columns.
- [x] 4.4 Run `python3 scripts/smoke-bootstrap-project.py`.
- [x] 4.5 Run skill/frontmatter discovery smoke or release baseline covering
  lifecycle skill metadata.
- [x] 4.6 Run `git diff --check`.
- [x] 4.7 Run public-surface scan for touched tracked docs/templates/skills and
  OpenSpec artifacts.

## Verification Notes

- `openspec validate formalize-deliver-ready-card-contract --strict` passed.
- `openspec validate --all --strict` passed with 15 items.
- Docs/template consistency smoke for `deliver-ready`, `$chrl-deliver` and
  five board columns passed.
- `python3 scripts/smoke-bootstrap-project.py` passed: 8/8 checks.
- `python3 scripts/smoke-wiring-discovery.py` passed: 172/172 checks.
- `git diff --check` plus trailing-whitespace scan for untracked files passed.
- `python3 scripts/public-surface-scan.py ...` passed for touched docs,
  templates, skills and OpenSpec artifacts: 15 files, 0 findings.
- RED evidence is not applicable because this is a docs/templates/skill-contract
  wording change without executable behavior under test.
