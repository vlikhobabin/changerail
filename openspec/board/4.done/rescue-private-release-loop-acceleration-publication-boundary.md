# Спасти публикацию ускоренного release loop через чистую bounded lineage

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- release-baseline-acceleration

## Series Index
- 02R9-C

## Source
- Published passive A1 authorization `b027d30441ad366931aa5c89203a4286efbfa4b1`.
- A private integration prototype and its retained ignored evidence are
  forensic design input only; no local commit identifier, diff, executable
  payload, receipt or runtime evidence from that prototype is publication
  authority.

## Summary
Заменить исчерпанный A1/A2 порядок чистой public lineage из четырех bounded
implementation owners. Две независимые основы, structural history scanner и
isolated case executor, могут разрабатываться параллельно; registry/affected
profile и payload-bound terminal authority выполняются после них. Измеряемая
оптимизация full-release bottleneck-ов и native Windows certification остаются
отдельными downstream стадиями.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Planning: fresh `gpt-5.6-sol`/`high`
- Implementation: docs-only deterministic
- Independent review: fresh `gpt-5.6-sol`/`high`
- Same-card repair: at most one fresh `gpt-5.6-terra`/`high`
- Re-review: fresh `gpt-5.6-sol`/`high`
- Same-card repair/rescue budget limit/used/remaining: `1/1/0`, exhausted `true`

Decision-only payload изменяет только tracked planning/spec artifacts и не
создает executable authority, wire behavior или повторную реализацию дефекта.
Единственный `xhigh` audit зарезервирован для финальной неизменяемой
full-release certification после публикации всех executable successors.
H, I, R and A successors declare `ordinary` risk and use fresh Sol/`high` review:
their bounded published authorizations permit protocol/authority work, while
they explicitly exclude credential/mutation authority, live admission and final
certification. Only the separate final certification card declares `critical`
and uses the reserved Sol/`xhigh` audit.

## Depends On
- `rescue-tiered-release-authority-two-stage-boundary`
- `authorize-bounded-passive-release-admission-registry`

## Blocks
- `authorize-clean-structural-history-scan-v3`
- `deliver-clean-structural-history-scan-v3`
- `authorize-bounded-isolated-release-case-executor-v2`
- `implement-bounded-isolated-release-case-executor-v2`
- `authorize-bounded-public-release-registry-profile-v2`
- `implement-public-release-registry-profile-v2`
- `authorize-bounded-payload-release-authority-v2`
- `implement-payload-bound-release-authority-v2`
- `profile-and-optimize-full-release-bottlenecks`
- `certify-native-windows-release-containment`

## Acceptance
- Решение явно supersedes старый обязательный порядок A1 -> A2 -> scanner ->
  Windows только для новой clean lineage; опубликованные старые решения и
  архивы не переписываются.
- Private prototype остается forensic-only: его commits не cherry-pick-ятся,
  runtime evidence не принимается как review/publish evidence, а executable
  successors реализуются заново от точных published predecessor HEAD.
- History и isolation foundations имеют непересекающееся владение и после
  публикации решения могут выполняться параллельно в отдельных clean
  worktrees. Registry/profile зависит от обеих основ; terminal authority
  зависит от registry/profile.
- Четыре будущих six-field authorization objects точны, одноразовы и имеют
  независимые ceiling не выше `500`; executable implementation остается на
  одну строку ниже своего ceiling против собственного published auth HEAD.
- Full-release authority получает bounded semantic execution, per-step
  timeout/output/process cleanup, deterministic ordered results, per-step
  telemetry, payload fingerprint, atomic receipt и manifest/review/pub
  equality. Affected остается non-authoritative при любом fallback.
- После authority publication отдельная measured optimization выбирает
  bottleneck-и по per-step telemetry без ослабления full gate; native Windows
  containment получает настоящий Windows run до финальной certification.
- Эта docs-only decision имеет production/test/runtime LOC `0` и не запускает
  history scan, full baseline, live Windows, implementation, successor,
  archive, review, commit или push во время FF.

## Change Set
- `rescue-private-release-loop-acceleration-publication-boundary`

## Verify
- Strict target/all OpenSpec, exact authorization/lineage/order oracle,
  JSON/TOML, current public scan, source classification, whitespace and scope.
- No reachable-history scan, full release baseline or live Windows run.

## Archive
- `openspec/changes/archive/2026-08-25-rescue-private-release-loop-acceleration-publication-boundary/`

## Related
- `openspec/changes/archive/2026-08-25-rescue-private-release-loop-acceleration-publication-boundary/`
- `openspec/board/4.done/rescue-tiered-release-authority-two-stage-boundary.md`
- `openspec/board/4.done/authorize-bounded-passive-release-admission-registry.md`
- `openspec/specs/changerail-release-ci/spec.md`

## Result
DO complete: one docs-only decision change was synchronized into the canonical
release-CI spec and archived. It defines four bounded clean successors, one
parallel foundation wave, sequential authority activation, measured
optimization and native Windows certification without creating or running any
executable successor. Cycle-1 review returned NO-GO for R1-R4; the single
bounded docs repair is complete and fresh cycle-2 independent review remains
pending.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `rescue-private-release-loop-acceleration-publication-boundary`

### Why
Приватный multi-worktree prototype доказал быстрый affected loop и полный
authoritative pass, но его ancestry нарушает опубликованный A1/A2 publication
order и не имеет payload-bound public receipt. Публиковать aggregate branch
нельзя.

### Goal
Зафиксировать clean-room public decomposition, точные authorization boundaries,
параллельную foundation wave и последовательные authority/optimization gates.

### Scope
- Decision/card/release-CI contract only; executable LOC `0`.

### Acceptance
- Старый порядок superseded только новой decision lineage; исторические
  sources остаются неизменными.
- Четыре bounded successors, зависимости, proof gates и private-forensic
  boundary заданы полностью и без ownership overlap.
- Финальный expensive capture выполняется один раз только после всех focused,
  static, receipt и native Windows gates.

### Depends On
- `rescue-tiered-release-authority-two-stage-boundary`
- `authorize-bounded-passive-release-admission-registry`

### Related
- `openspec/changes/archive/2026-08-25-rescue-private-release-loop-acceleration-publication-boundary/`

## Log
- 2026-08-25 card created from exact published base `b027d304`; private
  prototype remains forensic-only and no local identifier is tracked.
- 2026-08-25 FF created exactly one same-slug proposal, design, release-CI
  delta and tasks set; target and all strict OpenSpec validation passed without
  history, full-release, live Windows, archive, review, commit or push.
- 2026-08-25 DO synchronized the complete modified requirement, archived the
  sole change and prepared a docs-only review handoff; no successor, history,
  full-release, live Windows, review, commit or push ran.
- 2026-08-25 cycle-1 Sol/high review returned NO-GO for R1-R4. The only allowed
  docs repair removed local forensic identity, renamed the active requirement,
  strengthened pre-child/equality/no-retry norms and made H/I/R/A ordinary/high
  versus final-certification critical/xhigh routing explicit.
- 2026-08-25T19:01:05Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
