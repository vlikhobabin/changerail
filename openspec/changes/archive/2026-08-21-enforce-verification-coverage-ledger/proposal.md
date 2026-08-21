## Why

Schema сама по себе не предотвращает false-green: planning должен объявить
применимые invariants, delivery привязать observed evidence, а reviewer
fail-closed обнаружить missing или invalid proof. Нужен один derived ledger,
который проходит через существующие lifecycle и evidence surfaces.

## What Changes

- На planning/delivery boundary детерминированно выбирать applicable coverage
  entries для scoped changed paths и card acceptance.
- Записывать derived ledger в ignored runtime state и ссылаться на existing
  evidence-index ids вместо копирования raw outputs.
- Требовать от delivery manifest coverage outcome для каждой applicable записи
  и запрещать `pass` без observed oracle/evidence.
- На deterministic review preflight блокировать missing/stale ledger, а
  independent reviewer обязан сопоставить ledger с card acceptance и test
  adequacy.
- Сохранять текущий project-declared verification floor, когда coverage map не
  настроена; generic core не навязывает formatter/type/runtime matrix.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `changerail-agent-methodology`: `ff`, `do` и review используют единый
  fail-closed coverage flow.
- `changerail-skill-surface`: lifecycle skills создают, обновляют и аудитят
  derived coverage ledger.
- `changerail-project-verification`: deterministic preflight проверяет ledger и
  linked evidence до model review.
- `changerail-contracts`: manifest/evidence contracts связывают applicable
  coverage entries с observed evidence.

## Impact

- `skills/changerail-ff`, `skills/changerail-do`, `skills/changerail-review`
- `scripts/changerail_review_preflight.py`
- delivery manifest/evidence schemas and helpers
- focused false-green and generic Python end-to-end smokes
- зависит от `define-verification-coverage-map`
