## Context

Single-card runner сначала извлекает structured terminal signal из child
JSONL, а canonical verdict читает только как fallback при полном отсутствии
outcome. Это правильно для валидных structured reasons, но превращает опечатку
в reason после final review в потерю schema-valid `no-go`.

## Decisions

- При наличии `BLOCKED/malformed_terminal_reason` отдельно проверить canonical
  verdict тем же валидатором, который уже используется fallback path.
- Заменять marker только когда валидатор возвращает `NO-GO`.
- Не принимать `go` через этот путь: fresh, stale и invalid positive verdicts
  не могут авторизовать публикацию и не меняют malformed diagnostic.
- Оставить обычный malformed-marker smoke без verdict как negative control.

## Risks / Trade-offs

- [Старый negative verdict может остановить новый payload] -> это уже принятый
  conservative contract: no-go не авторизует commit/push и требует нового
  review для продолжения.
- [Дополнительный локальный вызов verdict validator] -> выполняется только для
  редкого malformed-marker path и остается bounded.
