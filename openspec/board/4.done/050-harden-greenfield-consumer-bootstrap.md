# Усилить greenfield bootstrap потребителя: переносимость, CI и профили

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Series
- none

## Series Index
- none

## Source
- Sanitized operator evidence от 2026-08-05: создание нового product workspace
  через `bin/bootstrap-project`, публикация и первый clean-clone CI run.
- Актуализация 2026-08-10 против текущих `bin/bootstrap-project`,
  `bin/verify-project`, templates, smoke fixtures, Windows support и
  maintenance consumer readiness.

## Summary
Довести bootstrap нового ChangeRail consumer от локально корректного skeleton до
воспроизводимого пути, в котором оператор явно выбирает topology, agent surfaces
и Codex authority, получает переносимый wiring contract, version lock и
опциональный CI, а существующий consumer можно безопасно донастроить без
перегенерации project-owned файлов.

```text
bootstrap profile
  -> portable tracked wiring intent
  -> optional strict source lock and CI
  -> explicit local auth/Git handoff
  -> static verification + opt-in runtime evidence
```

## Research Snapshot

### Confirmed Current Gaps
- POSIX bootstrap всегда пишет relative symlink targets через
  `os.path.relpath()`, поэтому clean clone зависит от исходной sibling topology.
- `--kind` остается document label и не меняет generated topology или policy.
- Generated Codex config всегда выбирает `approval_policy = "never"` и
  `sandbox_mode = "danger-full-access"` без explicit operator choice.
- Verification profile уже поддерживает `required`, `optional` и `forbidden`
  surfaces, но bootstrap не дает operator-facing выбора `codex-only` или
  `all-surfaces`.
- POSIX symlink consumers не имеют tracked intended wiring/source revision и не
  могут использовать существующий generated-copy-only `--refresh-wiring`.
- Consumer CI template и exact ChangeRail revision handoff отсутствуют.
- `--link-codex-auth` работает только при initial bootstrap; verifier указывает
  путь к runbook, которого нет в consumer repository, вместо готовой команды.
- Bootstrap не генерирует consumer README и не имеет opt-in Git initialization.
- Static config checks не доказывают effective Codex runtime; отдельного
  redacted runtime diagnostic contract нет.
- Fresh generated `AGENTS.md` занимает около 26 KiB, но verifier не предупреждает
  о приближении к tracked instruction budget.

### Already Delivered And Excluded
- Native Windows generated-copy bootstrap, refresh, verifier, Git safety,
  automated matrix и two-host clean-clone proof уже доставлены серией `040`.
- Maintenance consumer opt-in, first-run green scan, complete schema inventory и
  operations runbook доставлены серией `060` и карточкой `061`.
- Existing refuse-on-existing, dry-run, backup, ignore/public-safety и
  fail-closed verification contracts сохраняются.

## Product Decisions
- `--profile` получает поддержанные значения `generic`, `workspace-root` и
  `service`; legacy `--kind` остается backward-compatible alias на переходный
  период, unknown values fail closed.
- New public bootstrap default использует Codex policy `safe-interactive`:
  `approval_policy = "on-request"` и `sandbox_mode = "workspace-write"`.
  `trusted-automation` с `never`/`danger-full-access` требует explicit opt-in.
- Surface selection становится явной: `all-surfaces` сохраняется default для
  совместимости, `codex-only` делает Claude optional и legacy artifacts
  forbidden через tracked verification policy.
- POSIX independent-consumer default использует absolute symlink targets к
  resolved `--changerail-root`; relative mode доступен только через explicit
  `--wiring-path-mode relative` для одной переносимой workspace topology.
- Новый tracked consumer lock использует schema `changerail.consumer-lock.v1`,
  хранит public-safe ChangeRail version/revision, wiring backend/path mode и
  выбранные profiles. Enforcement бывает `advisory` или `strict`; CI требует
  exact strict revision.
- CI generation остается explicit opt-in. Workflow читает lock, checkout-ит
  exact ChangeRail revision в disposable path и запускает тот же consumer
  verification baseline; credentials для bootstrap не требуются.
- Existing-project configuration работает только в explicit idempotent mode и
  может управлять ChangeRail-owned wiring/auth handoff. Project-owned files не
  перезаписываются; commit, push и external publication не выполняются.
- README и Git initialization являются отдельными opt-ins. Bootstrap может
  выполнить `git init`, выбрать default branch и добавить remote, но никогда не
  делает commit или push.
- Runtime diagnostics являются opt-in evidence и отделены от static verifier.
  Raw output с local paths остается ignored; tracked/public summary redacted.
- Generated config явно задает instruction budget. Verifier предупреждает при
  достижении 85% и fail closed выше budget, с remediation для сокращения
  generated/shared и project-specific instructions.

## User Outcome
Оператор одной командой создает Codex-first consumer или multi-repository
workspace root, явно видит authority и wiring choices, а затем доказывает, что
тот же commit проходит verification из clean clone в другом supported layout и
в generated CI без ручного ремонта symlink-ов.

## Acceptance
- Profile, surface, Codex policy, wiring path mode и lock enforcement являются
  явными tracked choices с deterministic CLI validation.
- Default bootstrap больше не выдает `danger-full-access` неявно.
- Existing `--kind generic` и all-surfaces consumers имеют документированный
  compatibility path.
- POSIX clean-clone fixture переносит consumer в non-sibling checkout и проходит
  без ручного переписывания wiring.
- POSIX refresh/repair меняет только manifest-owned links и fail closed на
  project-owned divergence, scope/symlink escape или unrelated dirty state.
- Consumer lock не содержит absolute machine paths, credentials или private
  remote data; verifier различает valid wiring, source match и source drift.
- Strict lock mismatch блокирует CI, advisory mismatch остается видимой
  non-blocking diagnostic.
- Generated CI устанавливает exact declared ChangeRail revision и выполняет
  consumer baseline из clean clone.
- `generic`, `workspace-root` и `service` дают observable topology guidance без
  генерации domain-specific application structure.
- `codex-only` и `all-surfaces` проходят profile matrix; targeted OpenSpec
  validation нельзя ослабить profile-ом.
- Existing consumer получает idempotent auth-only configuration и POSIX wiring
  repair без чтения или печати credential contents.
- Missing auth diagnostic печатает существующий ChangeRail runbook path и
  готовую generic remediation command.
- Empty consumer может opt-in создать README и инициализировать Git с branch и
  remote; commit/push не выполняются.
- Opt-in runtime diagnostic фиксирует effective config/trust/MCP/instruction
  evidence отдельно от static PASS и redacts local paths в summary.
- Instruction budget warning/fail fixtures проверяют boundary и remediation.
- Windows generated-copy, maintenance opt-in, public-safety и release baseline
  не регрессируют.

## Constraints And Non-goals
- Не добавлять private consumer names, remotes, CI URLs, auth paths или raw
  runtime reports в tracked artifacts.
- Не копировать credentials и не создавать auth marker без explicit opt-in.
- Не выполнять commit, push, PR, publish или deployment из bootstrap/configure.
- Не менять native Windows generated-copy default и fallback proof contracts.
- Не утверждать runtime behavior только по static TOML parsing.
- Profiles описывают repository ownership topology и agent authority, но не
  генерируют domain-specific service/application code.
- Existing consumers без нового lock/profile metadata продолжают проверяться по
  legacy compatibility path.

## Change Set
1. `add-bootstrap-topology-and-permission-profiles`
2. `establish-portable-consumer-wiring-lock`
3. `add-pinned-consumer-ci-bootstrap`
4. `add-idempotent-post-bootstrap-configuration`
5. `add-consumer-runtime-and-instruction-budget-diagnostics`

## Verify
- `python3 scripts/smoke-bootstrap-project.py`
- `python3 scripts/smoke-verify-project.py`
- новый POSIX non-sibling clean-clone smoke
- новый profile/surface/authority matrix smoke
- новый consumer lock/drift и strict CI fixture
- новый configure/auth/Git/README no-mutation smoke
- новые runtime diagnostic redaction и instruction-budget boundary fixtures
- `python3 scripts/smoke-windows-matrix.py --json`
- `python3 scripts/run-release-baseline.py`
- `python3 scripts/public-surface-scan.py`
- `python3 scripts/public-surface-scan.py --history`
- `./bin/openspec validate --all --strict`
- `git diff --check`

## Planning Verification
- `./bin/openspec validate --all --strict` -> passed, 28/28 specs and active
  changes valid.
- Individual `./bin/openspec validate <change> --strict` -> passed for all five
  card-owned changes.
- `python3 scripts/run-release-baseline.py` -> passed, 31/31 steps.
- `python3 scripts/public-surface-scan.py` -> passed, 925 files, 0 findings.
- `python3 scripts/public-surface-scan.py --history` -> passed, 925 files,
  0 findings.
- `git diff --check` and explicit new-file trailing-whitespace scan -> passed.
- This evidence validates planning/public safety only; implementation tasks
  remain unchecked and must produce their own regression evidence during `do`.

## Delivery Verification
- RED: post-bootstrap smoke initially passed 21/22 and failed only the new
  configure/README/Git contract; после implementation прошел 22/22.
- RED: runtime/instruction smoke initially failed 0/2 and bootstrap снова
  зафиксировал 21/22; после implementation focused smoke прошел 2/2, а
  generated `AGENTS.md` занял 26890/32768 UTF-8 bytes, ниже 85%.
- `python3 scripts/smoke-verify-project.py` -> passed, 57/57.
- `python3 scripts/smoke-wiring-discovery.py` -> passed, 191/191.
- `python3 scripts/smoke-consumer-ci.py` -> passed, 4/4.
- `python3 scripts/run-release-baseline.py` -> passed, 33/33 steps; default
  verifier/CI не запускали Codex runtime diagnostics.
- `python3 scripts/public-surface-scan.py` и `--history` -> passed, 930 files,
  0 findings в каждом run.
- `./bin/openspec validate --all --strict`, pinned `ruff check bin scripts` и
  `git diff --check` -> passed.

## Archive
- `openspec/changes/archive/2026-08-10-add-bootstrap-topology-and-permission-profiles/`
- `openspec/changes/archive/2026-08-10-establish-portable-consumer-wiring-lock/`
- `openspec/changes/archive/2026-08-10-add-pinned-consumer-ci-bootstrap/`
- `openspec/changes/archive/2026-08-10-add-idempotent-post-bootstrap-configuration/`
- `openspec/changes/archive/2026-08-10-add-consumer-runtime-and-instruction-budget-diagnostics/`

## Related
- `bin/bootstrap-project`
- `bin/verify-project`
- `templates/project/`
- `scripts/smoke-bootstrap-project.py`
- `scripts/smoke-verify-project.py`
- `scripts/smoke-runtime-diagnostics.py`
- `docs/wiring-discovery.md`
- `docs/consumer-adoption-runbook.md`
- `docs/compatibility.md`
- `openspec/specs/changerail-project-bootstrap/spec.md`
- `openspec/specs/changerail-project-templates/spec.md`
- `openspec/specs/changerail-project-verification/spec.md`
- `openspec/specs/changerail-wiring-discovery/spec.md`

## Result
Все пять card-owned changes реализованы, проверены, синхронизированы с main
specs и архивированы. Greenfield bootstrap теперь имеет explicit profiles,
portable lock/wiring, strict consumer CI, bounded post-bootstrap configure,
README/Git opt-ins и отделенные static budget/runtime diagnostics. Independent
review cycle 2 вернул `go` без findings; карточка финализирована в `4.done`.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `add-bootstrap-topology-and-permission-profiles`

### Why
Текущий `--kind` не влияет на результат, а generic bootstrap неявно выдает
максимальную Codex authority.

### Goal
Добавить observable project/surface/Codex-policy profiles с безопасным default и
явным compatibility contract.

### Scope
- CLI profile and legacy alias mapping.
- `generic`, `workspace-root`, `service` template policy.
- `all-surfaces`, `codex-only` verification policy rendering.
- `safe-interactive`, `trusted-automation` Codex config rendering.

### Acceptance
- Default использует safe-interactive и all-surfaces.
- Trusted automation требует explicit selection.
- Unknown/incompatible combinations fail closed before target mutation.
- Profile matrix проходит bootstrap и verify smoke.

### Depends On
- none

### Related
- `openspec/changes/add-bootstrap-topology-and-permission-profiles/`

## Change 2: `establish-portable-consumer-wiring-lock`

### Why
POSIX relative links и отсутствие intended source metadata делают clean clone и
ChangeRail updates зависимыми от topology bootstrap-машины.

### Goal
Ввести portable POSIX path mode, public-safe consumer lock и idempotent
manifest-owned refresh/verification.

### Scope
- Absolute/relative POSIX path-mode contract.
- `changerail.consumer-lock.v1` schema and generated lock.
- Advisory/strict version and revision drift semantics.
- POSIX refresh/repair ownership and safety gates.
- Non-sibling clean-clone regression fixture.

### Acceptance
- Independent consumer default survives non-sibling clean clone.
- Lock contains no machine-local paths and validates through public schema.
- Verifier separates wiring validity from source drift.
- Repair refuses project-owned or unrelated dirty changes.

### Depends On
- `add-bootstrap-topology-and-permission-profiles`

### Related
- `openspec/changes/establish-portable-consumer-wiring-lock/`

## Change 3: `add-pinned-consumer-ci-bootstrap`

### Why
Consumer CI сейчас собирается вручную и не имеет machine-readable exact
ChangeRail revision contract.

### Goal
Генерировать explicit opt-in CI workflow, который воспроизводит strict locked
consumer baseline из clean clone.

### Scope
- CI template and bootstrap opt-in.
- Exact lock-driven ChangeRail checkout.
- Clean-clone bootstrap/verify baseline.
- CI smoke fixture without private credentials.

### Acceptance
- CI refuses absent, malformed, advisory or mismatched lock.
- Workflow uses exact revision and disposable installation path.
- Same verification command passes locally and in fixture CI.

### Depends On
- `establish-portable-consumer-wiring-lock`

### Related
- `openspec/changes/add-pinned-consumer-ci-bootstrap/`

## Change 4: `add-idempotent-post-bootstrap-configuration`

### Why
Auth setup, POSIX repair, README и Git handoff требуют ручных команд после
bootstrap, а повторный bootstrap небезопасен для живого project-owned content.

### Goal
Добавить bounded existing-project configure mode и explicit README/Git opt-ins
без commit, push или credential exposure.

### Scope
- Auth-only configure and actionable remediation.
- Manifest-owned POSIX repair handoff.
- Optional generated README.
- Optional `git init`, default branch and remote setup.

### Acceptance
- Repeated configure is idempotent.
- Project-owned files and unrelated dirty state remain untouched.
- Credential contents never enter output or tracked files.
- Git initialization never commits or pushes.

### Depends On
- `add-bootstrap-topology-and-permission-profiles`
- `establish-portable-consumer-wiring-lock`

### Related
- `openspec/changes/add-idempotent-post-bootstrap-configuration/`

## Change 5: `add-consumer-runtime-and-instruction-budget-diagnostics`

### Why
Static config validation не подтверждает effective Codex runtime, а растущий
embedded `AGENTS.md` может превысить instruction budget без раннего сигнала.

### Goal
Разделить static и opt-in runtime evidence и добавить deterministic
instruction-budget warning/fail gate.

### Scope
- Opt-in Codex runtime diagnostic with redacted summary.
- Effective config/trust/MCP/instruction evidence classification.
- Tracked `project_doc_max_bytes` budget and 85% warning.
- Over-budget fail and remediation guidance.

### Acceptance
- Static PASS не называется runtime proof.
- Unsupported/unavailable runtime probe дает explicit diagnostic, а не false
  success.
- Raw runtime output remains ignored and public summaries redact local paths.
- Warning/fail boundaries and remediation have deterministic smoke coverage.

### Depends On
- `add-bootstrap-topology-and-permission-profiles`

### Related
- `openspec/changes/add-consumer-runtime-and-instruction-budget-diagnostics/`

## Log
- 2026-08-05T14:14:56Z card created from sanitized greenfield consumer
  bootstrap, clean-clone CI and Codex setup review.
- 2026-08-09T17:56:40Z cross-card maintenance opt-in boundary зафиксирован для
  серии `060` без преждевременного выбора profile/path-mode решений.
- 2026-08-10T08:00:00Z карточка повторно исследована против текущего repository
  state; delivered Windows/maintenance scope исключен, пять implementation-sized
  changes и product decisions зафиксированы, owner назначен.
- 2026-08-10T08:00:01Z все пять change directories доведены до apply-ready
  status и прошли `openspec validate <change> --strict`; карточка перемещена в
  `2.todo` с handoff на `$chrl-do`.
- 2026-08-10T08:11:52Z planning gate завершен: release baseline 31/31,
  OpenSpec 28/28 и current/history public-surface scans green; implementation
  при этом не начиналась.
- 2026-08-10T11:19:21Z delivery завершен: пять changes реализованы и
  архивированы, release baseline 33/33, focused runtime 2/2, bootstrap 22/22,
verifier 57/57 и public-surface scans 930/0 green; карточка оставлена в
`3.inprogress` для независимого review.
- 2026-08-10T12:15:06Z independent review cycle 1 подтвердил все 16 acceptance
  criteria, но вернул `no-go` с одним scope blocker: manifest включал ранее
  выполненные переходы карточек `000`, `040`, `060` и `060-06`. Board cleanup
  отделен в самостоятельный commit `c7ed3ca`, manifest пересобран только по
  card-owned scope `050` и повторный scope-check прошел без расхождений.
- 2026-08-10T12:28:41Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
