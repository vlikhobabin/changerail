## Context

Published rescue v9 заменил неприменимый executable v8 contract чистой
lineage, где implementation обязана прямо зависеть от rescue investigation id.
До создания implementation нужен отдельный reviewed authorization commit,
который связывает exact successor, ceiling и protocol allowance.

Latest safe source — published rescue tip
`ab8e9a5391fc9be6a5e2c1a2f8ffad9202626c6f`. Terminal v8 card, code, tests,
manifest, evidence и preflight runtime state не являются input.

## Goals / Non-Goals

**Goals:**

- опубликовать exact six-field authorization для единственного v9 successor;
- закрепить exact authorization dependencies и sole block;
- потребовать direct rescue dependency в future implementation;
- сохранить retained RED, 499 LOC ceiling и accumulated affected floor;
- оставить affected mode non-authoritative и certification заблокированной.

**Non-Goals:**

- создавать implementation v9 card, tests, code, CI или runtime authority;
- читать, исправлять или воспроизводить terminal v8 payload/evidence;
- менять generic direct-investigation preflight;
- запускать history, real full/affected, benchmark, live matrix или
  certification checks;
- предоставлять affected mode publication authority.

## Decisions

### 1. Authorization object копируется exact из published rescue

Card и delta spec содержат один unwrapped six-field JSON object с rescue card/id,
future successor card/id, `production_loc_ceiling: 500` и
`allow_new_authority_or_wire_protocol: true`. Дополнительные поля, alternate
successor или меньший/больший ceiling не допускаются.

### 2. Authorization и implementation имеют разные exact dependency sets

Authorization зависит ровно от rescue v9, integration decision, scheduler v1
и authorization v8 и блокирует только implementation v9. Future implementation
добавляет эту authorization к rescue/integration/scheduler/auth-v8 set и
блокирует только certification. Rescue id присутствует напрямую и совпадает с
six-field `investigation_id`.

Альтернатива — полагаться на transitive dependency через authorization —
отклонена, потому что именно она воспроизвела бы v8 preflight contradiction.

### 3. Authorization не заменяет implementation evidence

Future implementation всё равно начинает test-first attempt: retained command
печатает fingerprint, затем напрямую запускает non-zero focused test и
сохраняет reachable pre-production tree. Authorization только делает этот
contract обязательным; synthetic note или late reproduction не принимаются.

### 4. Accumulated floor переносится без executable mutation

Authorization сохраняет exact 35→30 profile, typed aggregate admission,
effective package origins, four-stream selection, typed scheduler, full-only
authority, four-step CI, closed execution ownership, connected mutants и
protocol-artifact non-authority. Текущий change меняет только docs/spec/archive
и имеет production/test/runtime LOC `0`.

## Risks / Trade-offs

- [Risk] Большой accumulated contract может скрыть dependency detail →
  mitigation: exact sets и direct rescue edge перечислены отдельно и
  проверяются статически.
- [Risk] Protocol allowance может выглядеть как publication grant →
  mitigation: full-release остаётся единственным authority, affected artifacts
  явно non-authoritative.
- [Risk] Successor появится раньше remote publication → mitigation: проверять
  его отсутствие до review/publish и создавать только от published auth HEAD.

## Migration Plan

1. Опубликовать эту docs-only authorization от exact rescue HEAD.
2. Подтвердить remote authorization branch на exact published commit.
3. Только затем создать clean implementation v9 с direct rescue dependency и
   retained pre-production RED.
4. После fresh Sol/high GO и публикации implementation открыть critical
   certification.

Rollback — не создавать implementation successor. Authorization не меняет
executable behavior.

## Open Questions

- none; exact successor и dependency boundary опубликованы rescue v9.
