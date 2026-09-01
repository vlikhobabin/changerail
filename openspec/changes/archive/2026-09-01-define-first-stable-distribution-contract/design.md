## Context

ChangeRail является generic source/toolchain repository, а не Python или npm
package. Первый stable release должен быть переносимым snapshot exact reviewed
Git tree, содержать лицензию и версию, иметь независимый checksum и позволять
оператору доказать source revision без включения machine-local state.

Release publication выполняется после semantic review. Поэтому tracked payload
должен содержать только builder, durable contract и проверки, а generated
archives/checksums/runtime evidence остаются вне Git и строятся повторно из
уже опубликованного exact commit.

## Goals / Non-Goals

**Goals:**

- определить один минимальный generic source bundle;
- сделать bytes archive воспроизводимыми для одинакового commit;
- связать filename, `VERSION`, `LICENSE`, source commit и SHA-256;
- дать CI/reviewer deterministic smoke без внешнего package registry;
- сохранить fail-closed порядок review, commit/push, tag и GitHub Release.

**Non-Goals:**

- публиковать Python wheel, npm package, OCI image или installer;
- менять runtime behavior, supported dependency pins или bootstrap topology;
- включать generated assets и runtime evidence в tracked payload;
- заявлять native Windows certification без live proof.

## Decisions

### Generic archive вместо language registry

Canonical asset — `changerail-<version>.tar.gz` с root prefix
`changerail-<version>/`. Он строится через `git archive` из exact commit и
сжимается gzip с нулевым timestamp. Это сохраняет Git modes/content, исключает
untracked/ignored state и не связывает ChangeRail с конкретным package manager.

Альтернативы (wheel/npm package) отклонены: они объявили бы language-specific
runtime/install contract, которого у репозитория нет. GitHub auto-generated
source archives недостаточны как единственный asset, потому что их bytes и
naming не принадлежат versioned ChangeRail contract.

### Text metadata sidecar без нового wire protocol

Builder создает рядом:

- `<archive>.sha256` с lowercase SHA-256 и basename archive;
- `changerail-<version>.release-metadata.txt` с version, license path,
  dereferenced source commit, archive basename и checksum basename.

Plain text выбран вместо нового JSON schema: card не авторизует новый wire
protocol. `VERSION` и `LICENSE` также находятся внутри archive. Source ref
обязательно разрешается в commit; dirty working tree не влияет на bytes, но
release procedure требует clean/fresh reviewed candidate отдельно.

### Tracked builder и smoke как source of truth

`scripts/build-source-distribution.py` принимает source ref и output directory,
проверяет semver/`LICENSE`, разрешает commit, строит три assets и не использует
network. `scripts/smoke-source-distribution.py` в temporary Git fixture дважды
строит bundle и сравнивает bytes, layout, metadata и checksum. Smoke входит в
core release inventory; extended suite не дублирует его.

### Publication после fresh GO

Tracked docs фиксируют порядок: final suite на frozen candidate → fresh xhigh
`GO` → scoped commit/push → remote reachability → annotated tag → assets из
dereferenced tag commit → public GitHub Release. Любая unexpected existing
tag/release metadata, missing authority или mismatch останавливает публикацию.

## Risks / Trade-offs

- **Разные gzip implementations могут менять bytes** → builder использует
  Python standard library с фиксированным `mtime=0`, а smoke сравнивает два
  независимых build output.
- **Tag может указывать не на reviewed/published commit** → publication
  проверяет local/remote dereferenced target до asset build и после push.
- **Metadata sidecar не имеет schema** → фиксированный key/value contract и
  smoke дают достаточную проверку без введения нового wire protocol.
- **Generated assets могут попасть в Git** → output направляется в ignored или
  temporary directory и manifest явно исключает release artifacts.

## Migration Plan

1. Добавить builder, smoke и release docs/spec.
2. Проверить focused smoke и core baseline.
3. Sync delta spec и archive change до independent review.
4. Для `1.0.0` построить assets заново только после publication commit/tag.

Rollback до создания tag состоит в удалении scoped uncommitted payload через
обычный review/fix flow. После public release rollback не переписывает tag:
публикуется новый corrective release либо release помечается как withdrawn с
сохранением audit trail.

## Open Questions

Нет. Первый stable release использует только этот минимальный source bundle;
дополнительные package formats требуют отдельной карточки.
