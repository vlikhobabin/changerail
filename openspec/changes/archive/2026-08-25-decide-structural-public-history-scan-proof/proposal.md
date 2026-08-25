## Why

Две попытки построить bounded successor вокруг synthetic fixture-v2 показали,
что persistent cache, recipe/transcript authority, statistical thresholds и
descendant-RSS oracle создают больше недоказуемого состояния, чем сам scanner.
Нужен более простой published decision: correctness доказывается структурой
одного fresh real-Git запуска, а performance measurements остаются только
наблюдением.

## What Changes

- Supersede fixture-v2 только для future scanner delivery, сохранив published
  decisions, certification и stopped payload evidence как неизменную
  forensic-only lineage без implementation-evidence claim.
- Зафиксировать future scanner contract: fresh `git rev-list --all`, ровно один
  persistent `git cat-file --batch`, invocation-local memoization объектов и
  selected `(blob OID, exact path)`, strict fail-closed parsing и отсутствие
  cross-run cache.
- Заменить fixture/CV/RSS performance authority на structural real-Git proof:
  PATH-wrapped constant exact Git child count на small/enlarged histories,
  независимую actual `(commit,path,blob)` enumeration, малые legacy-parity и
  fault repositories, observational `/usr/bin/time -v`, один final history run
  и один full baseline на exact payload.
- Зафиксировать full-history CI checkout `fetch-depth: 0` и ordered lineage
  `authorize-bounded-structural-public-history-scan` ->
  `deliver-structurally-bounded-public-history-scan` с ceiling `301`, protocol
  allowance `false` и independent implementation limit `<=300` production LOC
  относительно `ccccb62562e1646b595119edd3326763860f14a7`.
- Ограничить этот change board/OpenSpec/spec documentation: production, test и
  runtime additions равны `0` LOC; successors, scans, baseline, archive, review,
  commit и push не создаются и не выполняются.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-release-ci`: заменить обязательную fixture-v2 benchmark authority
  для future successor на минимальный structural public-history proof contract
  и exact authorization/delivery lineage.

## Impact

Этот decision изменяет только source card и artifacts/spec delta в
`openspec/changes/decide-structural-public-history-scan-proof/`. После отдельной
публикации решения будущие authorization и implementation cards будут владеть
изменениями scanner, connected real-Git tests и release CI; текущие production,
tests, workflows, fixtures и runtime state не изменяются.
