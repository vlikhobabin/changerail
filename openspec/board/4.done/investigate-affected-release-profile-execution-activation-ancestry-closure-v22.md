# Исследовать execution binding, activation topology и ancestry closure affected profile v22

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 58

## Source
- Последняя safe published authorization boundary:
  `authorize-bounded-affected-release-profile-v21`, exact commit
  `f04b99d99555585703538eb9722be4c8e64cf6a6`.
- Terminal unpublished implementation v21 получила fresh ordinary/high
  `NO-GO`, acceptance `5/11`, findings `5/0/0`. Same-card repair не
  расходуется: фактическое execution binding и row-level activation proof
  требуют нового transport/proof design, а один prohibited fallback episode
  необратим внутри текущей попытки.
- Только validated counters и пять finding-class summaries переходят в эту
  investigation. V21 implementation card/OpenSpec/source/tests/CI/main-spec
  mutation, manifest, verdicts, logs и raw evidence являются forensic-only и
  далее не читаются, не копируются, не cherry-pick-ятся и не используются как
  proof.

## Summary
Опубликовать clean docs-only decision для v22, который связывает admitted
  environment и executable identity с atomic descriptor-bound broker exec, заменяет
placeholder activation inventory полным row-level context worklist и exact
static/catalog/dynamic topology equality, проверяет всю runtime ancestry и
требует новый clean execution episode без prohibited fallback diagnostics.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Independent review: one fresh `gpt-5.6-sol`/`high`
- Same-card repair budget limit/used/remaining: `1/1/0`, exhausted `true`

## Depends On
- `authorize-bounded-affected-release-profile-v21`
- `investigate-affected-release-profile-composite-command-dynamic-closure-v21`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`

## Blocks
- `authorize-bounded-affected-release-profile-v22`
- `implement-bounded-affected-release-profile-v22`
- `certify-accelerated-release-loop-v1`

## Authorization
- Future v22 implementation authorization:
  `{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-execution-activation-ancestry-closure-v22.md","investigation_id":"investigate-affected-release-profile-execution-activation-ancestry-closure-v22","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v22.md","successor_id":"implement-bounded-affected-release-profile-v22","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}`

## Acceptance
- Decision создаётся docs-only от exact published authorization v21 SHA;
  local/upstream/remote investigation branch и remote authorization branch до
  mutation указывают на этот SHA. Terminal v21 payload/evidence не
  импортируется, а chronology сохраняет review `5/11`, findings `5/0/0`,
  нерасходованный repair и пять bounded finding-class summaries.
- Published scheduler v1 `run_plan` и broker v5 `supervise` остаются
  backward-compatible. V22 явно авторизует только additive typed admitted-
  execution transport: one-to-one physical-owner row содержит direct member
  либо outer executor плюс exact ordered admission каждого composite inner
  argv. Worker открывает executable/operand FDs, запечатывает nested table в
  bounded `memfd`, а broker запускает exact FD через FD-capable `os.execve` с
  closed environment. Missing/extra/cross-owner/stale member, ambient fallback,
  legacy Popen, raw-token execution или identity drift fail closed до target
  start.
- Каждый direct/outer/inner record связывает owner/member, exact logical argv,
  deterministic physical argv/FD map, полную `(device,inode,type,mount)` chain,
  closed environment и digest. Script/launcher нормализуется в pinned native
  interpreter FD и pinned operand FDs без kernel shebang/PATH re-resolution.
  Composite owner сохраняет ровно один scheduler result; group executor
  валидирует sealed bundle/registry/digests и использует унаследованные member
  FDs, не ambient reconstruction. Existing scheduler/broker entrypoints and
  result schema не получают authority.
- Independent execution oracle строит все direct/outer/inner logical и physical
  rows отдельно из immutable v18 inventory, pinned CI и fixture filesystem,
  наблюдает `os.exec`/FD-exec inputs, FD identities, sealed bundle и post-exec
  `/proc` identity и сравнивает их bidirectionally. Legacy Popen для admitted
  work, fake-first PATH, ambient-only target, changed environment/member/bundle,
  pre-open swap и каждый malformed neighbor отвергаются до start; post-open
  rename не может изменить исполняемый объект.
- Static observer независимо парсит exact runner/profile/group executor,
  additive transport и exact-digest legacy scheduler/broker, материализует
  полный multiset imports/bindings/functions/predicates/calls/raw sinks и
  запускает finite context-sensitive worklist только от public
  `run_profile("affected", base=<known-docs-base>, jobs=1,
  environment=<production-shaped>)`. Каждая row получает source/digest, owner,
  canonical AST path/span, normalized context/predicates, finite callee/
  receiver set, predecessor/transfer, reachability/reason и sink class.
- Separately authored immutable `ACTIVATION_CATALOG` содержит полный exact
  annotated row multiset без placeholder/default annotations. Observer,
  catalog и worklist compare bidirectionally по каждому полю; every reachable
  row имеет predecessor chain до public seed, every unreachable row имеет
  evaluated false/unsupported reason, а unknown/ambiguous binding, extra/
  missing row, sentinel annotation, runtime rebind, alternate wrapper/sink или
  latent transition fail closed.
- Pre-import clean child сохраняет полный bounded raw event stream и complete
  registered process topology. Каждый raw production occurrence обязан
  однозначно map-иться на catalog row; canonical activation key
  `(role,row,context,predicate facts,callee/receiver)` collapse-ит только
  повторные итерации того же exact timing loop. Static reachable projection,
  catalog reachable projection и normalized dynamic topology равны
  bidirectionally; conflicting duplicate, unmapped raw occurrence, missing/
  extra key или disconnected public→scheduler→broker/group path fail closed.
- Test-only `sitecustomize`, nonce-bound bounded collector, import guard,
  opcode/profile/audit hooks и at-fork registration устанавливаются до
  production import в public child, scheduler spawn и group-executor exec.
  Registration/topology/event schemas закрыты; loss, overflow, timeout,
  sequence/replay, bad nonce, unknown role, disconnected parentage, digest
  mismatch и bootstrap removal/delay fail proof. Test transport не является
  production reachability, pass, authority или unreachable proof.
- Runtime root допускается только как empty direct child exact admitted runtime
  anchor. Phase A открывает anchor и каждый candidate component через
  directory-FD walk с `O_NOFOLLOW`, сравнивает lexical/real spelling и
  `(device,inode,type)` prefix, запрещает repeated identities, symlink, alias,
  mount/outside-anchor transition, dangling/non-directory/entry neighbor и
  повторяет identity check непосредственно до scheduler reservation. Любая
  ошибка даёт `semantic_started:0` и zero later process/Git/scheduler/write/
  mutation events.
- Replacement implementation создаёт новый original RED и использует только
  disposable real-Git focused fixtures. Workspace diagnostics не вызывают
  public affected/full fallback; harness имеет exact harmless command allowlist
  и retained process/event evidence. Reachable history, real full/affected
  execution or benchmark, live matrix и certification остаются запрещены до
  certification.
- Future authorization зависит ровно от этой investigation, integration
  decision, scheduler v1 и authorization v21 и блокирует только implementation
  v22. Future implementation зависит ровно от тех же predecessors плюс
  authorization v22, блокирует только certification, начинается от
  authorization-publishing HEAD, использует единственную exact two-field
  authorization reference, создаёт genuine fingerprint-first RED и добавляет
  максимум `499` production LOC.
- Investigation сохраняет published v18 proof inventory как единственный
  immutable anchor, exact `35/30/48`, semantic digest
  `7147ee3c4b067486162f3dc1fee218c87eb40cbdb0d7730a9a78442da7986513`,
  full digest
  `6587ad0b9887e79f731cdf1ef25f7ff139140747ac9f4def3aeda762c1c4ae72`,
  total 35→30 ownership, `36 - 4 - (3 - 1) = 30`, Unicode `23/235`, strict
  four-stream selection, full-only authority, affected/protocol non-authority
  и exact source-safe four-step CI.
- Investigation меняет только эту card, same-slug OpenSpec, synchronized main
  release-CI spec и archive metadata; production/test/runtime LOC `0`, future
  authorization/implementation/certification отсутствуют, а reachable history,
  real full/affected execution or benchmark, live matrix и certification
  checks не запускаются.

## Change Set
- `investigate-affected-release-profile-execution-activation-ancestry-closure-v22`

## Verify
- Required: exact safe base/remotes and forensic boundary; published execution
  gap proof; additive admitted transport; immutable execution identity;
  row-level worklist/catalog; raw-event mapping and exact normalized topology;
  full ancestry walk; clean replacement episode; exact future lineage/ceiling;
  successor absence; strict OpenSpec; JSON/TOML; source classification;
  current-only public scan; exact sync; whitespace and manifest scope.
- RED: not applicable; docs-only investigation.
- Prohibited: terminal v21 payload/evidence access after handoff, history, real
  full/affected execution or benchmark, live matrix and certification checks.
- Observed: exact local/upstream/remote authorization base and clean successor
  absence passed; published source proves legacy broker Popen receives raw argv
  and ambient environment; six v22 requirements synchronized byte-exactly;
  strict OpenSpec before archive `24/24`, JSON/TOML, source classification,
  zero executable LOC, whitespace and current-only public scan `1716/0`
  passed. Prohibited checks were not run.
- Commands/outcomes: `bin/openspec validate --all --strict` passed `23/23`
  after archive; `python3 -m json.tool .mcp.json` and the required `tomllib`
  parse passed; `bin/changerail-source-classification --workspace . --json
  check` returned zero blockers; `python3 scripts/public-surface-scan.py`
  passed `1716/0`; per-heading `awk`/`diff` returned `EXACT_SYNC_OK 6`;
  `git diff --numstat -- scripts bin .github schemas profiles
  requirements-dev.txt pyproject.toml` returned empty; explicit successor
  `test ! -e` checks and `git diff --check` passed.

## Archive
- `openspec/changes/archive/2026-08-30-investigate-affected-release-profile-execution-activation-ancestry-closure-v22/`

## Related
- `openspec/changes/investigate-affected-release-profile-execution-activation-ancestry-closure-v22/`
- `openspec/board/4.done/authorize-bounded-affected-release-profile-v21.md`
- `openspec/board/4.done/investigate-affected-release-profile-composite-command-dynamic-closure-v21.md`
- `openspec/changes/archive/2026-08-29-authorize-bounded-affected-release-profile-v18/proof-inventory.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
DO complete: docs-only v22 execution-binding/activation-topology/ancestry
decision synchronized byte-exactly with zero production/test/runtime LOC;
ready for deterministic preflight and fresh ordinary/high review.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `investigate-affected-release-profile-execution-activation-ancestry-closure-v22`

### Why
Terminal v21 выявила пять proof/execution classes, которые нельзя исправить
same-card repair: admitted state не достигает реального process boundary,
activation catalog/worklist/topology не row-complete, runtime ancestry допускает
alias, а текущий execution episode уже нарушил запрет fallback diagnostics.

### Goal
Опубликовать feasible independent execution, activation и ancestry architecture
до любой v22 authorization или executable successor.

### Scope
- this card;
- same-slug docs-only OpenSpec artifacts;
- synchronized release-CI decision contract and archive metadata.

### Acceptance
- Каждый acceptance criterion карточки проверяем из published sources,
  independently authored future proof contracts и exact clean lineage без
  terminal payload или prohibited execution.

### Depends On
- `authorize-bounded-affected-release-profile-v21`
- `investigate-affected-release-profile-composite-command-dynamic-closure-v21`
- `decide-accelerated-release-loop-integration-boundary`
- `implement-bounded-release-semantic-scheduler-v1`

### Related
- `openspec/changes/investigate-affected-release-profile-execution-activation-ancestry-closure-v22/`

## Log
- 2026-08-30 card created in a clean worktree and remote branch from exact
  published authorization v21 SHA; only validated terminal counters and five
  finding-class summaries crossed the forensic boundary.
- 2026-08-30 FF prepared one docs-only investigation change with additive
  admitted execution binding, full row-level activation topology, anchored
  runtime ancestry and a clean replacement episode.
- 2026-08-30 DO synchronized six v22 requirements byte-exactly and passed
  strict OpenSpec `24/24`, JSON/TOML, source classification, zero executable
  LOC, successor absence, current-only public scan `1716/0` and whitespace;
  prohibited checks were not run.
- 2026-08-30 fresh review cycle 1 returned `NO-GO`, acceptance `9/12`, one
  docs blocker: singular composite admission omitted inner executable/
  environment rows and reopen-then-path-Popen retained a TOCTOU window. The
  sole same-card rescue froze ordered nested admissions in a sealed memfd and
  atomic descriptor-bound exec for every direct/outer/inner target.
- 2026-08-30T18:49:35Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
