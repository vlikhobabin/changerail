## Context

`scripts/public-surface-scan.py --history` сейчас получает `git rev-list --all`,
запускает `git ls-tree` для каждого commit и затем `git show` для каждого
подходящего commit/path. Поэтому стоимость определяется числом повторных
commit/path occurrences, а локальные refs делают release gate зависимым от
содержимого конкретного workspace. Retained evidence `canonical-history-timeout`
фиксирует timeout focused real-checkout scan после 30 секунд; public-safe
synthetic fixtures воспроизводят тот же ceiling.

Investigation должна выбрать будущую реализацию, но не менять scanner,
`scripts/run-release-baseline.py`, `.github/workflows/release-ci.yml` или smoke
tests. Исторические локальные implementation branches не являются source of
truth. Source of truth этого решения — proposal, delta spec и эта design.

### Observed public-safe profile

Instrumented synthetic fixtures с 21 public path подтвердили точную форму
fan-out текущего алгоритма:

| Reachable commits | Git processes | `ls-tree` | `show` | Result |
| ---: | ---: | ---: | ---: | --- |
| 5 | 111 | 5 | 105 | pass, 4.416 s |
| 10 | 221 | 10 | 210 | pass, 8.304 s |
| 20 | 441 | 20 | 420 | pass, 17.745 s |
| 50 | at least 799 | 37 | 761 | timeout 30 s |

Wrapper instrumentation добавляет постоянный overhead на каждый process,
поэтому wall time используется только как diagnostic, а counts показывают
детерминированный рост `1 + commits + commit/path occurrences`. Fixtures на
100 и 250 commits также достигли 30-секундного timeout до завершения. Это
согласуется с retained real-checkout evidence `canonical-history-timeout`.
Raw результаты сохранены только в ignored evidence с ids
`synthetic-current-growth-profile` и `synthetic-current-profile`.

## Goals / Non-Goals

**Goals:**

- сохранить полное сканирование каждого уникального public blob, достижимого
  из release commit, и commit/path attribution для findings;
- сделать число Git process launches константным относительно commits, paths и
  blobs;
- задать однозначный NUL/size-delimited framing и fail-closed lifecycle;
- дать successor один проверяемый benchmark и production LOC budget.

**Non-Goals:**

- реализация или оптимизация production scanner в этой change;
- изменение current-tree rules, redaction policy, report schema, release
  baseline inventory или CI command strings;
- покрытие всех локальных refs, unreachable objects или shallow history;
- импорт кода из локальных экспериментальных branches.

## Decisions

### 1. Release ref — один полностью доступный `HEAD` commit

Release-facing `--history` MUST один раз разрешить `HEAD^{commit}` и обходить
только commits, достижимые из полученного object id. Дополнительные local refs,
worktree refs, remote-tracking refs и unreachable objects не входят в release
surface. Missing/unborn `HEAD`, shallow repository или Git lifecycle failure
дают fail-closed structured history finding и non-zero result.

Это соответствует тому, что публикуется из конкретного checkout, и устраняет
machine-local вариативность `--all`. Альтернатива `--all` отклонена: она
проверяет не release artifact, а произвольное локальное состояние refs.

### 2. Enumeration — один NUL-framed history stream

Successor `implement-bounded-public-history-scan-runtime` MUST заменить nested
Git calls на три bounded subprocess lifecycle:

1. `git rev-parse` разрешает full release object id и shallow-state;
2. один `git log --full-history -m --raw -z --root --no-renames --no-abbrev
   --format=tformat:%x1e%H` stream перечисляет изменения выбранных roots во всех
   reachable commits;
3. один persistent `git cat-file --batch` stream возвращает содержимое каждого
   deduplicated non-zero regular/symlink blob object id.

Raw-log parser строит `blob oid -> [(full commit oid, path)]`, дедуплицирует blob
до content scan и после finding разворачивает его в существующие commit/path
records. `tformat:%x1e%H` исключает config/default commit prose и задаёт marker
`0x1e + full oid`; вместе с `-z` stream состоит из NUL fields. После marker
следуют пары `raw header + path`; ровно первый header commit имеет один leading
LF. State machine различает ожидание marker/header/path, поэтому path,
начинающийся с marker-like bytes, остаётся path. Root diffs покрывают initial
files, `--full-history` не упрощает path-limited ancestry, `-m` включает
merge-resolution blobs, `--no-renames` явно представляет новый path, а `-z`
сохраняет произвольные non-NUL path bytes. Submodules и non-blob tree entries не
читаются как public file contents.

Альтернатива `rev-list --objects` плюс path hints отклонена как единственный
source attribution: object enumeration дедуплицирует blobs, но не сохраняет
полную commit/path связь. Per-blob `git show` и per-commit `ls-tree` отклонены
из-за unbounded process fan-out.

### 3. Framing и lifecycle fail closed

Raw-log framing MUST начать каждый commit NUL field с `0x1e`, за которым идёт
full hex oid длины, определённой resolved release oid. Затем MUST следовать zero
или больше пар: raw header field (только первый может начинаться с ровно одного
LF) и один path field. Header MUST содержать ожидаемые modes, full old/new oids
и single-path status; unexpected marker/header/path state MUST прекратить scan.
`cat-file --batch` MUST вернуть запрошенный oid, type `blob`, неотрицательный
decimal size, ровно `size` payload bytes и завершающий LF.
Unexpected/truncated/missing/duplicate response, invalid field, premature EOF,
non-zero exit, timeout или pipe error MUST прекратить history scan.

Ошибка представляется в существующем `changerail.public-surface-scan.v1` как
history finding с generic redacted message; raw blob, command output и
token-like values в JSON/stdout не копируются. Binary detection, UTF-8 skip,
current-tree scan rules и finding redaction остаются прежними.

### 4. Bounded regression и benchmark oracle

Public-safe synthetic fixture MUST содержать минимум 250 reachable commits,
20 public paths, повторное использование одинаковых blobs, modification,
deletion, rename-as-delete/add, merge-resolution blob, binary и invalid UTF-8
content, finding под несколькими paths, excluded root и unrelated local ref.

Successor проходит только если:

- semantic oracle подтверждает parity current rules, unique-blob coverage,
  commit/path attribution, exclusion unrelated ref и fail-closed malformed
  raw-log/`cat-file`/process fixtures;
- history phase запускает не более трех Git processes независимо от fixture
  cardinality;
- focused synthetic history scan завершается не более чем за 30 секунд;
- полный `scripts/run-release-baseline.py` в clean release checkout завершается
  не более чем за 300 секунд;
- оба time ceiling проверяются внешним timeout и сохраняют concise evidence.

Wall-clock limits являются release admission ceilings, а process-count oracle
делает regression детерминированным при разной скорости машин.

### 5. Один ordinary successor без authorization

Exact successor: `implement-bounded-public-history-scan-runtime`. Он ограничен
`scripts/public-surface-scan.py`, focused scanner smoke/benchmark и необходимой
release-ci spec/card metadata. Production-counted additions MUST быть не более
300 LOC; новая authority, mutation/credential boundary или wire protocol
запрещены. Поэтому отдельная authorization card не нужна. Если implementation
не помещается в эту границу, successor обязан остановиться для нового split или
investigation, а не расширять payload.

## Risks / Trade-offs

- **[Git raw framing сложно разобрать корректно]** → malformed/truncated fixture
  matrix и строгая state machine, которая fail closed до выдачи pass.
- **[Один blob может встречаться во многих paths]** → content сканируется один
  раз, но findings разворачиваются по всем introduction commit/path records.
- **[Shallow CI checkout не доказывает reachable history]** → явный fail-closed
  result; release checkout обязан предоставлять полную ancestry.
- **[300-секундный baseline ceiling включает другие checks]** → focused
  30-секундный oracle локализует scanner regression, полный ceiling защищает
  release usability.

## Migration Plan

1. Опубликовать эту decision-only change и successor card.
2. Successor реализует bounded streams и focused tests в пределах 300 LOC.
3. Прогнать semantic/process-count/30-second fixture и clean-checkout
   300-second release baseline.
4. На regression вернуть только successor commit; текущий scanner contract до
   его publish не меняется.

## Open Questions

Нет. Любое расширение release-ref semantics, report schema или production LOC
budget требует отдельного решения.
