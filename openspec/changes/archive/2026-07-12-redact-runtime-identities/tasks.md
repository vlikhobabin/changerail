## 1. Runtime Sanitizers

- [x] 1.1 Add repository identity sanitization to
  `scripts/changerail_delivery_manifest.py`.
- [x] 1.2 Add connectivity endpoint sanitization to
  `bin/changerail-delivery-runner`.

## 2. Regression Coverage

- [x] 2.1 Cover HTTPS remotes with user/password and token-like query values.
- [x] 2.2 Cover SCP-style SSH remotes.
- [x] 2.3 Cover connectivity success and failure diagnostics.

## 3. Docs And Verification

- [x] 3.1 Document sanitized identity guarantees and raw child log residual
  risk.
- [x] 3.2 Run `python3 scripts/smoke-delivery-manifest.py`.
- [x] 3.3 Run `python3 scripts/smoke-delivery-runner.py`.
- [x] 3.4 Run `./bin/openspec validate redact-runtime-identities --strict`.
- [x] 3.5 Run `git diff --check`.

## Verification Notes

- `python3 -m py_compile scripts/changerail_delivery_manifest.py bin/changerail-delivery-runner scripts/smoke-delivery-manifest.py scripts/smoke-delivery-runner.py` passed.
- `python3 scripts/smoke-delivery-manifest.py` passed.
- `python3 scripts/smoke-delivery-runner.py` passed.
- `./bin/openspec validate redact-runtime-identities --strict` passed.
- `git diff --check` passed.
- RED evidence is not applicable: this is a hardening change implemented with
  focused smoke fixtures rather than a test-first bug reproduction. The added
  smoke assertions inspect sanitized structured outputs and would fail if raw
  credentials or query values were persisted.
