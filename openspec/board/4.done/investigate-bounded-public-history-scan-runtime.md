# Исследовать bounded runtime public history scan

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
- Focused real-checkout history scan и public-safe synthetic fixtures достигли
  timeout 30 секунд. Evidence сохранено под ignored
  `.runtime/changerail/evidence/decide-bounded-public-history-scan-runtime/`.

## Summary
Выбрать bounded history scanner, который сохраняет полное fail-closed покрытие
release-reachable commits, но не запускает отдельные Git-процессы для каждого
повторяющегося blob во всех локальных refs.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

Карточка decision-only: production scanner, release baseline и smoke tests не
изменяются. Старые локальные implementation/authorization payloads не являются
source или authority для этого investigation.

## Depends On
- none

## Blocks
- `stabilize-first-stable-release-scope`
- `prepare-1-0-0-stable-release`

## Acceptance
- Scanner проверяет каждый уникальный public blob, достижимый из выбранного
  release ref, и сохраняет commit/path attribution для findings.
- Выбраны exact ref semantics, batching/caching algorithm, malformed Git
  framing lifecycle и измеримый ceiling для focused history scan и полного
  release baseline.
- Current/history self-tests, secret redaction и release CI остаются fail
  closed; malformed Git framing и lifecycle failures имеют structured result.
- Названы один exact implementation successor, bounded production LOC ceiling,
  regression/benchmark matrix и необходимость отдельной authorization card,
  если решение превышает обычный complexity boundary.

## Investigation Decision
Release history surface — commits, достижимые только из один раз разрешённого
полного `HEAD^{commit}`. Unrelated local/worktree/remote refs не являются
частью конкретного release artifact; missing/unborn `HEAD`, shallow ancestry и
любой Git framing/lifecycle failure дают redacted structured finding и non-zero
result.

Successor `implement-bounded-public-history-scan-runtime` заменяет nested
per-commit/per-path processes на максимум три Git process launches:

1. resolve release commit и shallow state;
2. один `git log --full-history -m --raw -z --root --no-renames --no-abbrev
   --format=tformat:%x1e%H` stream строит unique blob и commit/path attribution;
3. один persistent `git cat-file --batch` stream читает каждый unique public
   blob ровно один раз.

`-z` framing разбирается как NUL fields: commit marker `0x1e + full oid`, затем
ноль или больше пар `raw header + path`; только первый header commit может
иметь ровно один leading LF. Parser знает, ожидает ли marker, header или path,
поэтому marker-like path не меняет state. Raw-log и size-delimited batch framing
валидируются полностью; unexpected oid, mode/type/size, field/state, truncation,
premature EOF, non-zero exit, timeout или pipe error fail closed в существующем
`changerail.public-surface-scan.v1` без копирования raw blob/command output.
Existing current rules, binary/invalid UTF-8 handling, report shape и secret
redaction не расширяются.

## Profile And Ceilings
Public-safe synthetic profile с 21 public path дал:

- 5 commits: 111 Git processes, 4.416 s;
- 10 commits: 221 Git processes, 8.304 s;
- 20 commits: 441 Git processes, 17.745 s;
- 50 commits: timeout 30 s после как минимум 799 Git processes.

Wrapper добавляет overhead на process launch, поэтому durations диагностические,
а counts доказывают точный рост `1 + commits + commit/path occurrences`.
Fixtures на 100/250 commits и real-checkout evidence
`canonical-history-timeout` также достигли 30-секундного ceiling.

Successor regression floor: public-safe fixture минимум 250 commits/20 paths,
reused blobs, deletion, rename, merge resolution, binary/invalid UTF-8,
multi-path finding, excluded root, unrelated ref и malformed framing/lifecycle.
Focused ceiling — 30 секунд и максимум три Git processes; полный clean-checkout
release baseline ceiling — 300 секунд.

## Successor Decision
- Exact successor: `implement-bounded-public-history-scan-runtime`.
- Production-counted additions ceiling: 300 LOC.
- New authority or wire protocol: forbidden.
- Separate authorization card: not required.
- Если payload превышает ceiling или расширяет authority/schema/ref CLI, нужен
  новый split/investigation; эта decision не является waiver.

## Change Set
- `decide-bounded-public-history-scan-runtime`

## Verify
- GREEN: `bin/openspec validate decide-bounded-public-history-scan-runtime --strict`
  — evidence `openspec-change-strict`.
- GREEN: `bin/openspec validate changerail-release-ci --strict` — evidence
  `openspec-release-ci-strict`.
- GREEN: `bin/openspec validate --all --strict` — 24 items before archive,
  evidence `openspec-all-strict`.
- GREEN: post-archive `bin/openspec validate --all --strict` — 23 canonical
  specs, evidence `post-archive-openspec-all`.
- GREEN: `python3 scripts/public-surface-scan.py` — zero findings, evidence
  `public-surface-current` before archive and
  `post-archive-public-surface-current` after board handoff.
- GREEN: `git diff --check` — evidence `scoped-whitespace-check`.
- GREEN: post-archive `git diff --check` — evidence
  `post-archive-whitespace`.
- GREEN after cycle-1 rescue: `bin/openspec validate changerail-release-ci
  --strict`, `bin/openspec validate --all --strict`, current public scan and
  `git diff --check` — evidence `rescue-openspec-release-ci-strict`,
  `rescue-openspec-all-strict`, `rescue-public-surface-current` and
  `rescue-whitespace-check`.
- GREEN: scanner/baseline/CI workflow/smoke diff against `origin/main` is empty
  — evidence `production-surfaces-unchanged` and
  `rescue-production-surfaces-unchanged`.
- DIAGNOSTIC: current growth profile — 111/221/441 Git processes for
  5/10/20-commit fixtures; evidence `synthetic-current-growth-profile`.
- DIAGNOSTIC: 50/100/250-commit fixtures reached 30-second timeout; evidence
  `synthetic-current-profile`; real checkout timeout evidence
  `canonical-history-timeout`.
- RED test: not applicable — investigation changes decision/spec/card artifacts
  only and intentionally leaves production scanner/tests unchanged.

## Archive
- `openspec/changes/archive/2026-08-31-decide-bounded-public-history-scan-runtime/`

## Related
- `scripts/public-surface-scan.py`
- `scripts/run-release-baseline.py`
- `openspec/board/2.todo/implement-bounded-public-history-scan-runtime.md`

## Result
Decision-only investigation completed: exact `HEAD` semantics, three-process
unique-blob design, framing lifecycle, benchmark ceilings and ordinary 300 LOC
successor boundary are fixed; reciprocal successor card is ready.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-bounded-public-history-scan-runtime`

### Why
Текущий scanner запускает отдельные `ls-tree`/`show` процессы для каждого
commit/path и не дает bounded release gate даже в изолированном clone.

### Goal
Опубликовать одно decision-only решение для полного release-reachable history
coverage с bounded runtime и exact implementation handoff.

### Scope
- Профилировать текущий процесс на public-safe synthetic fixture.
- Сравнить unique-blob batching/caching и exact release-ref selection.
- Зафиксировать framing, redaction, attribution, timeout и benchmark oracle.
- Не изменять production scanner, baseline или smoke в investigation change.

### Acceptance
- Решение не ослабляет reachable-history coverage и задает один проверяемый
  successor с bounded regression floor.

### Depends On
- none

### Related
- `openspec/changes/decide-bounded-public-history-scan-runtime/`

## Log
- 2026-08-31T00:00:00Z создано из повторного bounded timeout evidence;
  historical local implementations не интегрированы и не используются как
  authority.
- 2026-08-31T07:00:00Z public-safe profile подтвердил линейный
  per-commit/per-path process fan-out и 30-секундный timeout; выбран bounded
  three-process design для exact successor без authorization.
- 2026-08-31T07:30:00Z delta requirement синхронизирован в
  `changerail-release-ci`, strict/current-public/whitespace gates прошли;
  production scanner, baseline, CI и smoke остались неизменными.
- 2026-08-31T08:58:54Z independent review cycle 1 дал `NO-GO`: decision не
  задавала config-independent commit marker, называла неверный existing schema
  id и ссылалась на неподтверждённые baseline observations.
- 2026-08-31T09:10:00Z scoped rescue зафиксировал exact
  `--format=tformat:%x1e%H` NUL-field grammar, actual unchanged
  `changerail.public-surface-scan.v1` и сузил motivation до retained
  30-second real/synthetic evidence; production scope не расширен.
- 2026-08-31T09:33:31Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
