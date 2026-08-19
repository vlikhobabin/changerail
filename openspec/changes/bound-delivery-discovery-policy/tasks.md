## 1. Delivery skill policy

- [ ] 1.1 Update `skills/changerail-deliver/SKILL.md` to require bounded
  discovery patterns before broad output reads.
- [ ] 1.2 Document that truncated command output and exit-130 truncation are
  inconclusive evidence requiring narrower follow-up.
- [ ] 1.3 Add reviewable examples of acceptable discovery evidence without
  embedding repository-specific source content.

## 2. Runner child handoff

- [ ] 2.1 Add a compact discovery budget/policy handoff to
  `bin/changerail-delivery-runner` child launch.
- [ ] 2.2 Keep the policy public-safe and independent of shell interception or
  codebase language.
- [ ] 2.3 Add focused runner smoke coverage proving the child receives the
  policy.

## 3. Verification

- [ ] 3.1 Run `python3 -m py_compile bin/changerail-delivery-runner`.
- [ ] 3.2 Run `python3 scripts/smoke-delivery-runner.py`.
- [ ] 3.3 Run `./bin/openspec validate "bound-delivery-discovery-policy" --strict`.
- [ ] 3.4 Run `./bin/openspec validate --all --strict`.
- [ ] 3.5 Run `git diff --check`.
