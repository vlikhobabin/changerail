## 1. Fixture Authority Decision

- [x] 1.1 Подтвердить, что `history-fixture-v1` остается historical-only и не
  может дать будущий GREEN без materializable tracked preimage.
- [x] 1.2 Синхронизировать release-CI contract с exact v2 recipe schema/data,
  sanitized deterministic Git materializer, two-root canonical transcript и
  independent `ccccb625` legacy oracle.
- [x] 1.3 Подтвердить detached separate digests для recipe schema, recipe,
  materializer, realization transcript, benchmark harness и self-tests без
  self-reference и с более поздним external authority anchor.
- [x] 1.4 Подтвердить, что decision payload ограничен board/OpenSpec/spec
  relationship documentation и имеет ровно `0` production/test/runtime LOC.

## 2. Benchmark And Successor Contract

- [x] 2.1 Сохранить exact `48/1152/96/72`, semantic-case set, legacy/cold/warm
  order, two discarded warmups, five measured trials, unrounded medians,
  population CV rule и cold `<=0.20`/warm `<=0.05` thresholds.
- [x] 2.2 Сохранить child VmHWM `<=256 MiB`, 100 ms aggregate RSS `<=384 MiB`
  для sequential history job и fail-closed missing-sample behavior.
- [x] 2.3 Проверить connected no-gaming self-test matrix для authority tamper,
  root leakage, oracle substitution, semantic/order drift, timing/CV/threshold,
  RSS и favorable sample/set selection.
- [x] 2.4 Зафиксировать exact publish order
  `materialize-public-history-benchmark-fixture-v2` ->
  `authorize-bounded-public-history-scan-replacement-v2` ->
  `deliver-path-sensitive-public-history-scan-replacement-v2`, не создавая эти
  cards в текущем change.
- [x] 2.5 Зафиксировать exact six-field authorization с ceiling `301` и protocol
  allowance `false`, exact two-field candidate reference, preflight reciprocal
  tracked-`4.done` validation и отдельный implementation limit `<=300` LOC
  относительно `ccccb625`.

## 3. Decision Verification

- [x] 3.1 Выполнить `bin/openspec validate
  decide-materialized-public-history-benchmark-v2 --strict` и
  `bin/openspec validate --all --strict`.
- [x] 3.2 Выполнить `python3 -m json.tool .mcp.json`, parse
  `.codex/config.toml` через `tomllib` и current-only
  `python3 scripts/public-surface-scan.py` без `--history`.
- [x] 3.3 Выполнить
  `bin/changerail-source-classification --workspace . --json check`, подтвердить
  scoped `0` production/test/runtime LOC и отсутствие fixture/successor paths.
- [x] 3.4 Покрыть tracked и каждый untracked file через `git diff --check` и
  explicit no-index whitespace checks; проверить final scoped status/diff.
- [x] 3.5 Derive и scope-check delivery manifest и выполнить normalized
  deterministic preflight на exact decision fingerprint перед independent
  review, не запуская history scan, benchmark или full release baseline.
