# Поддержать timestamped card references в review preflight

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- none

## Series Index
- none

## Source
- Consumer preflight evidence: repository-mandated sortable UTC card ids such
  as `2026-08-30T09-30-11Z-example-card` cannot satisfy an exact published
  investigation authorization relation.

## Summary
Расширить только синтаксис exact card reference в review preflight: наряду с
обычным lowercase slug принимать sortable UTC timestamp-prefix с обязательными
`T` и `Z`, не ослабляя canonical board-path и exact-id проверки.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Acceptance
- Bare, filename и canonical board-path references с exact UTC timestamp id
  проходят `_reference_matches` и позволяют валидной authorization chain
  достигнуть обычного risk-routed preflight outcome.
- Произвольный mixed-case id, malformed timestamp, другой stem, non-board path
  и suffix mismatch остаются non-match.
- Focused smoke содержит retained assertion-failure RED и полный timestamped
  authorization-chain regression.
- Полный ChangeRail release baseline и public-surface scans проходят.

## Change Set
- `support-timestamped-card-reference-normalization`

## Verify
- `python3 scripts/smoke-review-preflight.py` -> PASS, including the retained
  assertion-failure RED before implementation and the timestamped full chain.
- `python3 scripts/smoke-contract-schemas.py` -> PASS, 28 schemas.
- `/opt/changerail/.runtime/changerail/ci-venv/bin/ruff check
  scripts/changerail_review_preflight.py scripts/smoke-review-preflight.py
  scripts/smoke-contract-schemas.py` -> PASS; the pinned CI venv was used
  because `ruff` is not installed in the worktree `PATH`.
- `python3 -m py_compile scripts/changerail_review_preflight.py
  scripts/smoke-review-preflight.py scripts/smoke-contract-schemas.py` -> PASS.
- `python3 scripts/public-surface-scan.py` -> PASS, 1294 files and 0 findings.
- `python3 scripts/public-surface-scan.py --history` -> PASS, 1294 current
  files and 0 history findings.
- `./bin/openspec validate --all --strict` -> PASS, 23/23.
- `git diff --check` -> PASS.
- `./bin/changerail-review-verdict preflight ... --normalize --json` -> PASS,
  `ready-for-llm-review`, ordinary/high route, scope clean, 7 production LOC.
- `./bin/changerail-evidence validate
  .runtime/changerail/evidence/fix-timestamped-card-reference-normalization/index.json
  --workspace "$PWD" --json` -> PASS; retained RED
  `semantic-red-invalid-utc-calendar` exited 1 and retained GREEN
  `semantic-green-valid-utc-calendar` exited 0.
- `PATH=/opt/changerail/.runtime/changerail/ci-venv/bin:$PATH python3
  scripts/run-release-baseline.py` -> PASS, 36/36 release steps; live Windows
  two-host smoke was not requested and the matrix retained its explicit
  `not-run` caveat.

## Archive
- `openspec/changes/archive/2026-08-30-support-timestamped-card-reference-normalization/`

## Related
- `scripts/changerail_review_preflight.py`
- `scripts/smoke-review-preflight.py`
- `openspec/specs/changerail-contracts/spec.md`

## Result
- Exact authorization relations now accept either the existing lowercase slug
  or the bounded `YYYY-MM-DDTHH-MM-SSZ-<lowercase-slug>` form.
- Timestamp prefixes pass a strict UTC calendar/time parse after the lexical
  match, so impossible dates, out-of-range times and year `0000` are rejected.
- General card discovery remains lowercase-only, while arbitrary mixed-case,
  malformed timestamps, unrelated stems and noncanonical paths remain closed.
- Matcher and full tracked-HEAD timestamped authorization-chain regressions are
  green together with the complete ChangeRail release baseline.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `support-timestamped-card-reference-normalization`

### Why
Current reference regexes accept only lowercase slugs, while consumer board
policies can require sortable UTC prefixes containing uppercase `T` and `Z`.

### Goal
Accept the exact UTC timestamped-id grammar at the existing authorization
relation boundary without accepting arbitrary uppercase identifiers.

### Scope
- Add one timestamped card-id alternative to review-preflight reference parsing.
- Add matcher-level negative cases and an end-to-end timestamped authorization
  chain smoke.
- Update the canonical ChangeRail contract requirement.

### Acceptance
- Card-level acceptance and verification pass.

### Depends On
- `fix-review-preflight-card-reference-normalization`

### Related
- `openspec/changes/support-timestamped-card-reference-normalization/`

## Log
- 2026-08-30T19:35:00Z deliver-ready compatibility card created from a
  deterministic consumer preflight stop.
- 2026-08-30T19:38:00Z fast-forwarded to one apply-ready change; strict
  OpenSpec validation passed 24/24.
- 2026-08-30T20:50:29Z implementation, spec sync and archive completed; focused
  gates and the 36-step release baseline passed, ready for normalized preflight.
- 2026-08-30T20:51:20Z derived manifest matched the working tree exactly and
  normalized ordinary preflight returned `ready-for-llm-review` at high effort.
- 2026-08-30T21:27:49Z independent review cycle 1 returned NO-GO: lexical
  width alone admitted impossible UTC values and retained RED evidence was
  absent.
- 2026-08-30T21:34:26Z cycle-1 blockers remediated with strict calendar/time
  validation, impossible-value assertions and validated retained RED/GREEN
  evidence; full verification and review cycle 2 pending.
- 2026-08-30T22:19:46Z post-remediation release baseline passed 36/36,
  including history scan, updated review-preflight regression and retained
  evidence smoke; manifest refresh and review cycle 2 pending.
- 2026-08-30T23:05:07Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
