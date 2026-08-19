## Context

`bin/bootstrap-project --configure-existing --refresh-wiring` уже является
bounded surface для existing consumers, но lock-owned refresh требует
`openspec/changerail-consumer-lock.json`. Legacy consumer, подключенный до
consumer lock, может иметь корректные ChangeRail symlinks, `.codex` skills,
Claude commands и helper wrappers, но refresh не может доказать intended
ownership и поэтому останавливается.

Этот change добавляет отдельный adoption path между lockless compatibility и
lock-owned refresh. Он должен принять только уже доказанную ChangeRail-owned
surface, создать tracked intent и добавить missing allowlisted helper без
перезаписи project-owned files.

## Goals / Non-Goals

**Goals:**
- дать оператору explicit opt-in migration для lockless existing consumer;
- сохранить fail-closed behavior обычного `--refresh-wiring`;
- вывести dry-run inventory с keep/add/reject decisions до mutation;
- доказать single-root ownership, backend и path mode перед записью lock;
- создать schema-valid consumer lock и, для generated-copy wiring, manifest;
- покрыть POSIX symlink и Windows generated-copy/junction policy decisions;
- обновить runbook с rollback и remediation steps.

**Non-Goals:**
- автоматически принимать произвольные `.codex`, `.claude`, `bin/` или
  application files как ChangeRail-owned;
- менять `AGENTS.md`, `.codex/config.toml`, `.mcp.json`, board cards,
  application source, auth files или unrelated Git state;
- повышать Codex authority profile или менять project verification policy без
  explicit tracked evidence;
- создавать новый wire schema или заменять существующий consumer lock contract.

## Decisions

### Separate adoption flag

Adoption остается в `--configure-existing`, но получает отдельный explicit flag,
например `--adopt-lockless-wiring`, который можно сочетать с dry-run и выбранным
lock enforcement. `--refresh-wiring` без lock продолжает fail-closed, чтобы
existing automation не начала принимать неизвестную surface как owned.

Alternative: сделать missing lock автоматическим adoption prompt. Это хуже для
non-interactive runner-ов и противоречит fail-closed refresh contract.

### Inventory-first plan

Bootstrap строит allowlisted inventory из того же canonical wiring inventory,
который используется fresh bootstrap и refresh. Каждый destination получает
decision:

- `keep`: existing artifact matches allowed ChangeRail source root;
- `add`: artifact отсутствует, но может быть создан через inferred backend/path
  mode;
- `reject`: artifact dangling, mixed-root, regular-file, undeclared,
  project-owned, escaped или unsupported для platform policy.

Apply разрешен только если весь plan не содержит blocking rejects. Dry-run
печатает plan и не пишет lock, manifest или helper.

### Single source and backend inference

POSIX adoption принимает symlinks только если accepted artifacts resolve under
один declared ChangeRail root. Path mode выводится как `absolute` или
`relative` по actual targets, а mixed mode блокируется. Missing helper
создается тем же mode.

Windows generated-copy adoption принимает только artifacts с verifier-readable
generated ownership metadata. Если metadata отсутствует или junction/symlink
fallback не имеет требуемого proof, adoption блокируется с remediation вместо
inferred overwrite.

### Lock after proof

Consumer lock и generated manifest записываются только после successful
preflight. Lock reuses `changerail.consumer-lock.v1`, records source
version/revision, selected profiles, backend/path mode, artifact inventory and
enforcement. Source revision must come from a clean tracked ChangeRail checkout;
dirty source fails before target mutation.

### No project-owned mutation

Migration never edits project-owned instructions, config, source, board cards,
auth or unrelated Git state. Only adopted ChangeRail-owned wiring paths,
generated ownership metadata and consumer lock are in scope. Partial failure
rollback removes only current-run-created artifacts and never recurses into link
targets.

## Risks / Trade-offs

- [Risk] Legacy consumer has partial but usable custom wiring -> Mitigation:
  report reject reasons and require manual ownership cleanup before adoption.
- [Risk] Missing helper is added with wrong topology -> Mitigation: infer backend
  and path mode only from accepted artifacts on one source root; mixed evidence
  blocks migration.
- [Risk] Lock creation could expose local paths -> Mitigation: lock stores
  public-safe source identity and project-relative artifact inventory, not
  resolved machine roots or credential-bearing URLs.
- [Risk] Operators confuse adoption with refresh -> Mitigation: `--refresh-wiring`
  remains lock-required and diagnostics name the explicit adoption command.

## Migration Plan

1. Add plan/inventory model and CLI flag for dry-run lockless adoption.
2. Implement fail-closed POSIX and Windows inference gates.
3. Write lock/manifest only after full preflight passes, with scoped rollback for
   current-run-created artifacts.
4. Add successful, negative and idempotency smoke fixtures under ignored runtime
   space.
5. Update consumer adoption runbook with migration, verification and rollback.

## Open Questions

- Final CLI spelling may be adjusted during implementation, but it must remain
  explicit and separate from plain `--refresh-wiring`.
