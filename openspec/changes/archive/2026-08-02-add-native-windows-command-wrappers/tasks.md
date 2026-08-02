## 1. Wrapper Surface

- [x] 1.1 Add tracked `.cmd` wrappers for `openspec`, `changerail-python`,
  `verify-project`, `changerail-review-verdict`, `changerail-evidence`,
  `changerail-delivery-runner` and `changerail-delivery-metrics`.
- [x] 1.2 Route Python-backed helper wrappers through `changerail-python.cmd`
  and preserve the shared runtime selector diagnostics.
- [x] 1.3 Preserve existing POSIX helper entrypoints and avoid implicit Bash or
  extensionless POSIX launch as the native Windows default.

## 2. Documentation And Contract

- [x] 2.1 Update compatibility or operator-facing docs that describe supported
  native Windows helper entrypoints.
- [x] 2.2 Record why deterministic wrapper behavior tests are delivered by the
  dependent `test-native-windows-entrypoints` change.

## 3. Verification

- [x] 3.1 Run `bin/openspec status --change add-native-windows-command-wrappers --json`.
- [x] 3.2 Run `bin/openspec instructions apply --change add-native-windows-command-wrappers --json`.
- [x] 3.3 Run `bin/openspec validate add-native-windows-command-wrappers --strict`.
- [x] 3.4 Run focused local checks for wrapper inventory and static command
  safety.
- [x] 3.5 Run `git diff --check`.
