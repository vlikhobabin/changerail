# OPSX contracts

Статус: рабочий контракт для review, delivery и evidence handoff.

## Namespace

Новые публичные wire contracts OPSX используют namespace `opsx.*`:

- `opsx.review-verdict.v1`
- `opsx.delivery-manifest.v1`
- `opsx.evidence-index.v1`

Schemas находятся в `schemas/`:

```text
schemas/opsx-review-verdict.schema.json
schemas/opsx-delivery-manifest.schema.json
schemas/opsx-evidence-index.schema.json
```

Review verdict-файлы и public schemas должны использовать только
`opsx.review-verdict.v1`; helper отклоняет другие schema ids.

## Review Verdict

Review verdict является runtime-файлом:

```text
.runtime/opsx/reviews/<card-id>.json
```

Он не коммитится. Publish gate принимает только verdict, который:

- валиден по shape и cross-field правилам;
- имеет `result: go`;
- fresh относительно текущего `HEAD`, `git status --porcelain`,
  `git diff HEAD --no-color` и содержимого untracked non-ignored файлов,
  перечисленных через `git ls-files --others --exclude-standard`.

Helper:

```bash
python3 scripts/opsx_review_verdict.py fingerprint --workspace .
python3 scripts/opsx_review_verdict.py validate \
  ".runtime/opsx/reviews/<card-id>.json" --check-fresh --workspace . --json
```

Consumer project может вызывать helper через wrapper:

```bash
bin/opsx-review-verdict fingerprint --workspace .
bin/opsx-review-verdict validate \
  ".runtime/opsx/reviews/<card-id>.json" --check-fresh --workspace . --json
```

Exit codes: `0` valid, `1` validation failed, `2` input error.

Ignored paths не входят в freshness fingerprint. Поэтому запись verdict под
`.runtime/opsx/reviews/` не инвалидирует сам verdict, но изменение содержимого
нового untracked deliverable-файла делает verdict stale.

## Delivery Manifest

Delivery manifest является runtime-файлом:

```text
.runtime/opsx/delivery-manifests/<card-id>.json
```

Он описывает card-owned scope: planned changes, committable paths, excluded
runtime paths, preexisting dirty state и publish handoff details. Publish
использует manifest как initial staging proposal, но обязан повторно сверить
его с `git status` и не stage-ить runtime files.

## Evidence Index

Evidence index описывает retained evidence для verification/review handoff.
Evidence может быть committable, runtime или external, но committed artifact не
должен содержать secrets, credentials, customer data, local traces или большие
сырые логи.

## Public Safety

Contracts are public source. Примеры должны использовать только generic пути
вроде `/opt/opsx` и `/opt/example-project`. Runtime payloads, verdicts,
manifests и local evidence остаются ignored state.
