# Добавить deterministic knowledge integrity gate

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
`060-repository-knowledge-maintenance`

## Series Index
`02`

## Planning State
deliver-ready against the published `060-01` catalog, policy and CLI contract;
OpenSpec artifacts are delegated to the internal `ff` phase of `$chrl-deliver`

## Source
- `060-00-repository-knowledge-maintenance-program-epic.md`
- `openspec/board/4.done/060-01-establish-repository-knowledge-contract.md`
- ArchUnit and other native architecture checker adapter patterns.

## Summary
Добавить read-only deterministic `scan` и configurable detectors для catalog
coverage, repository links, generated freshness, active-reference policy и
consumer-owned architecture/instruction checks.

## Acceptance
- `bin/changerail-maintenance scan` работает без LLM, не меняет repository и
  выводит schema-bound report либо fail-closed configuration diagnostic.
- Public schemas используют ids `changerail.maintenance-scan-report.v1` и
  `changerail.maintenance-detector-result.v1`; report отделяет raw findings,
  detector errors и configuration diagnostics.
- Существующий `changerail.maintenance-policy.v1` расширяется только optional
  scan/adapters полями; минимальный policy, опубликованный в `060-01`, остается
  валидным и сохраняет `additionalProperties: false` на contract-owned objects.
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
- Exit `0` означает созданный complete report ниже threshold, exit `1` —
  созданный report, достигший `--fail-on`, exit `2` — invalid configuration
  или невозможность создать schema-valid report; JSON stdout остается одним
  machine-readable document во всех режимах.
- Focused fixtures доказывают link drift, stale index, orphan record, forbidden
  active reference, adapter timeout и invalid adapter output.

## Depends On
- `060-01-establish-repository-knowledge-contract`
- Instruction-budget integration optionally depends on the relevant delivered
  change from `050-harden-greenfield-consumer-bootstrap`.

## Delivered Dependency Contract
- Loader и safe-path semantics: `scripts/changerail_repository_knowledge.py`.
- CLI extension point: `scripts/changerail_maintenance.py` и wrappers
  `bin/changerail-maintenance{,.cmd}`.
- Published policy currently requires only `schema`, `catalog_path` and
  `generated_index_path`; scan configuration must be an additive opt-in.
- Published catalog records and deterministic index behavior are specified in
  `openspec/specs/changerail-repository-knowledge/spec.md`.
- Instruction-budget adapter не входит в эту delivery: card `050` еще не
  опубликовала stable producer output contract. Generic adapter protocol must
  allow it to be connected later without schema changes.

## Change Set
- `add-deterministic-knowledge-integrity-scan`
- `add-maintenance-detector-adapter-protocol`

## Verify
- Fast-forward artifact validation:
  `./bin/openspec validate add-deterministic-knowledge-integrity-scan --strict`
  passed.
- Fast-forward artifact validation:
  `./bin/openspec validate add-maintenance-detector-adapter-protocol --strict`
  passed.
- Fast-forward aggregate validation: `./bin/openspec validate --all --strict`
  passed.
- Fast-forward whitespace validation: `git diff --check` and trailing-whitespace
  scan over new change artifacts passed.
- Delivery verification still required:
  detector unit fixtures with one regression source per finding; integration
  scan over disposable repository fixtures; no-mutation snapshot before/after
  scan; adapter argv, timeout, invalid-output and relative-path safety tests;
  Markdown links/anchors cases with duplicate headings and encoded fragments;
  full release baseline, public-surface scan and OpenSpec validation.
- `python3 -m py_compile scripts/changerail_repository_knowledge.py
  scripts/changerail_maintenance.py scripts/smoke-repository-knowledge.py
  scripts/smoke-contract-schemas.py` - pass.
- `python3 scripts/smoke-repository-knowledge.py` - pass; focused fixtures cover
  link drift, stale index, orphan/missing catalog target, forbidden active
  reference, adapter timeout, adapter invalid JSON, schema-invalid adapter
  output, adapter non-zero exit and unsafe adapter paths with no-mutation
  snapshots.
- `python3 scripts/smoke-contract-schemas.py` - pass with 11 schemas, including
  `changerail.maintenance-scan-report.v1` and
  `changerail.maintenance-detector-result.v1`.
- `bin/changerail-maintenance validate-catalog` - pass.
- `bin/changerail-maintenance render-index --check` - pass.
- `bin/changerail-maintenance scan --json` - pass; complete report with zero
  detectors for the minimal dogfood policy.
- `bin/changerail-maintenance --workspace fixtures/repository-knowledge/adapters
  scan --catalog knowledge.yaml --policy maintenance.yaml --json` - expected
  exit `1`; complete report reached threshold through adapter fixture findings
  and detector errors.
- `./bin/openspec validate add-deterministic-knowledge-integrity-scan --strict`
  - pass before archive.
- `./bin/openspec validate add-maintenance-detector-adapter-protocol --strict`
  - pass before archive.
- `./bin/openspec validate changerail-repository-knowledge --strict` - pass
  after spec sync.
- `./bin/openspec validate changerail-contracts --strict` - pass after spec
  sync.
- `./bin/openspec validate --all --strict` - pass after archive with 23/23
  items.
- `python3 scripts/public-surface-scan.py` - pass with 808 files scanned and 0
  findings.
- `git diff --check` - pass.
- `python3 scripts/run-release-baseline.py` - pass.
- Independent review cycle 1 returned `no-go` for schema-invalid adapter output
  being rewritten into a passing detector result; same-card rescue fixed raw
  adapter output validation and added the missing-fields regression fixture.
- `python3 -m py_compile scripts/changerail_repository_knowledge.py
  scripts/smoke-repository-knowledge.py` - pass after same-card rescue.
- `python3 scripts/smoke-repository-knowledge.py` - pass after same-card rescue.
- `python3 scripts/smoke-contract-schemas.py` - pass after same-card rescue.
- `ADAPTER_SCHEMA_INVALID_OUTPUT_FIX_OK` assertion - pass; fixture scan reports
  `invalid_adapter_output` for missing required adapter detector-result fields.
- `python3 scripts/run-release-baseline.py` - pass after same-card rescue with
  30/30 steps.

## Archive
- `openspec/changes/archive/2026-08-09-add-deterministic-knowledge-integrity-scan/`
- `openspec/changes/archive/2026-08-09-add-maintenance-detector-adapter-protocol/`

## Related
- `openspec/board/1.backlog/060-00-repository-knowledge-maintenance-program-epic.md`
- `openspec/board/4.done/060-01-establish-repository-knowledge-contract.md`
- `openspec/board/1.backlog/050-harden-greenfield-consumer-bootstrap.md`
- `openspec/specs/changerail-repository-knowledge/spec.md`
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
- `openspec/changes/archive/2026-08-09-add-deterministic-knowledge-integrity-scan/`

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
- `openspec/changes/archive/2026-08-09-add-maintenance-detector-adapter-protocol/`

## Result
Implemented, verified, synced and archived; awaiting independent review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- `2026-08-09T12:35:25Z` — story extracted with deterministic/adapter boundary.
- `2026-08-09T14:04:07Z` — refreshed against delivered `060-01`; fixed report
  schema ids, additive policy and exit contracts, deferred `050` integration,
  and moved the card to `2.todo`.
- `2026-08-09T14:11:01Z` — fast-forward artifacts created for
  `add-deterministic-knowledge-integrity-scan` and
  `add-maintenance-detector-adapter-protocol`; strict OpenSpec validation
  passed and card moved to `3.inprogress`.
- `2026-08-09T14:27:43Z` — implemented maintenance scan and adapter protocol;
  synced specs, archived both changes and prepared review handoff.
- `2026-08-09T14:52:54Z` — independent review cycle 1 returned `no-go` for
  schema-invalid adapter output normalization; fixed raw adapter result
  validation and added a missing-fields adapter fixture.
- `2026-08-09T15:06:26Z` — post-fix release baseline passed with 30/30 steps;
  ready for fresh re-review.
- 2026-08-09T15:22:20Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
