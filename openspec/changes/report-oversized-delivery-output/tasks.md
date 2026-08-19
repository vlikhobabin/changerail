## 1. Operator summary

- [ ] 1.1 Add sanitized oversized-command summary output to
  `bin/changerail-delivery-runner`.
- [ ] 1.2 Include concise remediation guidance that points to bounded
  discovery patterns.
- [ ] 1.3 Reuse existing redaction helpers for URLs, token-like values and
  runtime paths.

## 2. Metrics and docs

- [ ] 2.1 Extend `bin/changerail-delivery-metrics` text/JSON/CSV output with
  oversized output fields.
- [ ] 2.2 Document output bytes separately from cached, uncached and total
  token usage.
- [ ] 2.3 Preserve `unknown` rendering when output metadata or token usage is
  unavailable.

## 3. Synthetic smoke

- [ ] 3.1 Add a synthetic oversized-output fixture to
  `scripts/smoke-delivery-runner.py`.
- [ ] 3.2 Assert bounded `status.json` size and absence of raw oversized
  payload.
- [ ] 3.3 Assert raw retained evidence stays under ignored `.runtime/changerail/`
  scope.

## 4. Verification

- [ ] 4.1 Run `python3 -m py_compile bin/changerail-delivery-runner bin/changerail-delivery-metrics`.
- [ ] 4.2 Run `python3 scripts/smoke-delivery-runner.py`.
- [ ] 4.3 Run relevant delivery metrics smoke coverage.
- [ ] 4.4 Run `./bin/openspec validate "report-oversized-delivery-output" --strict`.
- [ ] 4.5 Run `./bin/openspec validate --all --strict`.
- [ ] 4.6 Run `git diff --check`.
