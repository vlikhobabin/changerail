# Добавить deterministic knowledge integrity gate

## Status
1.backlog

## Owner
ChangeRail core

## OpenSpec Stage
story

## Series
`060-repository-knowledge-maintenance`

## Series Index
`02`

## Planning State
blocked on `060-01`; detector semantics captured for refresh after contract delivery

## Source
- `060-00-repository-knowledge-maintenance-program-epic.md`
- `060-01-establish-repository-knowledge-contract.md`
- ArchUnit and other native architecture checker adapter patterns.

## Summary
Добавить read-only deterministic `scan` и configurable detectors для catalog
coverage, repository links, generated freshness, active-reference policy и
consumer-owned architecture/instruction checks.

## Acceptance
- `bin/changerail-maintenance scan` работает без LLM, не меняет repository и
  выводит schema-bound report либо fail-closed configuration diagnostic.
- Policy определяет include/exclude globs, enabled detectors, severity threshold,
  timeout и per-detector options; пустой inventory не превращается в silent pass.
- Catalog coverage проверяет явно настроенный documentation universe, а не все
  repository files по неявной эвристике.
- Orphan detector различает missing catalog target и discovered knowledge file,
  который не покрыт ни одной active catalog record.
- Local link/anchor detector использует maintained Markdown parser и
  документированный GitHub-compatible anchor algorithm; regex-only Markdown
  parsing не считается реализацией contract.
- Generated freshness проверяется passive source/output fingerprints или
  `render-index --check`; arbitrary generator command не запускается неявно.
- Forbidden active references проверяют только configured active knowledge
  scope и выдают actionable relative-path evidence.
- Architecture/instruction adapters запускаются как argv array без shell,
  получают repository cwd и timeout, возвращают schema-bound findings и не
  встраивают language-specific logic в ChangeRail core.
- Adapter failure, timeout, invalid JSON или path escape дает отдельную
  detector-error finding и не интерпретируется как green architecture result.
- Instruction-budget producer из карточки `050` подключается только после
  появления стабильного output contract; thresholds не дублируются в серии `060`.
- Scan exit behavior разделяет successful report generation и configured
  `--fail-on` threshold для CI gate.
- Focused fixtures доказывают link drift, stale index, orphan record, forbidden
  active reference, adapter timeout и invalid adapter output.

## Depends On
- `060-01-establish-repository-knowledge-contract`
- Instruction-budget integration optionally depends on the relevant delivered
  change from `050-harden-greenfield-consumer-bootstrap`.

## Change Set
- none yet

## Verify
- Detector unit fixtures with one regression source per finding.
- Integration scan over disposable repository fixtures.
- No-mutation snapshot before/after scan.
- Adapter argv, timeout, invalid-output and relative-path safety tests.
- Markdown links/anchors cases with duplicate headings and encoded fragments.
- Full release baseline, public-surface scan and OpenSpec validation.

## Related
- `openspec/board/1.backlog/060-00-repository-knowledge-maintenance-program-epic.md`
- `openspec/board/1.backlog/060-01-establish-repository-knowledge-contract.md`
- `openspec/board/1.backlog/050-harden-greenfield-consumer-bootstrap.md`
- `openspec/specs/changerail-drift-gate/spec.md`

## Change 1: `add-deterministic-knowledge-integrity-scan`

### Why
Repository knowledge needs a reproducible first-line gate before any ambiguous
finding is sent to an agent.

### Goal
Implement read-only catalog, coverage, orphan, link/anchor, generated freshness
and forbidden-reference detectors with stable diagnostics.

### Acceptance
- Core detectors satisfy the acceptance above without LLM or repository writes.
- CI threshold and report-generation outcomes are distinct.
- Each fixture demonstrably fails when its target regression is present.

### Depends On
- `060-01-establish-repository-knowledge-contract`

### Related
- `openspec/changes/add-deterministic-knowledge-integrity-scan/`

## Change 2: `add-maintenance-detector-adapter-protocol`

### Why
Architecture and instruction checks are language/project specific, but their
findings need one safe generic ingestion boundary.

### Goal
Define and implement the bounded native adapter execution and output protocol.

### Acceptance
- Adapter invocation is shell-free, timeout-bounded and repository-scoped.
- Invalid or failed adapters cannot produce a false green result.
- Example adapters remain generic and do not add ArchUnit or another language
  analyzer to core runtime dependencies.

### Depends On
- `add-deterministic-knowledge-integrity-scan`

### Related
- `openspec/changes/add-maintenance-detector-adapter-protocol/`

## Result
Not started.

## Next
- Refresh after `060-01` delivery, then run readiness review.

## Log
- `2026-08-09T12:35:25Z` — story extracted with deterministic/adapter boundary.
