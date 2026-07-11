## 1. Verification Contract

- [x] 1.1 Update shared methodology and how-it-works docs with project-declared verification floor language.
- [x] 1.2 Update `opsx-do` to collect mandatory checks from local rules, OpenSpec artifacts and affected toolchain.
- [x] 1.3 Update `opsx-review` to audit mandatory verification evidence and test adequacy claims.

## 2. Evidence Semantics

- [x] 2.1 Document command/outcome evidence expectations and when RED evidence is not applicable.
- [x] 2.2 Ensure delivery manifest/reference text can record verification evidence without committing raw runtime logs.

## 3. Verification

- [x] 3.1 Run `./bin/openspec validate declare-delivery-verification-floor --strict`.
- [x] 3.2 Run `git diff --check`.
