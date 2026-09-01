## Context

`origin/main@aabfb2d8d7ba98e727766f2cb0299a607389b6d9` содержит
опубликованный merge PR #6 и clean-core scope decision. Release preparation
добавляет только stable metadata и generic distribution tooling/contract; все
phase-routed delivery и runtime-retention payloads остаются deferred.

Карточка является critical final certification с mutation authority. Exact
tracked payload должен быть frozen до fresh xhigh independent review, а tag и
GitHub Release разрешены только после `GO`, scoped publish и remote proof.

## Goals / Non-Goals

**Goals:**

- согласовать `VERSION`, changelog, compatibility, migration и release notes;
- сертифицировать один exact candidate в isolated clone на 2 CPUs;
- выполнить core и extended heavy suites строго последовательно с pinned dev
  dependencies;
- выполнить release CI smoke, current/history scans и trusted-network
  integrity checks;
- опубликовать annotated `v1.0.0` и public GitHub Release с reproducible source
  assets только после fresh `GO`.

**Non-Goals:**

- добавлять deferred payloads или менять runtime/dependency pins;
- переопределять native Windows support без real live evidence;
- использовать другие worktrees или root checkout как release candidate;
- создавать package-registry distribution.

## Decisions

### Один frozen candidate fingerprint

После tracked implementation payload создается isolated local clone из exact
working-tree candidate commit/tree. Pinned `requirements-dev.txt` ставится в
candidate-local venv. Environment ограничивается двумя CPUs, core и extended
commands запускаются последовательно, затем на том же candidate выполняются
smoke/public/trusted checks. Evidence сохраняет commit/tree/fingerprint и
command outcomes в ignored runtime state.

### Linux-focused support claim и Windows caveat

Без нового native Windows live evidence `1.0.0` остается Linux-focused stable
release. Compatibility, migration и release notes явно говорят, что native
Windows helpers существуют, но platform release certification не заявляется.
Private host data и synthetic evidence не создаются.

### Stable metadata

`VERSION` становится `1.0.0`. `CHANGELOG.md` сохраняет пустой `Unreleased` и
добавляет `1.0.0 - 2026-09-01`, суммирующий public changes после `0.5.0` без
ложного dependency-pin claim. Compatibility и migration guide содержат exact
`0.5.0 -> 1.0.0` actions, verification и rollback. Durable release notes
описывают source assets и caveats без mutable commit hash.

### Final publication transaction

После fresh `GO` substantive edits запрещены. Publish создает scoped reviewed
commit и push-ит feature branch, но оставляет card в `3.inprogress`. После
exact parent/tree, committed-manifest scope и remote feature-branch proof
создается annotated `v1.0.0` на этом commit, tag push-ится без force, assets
строятся из dereferenced target и создается public GitHub Release. Только после remote и downloaded-asset proof
publish детерминированно финализирует card отдельным card-only commit и
push-ит его без изменения immutable release tag. Existing unexpected
tag/release или missing credentials останавливают transaction с card в
`3.inprogress`.

Canonical freshness проверяется на reviewed working tree перед staging.
Созданный после проверки commit не объявляется новым fresh review state:
publish сравнивает его parent с recorded review HEAD, а tree — с recorded
review tree. Для `1.0.0` exact identity — annotated message
`ChangeRail 1.0.0`, hosted title `ChangeRail 1.0.0` и notes body из полного
tracked `docs/releases/1.0.0.md`. Partial resume допускает только unique subset
трёх contracted basenames: каждый присутствующий asset должен byte-match-ить
fresh build из tag, загружаются только отсутствующие; duplicate, unexpected
или mismatched asset является hard stop.

## Risks / Trade-offs

- **Heavy suites могут видеть shared refs** → запускать только в isolated clone
  с frozen candidate и bounded refs.
- **Network metadata может измениться** → сравнивать live trusted registry
  integrity с tracked pins; не обновлять pins в этой карточке.
- **Review устареет после metadata edit** → после `GO` разрешена только
  deterministic board finalization; любые substantive edits возвращаются в
  delivery/review.
- **GitHub mutation может выполниться частично** → проверять каждый remote
  объект read-only и fail closed; существующий корректный шаг можно принять
  idempotently, неожиданный — не переписывать.

## Migration Plan

1. Реализовать tracked release metadata и verification contract.
2. Выполнить isolated certification, sync/archive и manifest handoff.
3. Получить fresh xhigh independent `GO`.
4. Scoped reviewed commit/push, затем annotated tag/assets/public GitHub
   Release при card в `3.inprogress`.
5. Проверить remote main/branch/tag и public release metadata read-only, затем
   финализировать card отдельным deterministic card-only commit/push.

Rollback consumer upgrade описывается в migration guide. После публикации
immutable tag не перемещается; corrective changes выпускаются новым semver.

## Open Questions

Нет. Native Windows certification остается отдельной будущей admission work,
если появится настоящее live evidence.
