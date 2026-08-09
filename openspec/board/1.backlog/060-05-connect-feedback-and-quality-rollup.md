# Подключить feedback и quality rollup

## Status
1.backlog

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`060-repository-knowledge-maintenance`

## Series Index
`05`

## Planning State
post-MVP story; blocked on structured lifecycle and operational evidence

## Source
- `060-00-repository-knowledge-maintenance-program-epic.md`
- Existing `changerail.delivery-run.v1` and
  `changerail.review-cycle-history.v1` runtime contracts.
- Existing `changerail-delivery-metrics` structured observability approach.

## Summary
Нормализовать feedback из review/blocked delivery и external producers в
maintenance findings, добавить quality rollup и полное ChangeRail dogfooding без
парсинга свободного текста или централизованной mutation consumer repositories.

## Acceptance
- Feedback adapters читают schema-valid review-cycle history и delivery-run
  records; arbitrary log/prose scraping не является supported input.
- Review finding сохраняет source record reference, original finding id,
  severity и affected relative paths без изменения frozen review schema ids.
- Blocked-run adapter использует structured terminal outcome/reason/evidence;
  неизвестный или legacy prose-only blocker классифицируется как unsupported,
  а не как доказанная maintenance finding.
- External producer protocol принимает schema-bound findings через detector
  adapter boundary из `060-02`; consumer-specific retrospective остается у
  consumer.
- Feedback normalization использует те же identity/evidence fingerprint rules
  и board dedup contract, что deterministic scan.
- Quality rollup читает structured maintenance reports/state и показывает как
  минимум catalog coverage, open/resolved/waived findings, stale/generated
  findings, duplicate-card prevention, instruction bytes when available,
  time-to-triage и accepted/rejected fix proposals.
- Missing optional metrics выводятся как `unknown`, а не как zero.
- Rollup поддерживает human-readable, JSON и stable CSV output без изменения
  existing delivery metrics columns.
- ChangeRail dogfood catalog покрывает canonical docs и fixtures для broken
  link/anchor, stale generated index, instruction overflow producer и canonical
  source contradiction annotation.
- Semantic contradiction остается agent annotation with retained evidence;
  один LLM verdict не превращается в deterministic gate.
- Никакой feedback adapter по умолчанию не создает card, commit, comment, PR или
  external mutation.

## Depends On
- `060-03-add-maintenance-findings-lifecycle`
- `060-04-add-maintain-skill-and-scheduler-adapters`
- Structured instruction-budget producer from card `050` for that optional
  dogfood scenario.

## Change Set
- none yet

## Verify
- Review history and blocked-run positive/negative fixtures.
- Legacy/malformed record fail-closed tests without prose parsing.
- External producer fingerprint/dedup integration smoke.
- Rollup text/JSON/CSV golden fixtures with unknown optional values.
- ChangeRail dogfood scan and contradiction triage fixture.
- Public-surface current/history scans and full release baseline.

## Related
- `openspec/board/1.backlog/060-00-repository-knowledge-maintenance-program-epic.md`
- `openspec/board/2.todo/060-04-add-maintain-skill-and-scheduler-adapters.md`
- `openspec/specs/changerail-delivery-observability/spec.md`
- `bin/changerail-delivery-metrics`

## Change 1: `connect-maintenance-feedback-adapters`

### Why
Review and blocked-run evidence already identifies harness weaknesses, but it
cannot enter maintenance backlog reliably without structured normalization.

### Goal
Add schema-backed review, blocked-run and external producer adapters using the
common finding lifecycle.

### Acceptance
- Adapters satisfy the structured-input and compatibility rules above.
- Existing schema ids remain unchanged.
- Duplicate findings/cards are prevented by common identity fingerprints.

### Depends On
- `060-03-add-maintenance-findings-lifecycle`

### Related
- `openspec/changes/connect-maintenance-feedback-adapters/`

## Change 2: `add-maintenance-quality-rollup-and-dogfood`

### Why
Maintainers need trend evidence before deciding whether broader automation or
fix mode is justified.

### Goal
Add stable quality rollup outputs and run the complete read-only pipeline over
ChangeRail's own knowledge catalog and regression fixtures.

### Acceptance
- Rollup and dogfood satisfy the metrics and fixture coverage above.
- Optional data remains `unknown` when not observed.
- Dogfood output remains ignored and public-safe.

### Depends On
- `connect-maintenance-feedback-adapters`
- `060-04-add-maintain-skill-and-scheduler-adapters`

### Related
- `openspec/changes/add-maintenance-quality-rollup-and-dogfood/`

## Result
Not started.

## Next
- Refresh after sufficient real audit/triage runs exist for metric semantics.

## Log
- `2026-08-09T12:35:25Z` — feedback/rollup story extracted from broad harness card.
