## 1. Decision Contract

- [x] 1.1 Сверить card/proposal/design/spec: все numeric, value, aggregate и
  token/depth ceilings, stable details, role order и zero-dispatch oracle
  published commit `6e1cbfa` сохранены exact.
- [x] 1.2 Зафиксировать observable field-17 prefix gate до line-end/content
  access, trim/backtick work или span retention для source и inline roles.
- [x] 1.3 Зафиксировать incremental RFC 8259 number FSM без whole-tail regex,
  fallback/rollback и numeric conversion: valid continuation 65 выигрывает до
  value character 4097.
- [x] 1.4 Зафиксировать exact nested `NaN`/`Infinity`/`-Infinity` delimiter
  rules для end, whitespace, comma, `]`, `}`, suffix/malformed controls и
  lowercase-only inline `none`.
- [x] 1.5 Зафиксировать future connected source/inline matrix при
  `PYTHONINTMAXSTRDIGITS=640` и `0`, включая 4301-digit, field-17 read-bound,
  no-conversion и все published boundary/collision rows.
- [x] 1.6 Зафиксировать, почему exhausted payload non-repairable,
  non-publishable и `SUPERSEDED`, сохранив `6e1cbfa`, worktree и cycle-1/cycle-2
  history неизменными.
- [x] 1.7 Сверить exact A->B->C->D->successor ids, paths и adjacent relations,
  B six-field object с ceiling 301/protocol false и D six-field object с
  ceiling 500/protocol true.

## 2. Decision Apply And Archive

- [x] 2.1 Только во время `$changerail-do` синхронизировать один added
  requirement в `openspec/specs/changerail-contracts/spec.md` без runtime edits.
- [x] 2.2 После successful decision validation архивировать только
  `decide-incremental-authorization-gate-boundary` и обновить только A card
  stage/archive/result/related metadata.
- [x] 2.3 Оставить A в `3.inprogress` для fresh independent review; не создавать
  verdict, commit, push или publish в apply loop.
- [x] 2.4 Не создавать B до published A, C до published B, D до published C и
  не изменять existing successor до published D.

## 3. Investigation Verification

- [x] 3.1 Запустить `bin/openspec validate
  decide-incremental-authorization-gate-boundary --strict` до sync.
- [x] 3.2 После apply-time sync запустить `bin/openspec validate
  changerail-contracts --strict` и `bin/openspec validate --all --strict`.
- [x] 3.3 Запустить `python3 scripts/public-surface-scan.py`, JSON parse
  `.mcp.json` и TOML parse `.codex/config.toml`.
- [x] 3.4 Запустить `git diff --check`, explicit whitespace scan новых untracked
  artifacts и scoped status/diff check для card/change/main-spec/archive paths.
- [x] 3.5 Записать runtime RED/GREEN как `not applicable` для decision-only
  payload и подтвердить отсутствие code/tests/main-spec/archive/verdict edits
  во время fast-forward.

## 4. Future Lineage Handoff

- [x] 4.1 Передать B exact authorization object и обязанность publish source с
  ceiling 301/protocol false до создания C.
- [x] 4.2 Передать C exact published-B reference, incremental extractor/FSM и
  dual-environment connected implementation floor без superseded identity.
- [x] 4.3 Передать D exact authorization object с ceiling 500/protocol true
  только после published C.
- [x] 4.4 Передать existing successor exact published-D reference и fail-closed
  запрет продолжения при missing/stale/mismatched source.
