# Skip published plan card on resume

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Review
- Risk tier: `ordinary`
- Review effort: `high`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Summary
Не запускать delivery child повторно для карточки, которая была опубликована
вне остановившегося aggregate run и при resume уже однозначно находится в
`4.done` в чистом синхронизированном repository.

## Acceptance
- `resume-plan` распознаёт ранее blocked карточку как delivered, если она теперь
  имеет ровно одно расположение в `4.done`, repository чист и `HEAD == upstream`.
- Для такой карточки child не запускается, а dependency разрешается продолжить.
- Dirty, divergent или неоднозначное состояние не получает auto-success.
- Focused regression, delivery-runner smoke и release baseline проходят.

## Change Set
- `skip-published-plan-card-on-resume`

## Change 1: `skip-published-plan-card-on-resume`

### Goal
Сделать resume идемпотентным после отдельного rescue/publish без ослабления
queue success criteria.

### Depends On
- none

### Size Budget
- At most 300 added production LOC.

## Verify
- focused published-card resume smoke
- `python3 scripts/smoke-delivery-runner.py`
- `bin/openspec validate --all --strict`
- `python3 scripts/run-release-baseline.py`
- `git diff --check`
- fresh independent ordinary/high review

## Next
- done

## Log
- 2026-08-21: bounded RED reproduced the exact blocked handoff: a current `4.done` card was relaunched and returned `already_published_card_requested_for_delivery`.
- 2026-08-21: resume reconciliation and focused GREEN regression implemented.
- 2026-08-21: full delivery-runner smoke passed; OpenSpec change archived and main spec synchronized.
- 2026-08-21: cycle-1 NO-GO found missing mutation coverage; divergent-upstream and permitted dirty-retained-resume negatives added.
- 2026-08-21T17:54:06Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.

## Result
Published-card reconciliation is bounded by the existing push-mode queue
success proof; pending independent review and publish.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.
