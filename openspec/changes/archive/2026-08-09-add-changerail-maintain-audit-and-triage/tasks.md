## 1. Skill and command surfaces

- [x] 1.1 Add canonical `skills/changerail-maintain/SKILL.md` with `audit` and
  `triage` workflows.
- [x] 1.2 Add `skills/chrl-maintain/SKILL.md` as a short alias that delegates to
  the canonical maintain contract.
- [x] 1.3 Add Claude wrappers for `/changerail:maintain` and `/chrl:maintain`.
- [x] 1.4 Wire repo-local `.codex/skills/` symlinks for both maintain skills.

## 2. Safety boundaries

- [x] 2.1 Document audit read-only behavior: scan/report only, no state,
  baseline, board, delivery, publish or external-system mutation.
- [x] 2.2 Document triage behavior: schema-valid ignored annotations and card
  previews by default.
- [x] 2.3 Document explicit `--write-cards` handoff to
  `bin/changerail-maintenance cards --write` without commit/push/publish.
- [x] 2.4 Document that fix mode is unavailable until card `060-06` and route
  mutation requests through normal ChangeRail card delivery.

## 3. Verification

- [x] 3.1 Run skill frontmatter validation through
  `python3 scripts/run-release-baseline.py`.
- [x] 3.2 Run `python3 scripts/public-surface-scan.py`.
- [x] 3.3 Run `./bin/openspec validate add-changerail-maintain-audit-and-triage
  --strict`.
- [x] 3.4 Run `./bin/openspec validate --all --strict`.
- [x] 3.5 Run `git diff --check`.
