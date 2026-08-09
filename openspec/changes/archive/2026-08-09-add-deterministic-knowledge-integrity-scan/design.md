## Context

Серия `060` уже опубликовала catalog/policy loader и deterministic generated
index. Текущий maintenance helper умеет validate/render, но еще не дает единого
read-only gate-а, который CI или maintainer может запускать для drift
диагностики. Policy schema минимальна: `schema`, `catalog_path` и
`generated_index_path`; новая scan-конфигурация должна быть additive, чтобы
опубликованный минимальный policy оставался valid.

## Goals / Non-Goals

**Goals:**
- Добавить `scan` subcommand, который возвращает один schema-bound JSON report
  и не меняет repository.
- Разделить raw detector findings, detector execution errors и configuration
  diagnostics.
- Сделать policy opt-in: include/exclude universe, enabled detectors,
  `fail_on` severity threshold, timeout и detector-specific options.
- Реализовать deterministic core detectors для coverage/orphan, Markdown
  links/anchors, generated freshness и forbidden active references.
- Дать focused fixtures, которые ломаются при каждом заявленном drift class.

**Non-Goals:**
- Не подключать LLM triage, scheduler или mutation/fix mode.
- Не запускать arbitrary generator commands. Generated freshness проверяется
  passive fingerprint/index check behavior only.
- Не подключать instruction-budget producer из серии `050` до stable output
  contract.
- Не добавлять language-specific architecture analyzers; это отдельный adapter
  protocol change.

## Decisions

- **One report, three diagnostic classes.** `scan` пишет ровно один JSON
  document в stdout. `detectors[].findings` описывает domain findings,
  `detectors[].errors` описывает detector failure/configuration failure внутри
  enabled detector-а, а top-level `configuration_diagnostics` описывает invalid
  policy или невозможность собрать schema-valid report.
- **Exit behavior follows gate semantics.** Exit `0` означает schema-valid
  complete report ниже threshold. Exit `1` означает complete report с finding
  severity at or above configured `--fail-on`/policy threshold. Exit `2`
  означает invalid configuration или невозможность создать schema-valid report.
- **Policy stays additive.** Existing required fields do not change. Optional
  `scan` and later `adapters` objects are contract-owned and keep
  `additionalProperties: false`.
- **Configured universe over repository heuristics.** Coverage scans only
  explicit include/exclude globs from policy; an empty discovered universe is a
  finding/error instead of silent pass.
- **Markdown parser plus documented anchors.** Link detector uses a maintained
  Markdown parsing path for link extraction and a documented GitHub-compatible
  heading anchor algorithm with duplicate heading suffixes.
- **Generated freshness is passive.** The detector compares configured
  generated outputs against maintained source fingerprints or delegates to
  existing `render-index --check`. It does not execute configured generator
  commands.
- **No-mutation verification is a first-class fixture.** Scan tests snapshot a
  disposable repository before/after execution and assert tracked/untracked
  content is unchanged except ignored runtime fixtures created by the test
  harness itself.

## Risks / Trade-offs

- **Glob semantics surprise consumers** -> Policy docs and fixtures use
  repository-relative examples and fail closed on absolute/traversal paths.
- **Markdown parser dependency drift** -> Reuse runtime dependencies already
  available to ChangeRail where possible and isolate link extraction behind a
  small helper covered by duplicate-heading and encoded-fragment cases.
- **Large repositories make scans slow** -> Policy timeout applies to detector
  execution and fixtures cover timeout/error reporting instead of unbounded
  scans.
