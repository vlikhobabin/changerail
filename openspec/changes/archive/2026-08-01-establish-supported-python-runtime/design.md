## Context

ChangeRail уже содержит несколько tracked Python helper-ов в `bin/` и
`scripts/`: `verify-project`, review verdict, delivery manifest, delivery
runner, delivery metrics и release smoke. Часть helpers импортирует `tomllib`,
что делает фактический минимум Python 3.11, а schema-backed contract helpers
требуют `jsonschema`. Сейчас это не объявлено как runtime API, и failures могут
возникать до понятного ChangeRail diagnostic.

## Goals / Non-Goals

**Goals:**
- Зафиксировать Python 3.11 как минимальный supported runtime для ChangeRail
  Python helpers.
- Разделить runtime dependency (`jsonschema`) и release-only tooling
  (`PyYAML`, `ruff`) в tracked dependency files и docs.
- Добавить один shell-level selector, который проверяет interpreter и modules
  до запуска Python code.
- Поддержать `CHANGERAIL_PYTHON` override без изменения tracked shebangs.
- Оставить runtime records только под ignored `.runtime/changerail/`.
- Покрыть supported, old-version, missing dependency и invalid override cases
  focused smoke test-ом.

**Non-Goals:**
- Native Windows command shims остаются scope серии `040`.
- Packaging ChangeRail как wheel/installer не входит в эту карточку.
- Замена OpenSpec, Codex или npm dependency selection не входит в runtime
  contract.

## Decisions

1. **Python 3.11 как supported minimum.**

   Rationale: helpers уже используют stdlib `tomllib`, который появился в
   Python 3.11. Поддержка Python 3.10 потребовала бы backport dependency и
   усложнила bootstrap без явной необходимости.

   Alternative considered: поддержать Python 3.10 через `tomli`. Rejected,
   потому что это добавляет еще один runtime package только для обхода уже
   принятого stdlib contract.

2. **Явный runtime dependency file.**

   `requirements-runtime.txt` становится source of truth для packages,
   необходимых public Python helpers во время обычной работы. На старте это
   `jsonschema`, потому что manifest/verdict validation должна оставаться
   schema-backed. `requirements-dev.txt` может включать runtime requirements,
   но не является implicit runtime API.

3. **Shell-level selector перед Python import.**

   Добавить tracked `bin/changerail-python`, который:
   - выбирает `CHANGERAIL_PYTHON`, если override задан;
   - иначе выбирает `python3`/`python` из `PATH`;
   - запускает probe через выбранный interpreter;
   - проверяет version >= 3.11 и required modules;
   - пишет sanitized check record under
     `.runtime/changerail/python-runtime/`;
   - exec-ит выбранный interpreter с target script.

   Rationale: Python-level bootstrap не может дать ранний diagnostic, если
   выбранный interpreter слишком старый для parsing/import.

4. **Executable helpers use one selector.**

   `bin/verify-project`, `bin/changerail-review-verdict`,
   `bin/changerail-delivery-runner` и `bin/changerail-delivery-metrics`
   получают shell/Python polyglot prelude, который exec-ит
   `bin/changerail-python` и затем продолжает выполнять существующий Python
   code. Contract helper invocations from docs/skills use the same selector for
   `scripts/changerail_delivery_manifest.py` and
   `scripts/changerail_review_verdict.py`.

5. **Diagnostics are actionable and public-safe.**

   Failure messages name the required version, missing module or invalid
   override and point to runtime/dependency remediation. They must not print
   secrets or raw environment values beyond the override command/path needed to
   fix the invocation.

## Risks / Trade-offs

- [Risk] Polyglot prelude can break executable helpers if malformed.
  Mitigation: focused smoke executes helper entrypoints and compile inventory
  still compiles them as Python.
- [Risk] Always requiring `jsonschema` raises the baseline for helpers that do
  not import it directly.
  Mitigation: document `requirements-runtime.txt` and keep release-only
  dependencies separate.
- [Risk] Direct `python3 scripts/*.py` invocations can bypass the selector.
  Mitigation: update public docs, skills and smoke tests to prefer
  `bin/changerail-python scripts/<helper>.py ...` for runtime helpers.

## Migration Plan

1. Add runtime selector and explicit runtime requirements.
2. Route public helper entrypoints through the selector.
3. Update compatibility and migration docs with the version/modules/override
   contract.
4. Add focused smoke coverage and include it in the local release baseline.
5. Verify with focused smoke, release baseline, OpenSpec strict validation,
   public-surface scan and whitespace checks.

## Open Questions

None.
