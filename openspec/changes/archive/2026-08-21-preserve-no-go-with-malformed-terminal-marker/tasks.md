## 1. Terminal classification

- [x] 1.1 Разрешить schema-valid canonical `no-go` заменить только
  `BLOCKED/malformed_terminal_reason`.
- [x] 1.2 Сохранить fail-closed поведение malformed marker без valid negative
  verdict и всех positive verdict paths.

## 2. Regression coverage and contracts

- [x] 2.1 Добавить smoke с final canonical no-go и malformed child reason.
- [x] 2.2 Синхронизировать normative runner spec и contracts guide.

## 3. Verification

- [x] 3.1 Запустить focused delivery-runner smoke и strict OpenSpec validation.
- [x] 3.2 Запустить полный release baseline, public-surface checks и diff check.
- [ ] 3.3 Получить fresh independent ordinary/high review.
