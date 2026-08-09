# Усилить greenfield bootstrap потребителя: переносимость, CI и профили

## Status
1.backlog

## Owner
unassigned

## OpenSpec Stage
story

## Series
- none

## Series Index
- none

## Source
- Sanitized operator evidence от 2026-08-05: создание нового product workspace
  через `bin/bootstrap-project`, настройка root Git/Codex/ChangeRail,
  публикация и первый clean-clone CI run.
- Аудит `bin/bootstrap-project`, `bin/verify-project`, `templates/project/`,
  `docs/wiring-discovery.md` и consumer adoption docs.

## Summary
Довести ChangeRail greenfield consumer bootstrap от качественного генератора
локального skeleton до воспроизводимого end-to-end пути:

```text
bootstrap
  -> Git repository
  -> trusted Codex profile
  -> auth-ready delivery runner
  -> clean clone
  -> pinned ChangeRail wiring
  -> green consumer CI
```

Текущий bootstrap безопасно создает проект и дает сильный статический verifier,
но оставляет оператору существенную ручную сборку README, Git, CI, version pin,
workspace topology и post-bootstrap auth. POSIX wiring также зависит от
исходной относительной топологии каталогов, хотя публичные документы описывают
`/opt/changerail` как contract path.

## User Outcome
Оператор может одной явной командой создать новый Codex-first consumer или
multi-repository workspace root, выбрать безопасный/automation profile,
получить документированный Git/CI handoff и доказать, что тот же commit работает
из clean clone в произвольном runner path без ручного исследования symlink-ов.

## What Already Works Well
- Bootstrap refuse-on-existing, `--dry-run`, backup и post-generation verifier
  дают безопасную базовую операцию.
- Generated OpenSpec board, shared methodology, Codex/Claude skills и helper
  wiring согласованы и обнаруживаются локально.
- `verify-project` дает понятный red/green итог, проверяет MCP pins, OpenSpec,
  runtime/auth ignore policy и stale legacy wiring.
- Opt-in `--link-codex-auth` не копирует credential contents и verifier не
  допускает tracked auth state.

Эти свойства должны сохраниться; карточка не предлагает ослаблять fail-closed
проверки или автоматически публиковать новый repository.

## Observations And Evidence

### 1. POSIX symlink wiring не соответствует документированному contract path

- `create_symlink()` безусловно записывает target через `os.path.relpath()`.
- При bootstrap `/opt/example-project` из `/opt/changerail` tracked helper link
  получает форму вроде `../../changerail/bin/openspec`.
- `docs/wiring-discovery.md` описывает consumer links как
  `/opt/changerail/...`, а архитектурный документ рекомендует абсолютный
  `/opt/changerail` для consumers и относительные links только внутри одного
  workspace tree.
- В clean CI clone, расположенном глубже исходного `/opt` layout, link оказался
  broken, когда ChangeRail был корректно установлен в `/opt/changerail`.
  Первый consumer baseline run остановился на `bin/openspec: No such file or
  directory`; временный workaround потребовал клонировать ChangeRail как
  sibling конкретного CI checkout.

Вывод: portable tracked config (`.`) не означает portable wiring; repository
сохраняет неявную относительную топологию bootstrap-машины.

### 2. Нет consumer CI template и version/wiring lock

- Bootstrap не создает готовый consumer CI gate.
- Symlink consumers следуют текущему checkout ChangeRail, поэтому обновление
  `/opt/changerail` может изменить поведение всех consumers без изменения их
  Git payload.
- Для первого CI пришлось вручную выбрать ChangeRail commit, способ установки,
  Python runtime dependency и Node setup.
- Consumer не хранит machine-readable expected ChangeRail version/commit,
  backend и path mode; verifier может подтвердить текущий wiring, но не
  intended release baseline.

### 3. `--kind` является label, а не bootstrap profile

- Значение `--kind` рендерится в документы, но не выбирает структуру или policy.
- Workspace root с будущими независимыми child repositories требует иных
  boundaries, `.gitignore`, catalog и board guidance, чем deployable service.
- Codex-first запрос все равно получает обязательные Claude и legacy MCP
  surfaces через default `all-surfaces` profile.

### 4. Generic Codex template сразу выбирает максимальные полномочия

- Generated `.codex/config.toml` использует `approval_policy = "never"` и
  `sandbox_mode = "danger-full-access"` для любого нового consumer.
- Такой профиль удобен для trusted unattended delivery, но слишком широк как
  неявный default публичного generic bootstrap.
- Интерактивная разработка и automation runner имеют разные risk/approval
  requirements и должны выбираться явно.

### 5. Post-bootstrap auth и POSIX refresh неудобны

- `--link-codex-auth` доступен только при первоначальном bootstrap.
- `--refresh-wiring` сначала требует generated-copy manifest и поддерживает
  только generated-copy backend; POSIX symlink consumer не может использовать
  команду для repair/refresh.
- Auth advisory сообщает относительный путь
  `docs/consumer-adoption-runbook.md#codex-auth-for-delivery-runner`, которого
  нет в consumer repository, и не печатает готовую безопасную remediation
  command.
- В реальном greenfield flow auth readiness пришлось завершать отдельной
  ручной symlink-командой после bootstrap.

### 6. Empty-project README и Git handoff остаются ручными

- `templates/project/README.md` является документацией template source и
  намеренно исключается из generated outputs.
- Bootstrap печатает `git init`, `git add`, commit и remote как текстовые next
  steps, но не предлагает opt-in flags для безопасной автоматизации.
- Для пустого greenfield target полезен минимальный generated README; для Git
  нужны opt-in `init/default branch/remote`, но commit и push должны оставаться
  отдельным явным operator action.

### 7. Static verifier не доказывает effective Codex runtime config

- `verify-project` правильно проверяет синтаксис, trust entry и filesystem
  scope в tracked `.codex/config.toml`.
- В observed session `codex mcp list` показывал глобальный filesystem scope,
  тогда как `codex debug prompt-input` загружал project AGENTS/skills.
- Это не считается доказанным runtime bug: различие может зависеть от trust,
  Codex subcommand semantics или managed policy. Однако текущий PASS verifier
  нельзя интерпретировать как доказательство effective MCP/runtime profile.

### 8. Embedded shared methodology близка к default Codex size budget

- `AGENTS.shared.md` занимает около 23 KB, а базовый generated template вместе
  с shared block — около 26 KB.
- Representative customized consumer достиг 29,364 bytes, то есть близко к
  стандартному 32 KiB instruction discovery budget.
- Project-specific rules могут быть тихо усечены после дальнейшего роста shared
  methodology, если verifier не контролирует размер.

## Recommended Product Decisions

1. Разделить `config portability` и `wiring portability` как два явных
   контракта.
2. Для POSIX ввести `--wiring-path-mode absolute|relative`; default должен
   совпадать с публично документированным contract path. Рекомендуемый вариант:
   absolute resolved `--changerail-root` для independent consumers, relative
   mode только по explicit opt-in для одного переносимого workspace tree.
3. Генерировать public-safe lock с ChangeRail version, Git commit, backend и
   path mode; verifier должен отдельно показывать compatible/current/drifted.
4. Поставлять опциональный consumer CI template, который читает lock, создает
   заявленную topology и запускает тот же `verify-project` из clean clone.
5. Сделать `--kind` настоящим preset или заменить на `--profile`:
   `generic`, `workspace-root`, `service` с явным `--surfaces`.
6. Разделить Codex policy profiles минимум на `safe-interactive` и
   `trusted-automation`; максимальные полномочия не должны выбираться
   неявно для generic consumer.
7. Добавить idempotent post-bootstrap configure/repair surface для auth и
   POSIX symlink wiring без backup/overwrite project-owned files.
8. Добавить optional README/Git initialization flags, но не выполнять commit
   или push без отдельного operator action.
9. Отделить static verifier от opt-in effective Codex runtime diagnostic и
   документировать trust prerequisite и supported runtime probe.
10. Ввести AGENTS size warning/fail threshold с объяснением remediation:
    сократить shared block, вынести детали в skills/docs или осознанно увеличить
    `project_doc_max_bytes`.

## Acceptance
- POSIX consumer, созданный в одном filesystem layout, проходит bootstrap и
  verify после commit/clean clone в другом, документированно поддерживаемом
  layout без ручного переписывания symlink-ов.
- Документация, bootstrap implementation и smoke fixtures используют один
  contract для absolute/relative POSIX wiring.
- Новый clean-clone POSIX smoke воспроизводит старый broken-link scenario и
  становится зеленым после исправления.
- Consumer может получить tracked ChangeRail lock и generated CI workflow;
  clean CI устанавливает declared ChangeRail revision и выполняет полный
  consumer baseline.
- `verify-project` различает wiring validity и version drift, печатая
  actionable remediation без утечки local/private paths.
- Bootstrap поддерживает явные `generic`, `workspace-root` и `service`
  semantics либо документация честно ограничивает поддерживаемые presets.
- Оператор может выбрать Codex-only или all-surfaces setup; verifier следует
  выбранной tracked policy.
- Safe interactive и trusted automation Codex profiles имеют документированные
  permissions и проверяемый explicit selection.
- Существующий consumer может безопасно выполнить auth-only configuration и
  POSIX wiring repair; команды не читают и не печатают credential contents.
- Auth diagnostic указывает реальный ChangeRail runbook и готовую generic
  remediation command.
- Empty consumer может opt-in создать минимальный README и инициализировать Git
  с заданной default branch/remote; commit и push не выполняются автоматически.
- Optional runtime Codex diagnostic явно маркируется как runtime evidence и не
  подменяется статической config-проверкой.
- Verifier предупреждает до достижения default AGENTS instruction budget и
  содержит проверяемую remediation guidance.
- Existing Windows generated-copy default, fail-closed manifest ownership,
  public-safety scan и current release baseline не регрессируют.

## Constraints And Non-goals
- Не коммитить consumer names, remotes, CI URLs, auth paths или raw logs из
  operator evidence; fixtures используют только `/opt/example-project` и
  disposable generic paths.
- Не создавать и не копировать auth автоматически без explicit opt-in.
- Не выполнять consumer commit/push из default bootstrap.
- Не ослаблять Windows generated-copy, junction/symlink proof или Git-safety
  contracts.
- Не утверждать effective Codex behavior только по `codex mcp list`, пока не
  выбран и не проверен supported runtime probe contract.
- Не превращать ChangeRail core в domain-specific workspace generator;
  presets описывают repository ownership topology, а не предметную область.

## Proposed Decomposition

Предварительный план для triage/`$changerail-ff`; названия changes не являются
созданными OpenSpec artifacts.

1. `make-posix-consumer-wiring-clone-portable`
   - согласовать absolute/relative contract;
   - добавить path mode и POSIX repair/refresh;
   - добавить clean-clone/non-sibling regression smoke;
   - синхронизировать wiring/architecture/migration docs.
2. `add-consumer-lock-and-ci-bootstrap`
   - определить lock schema и version drift semantics;
   - генерировать opt-in consumer CI;
   - проверять pinned clean-clone baseline;
   - документировать update flow.
3. `add-bootstrap-workspace-and-permission-profiles`
   - сделать `kind/profile` observable;
   - добавить `workspace-root`, `service` и surface selection;
   - разделить safe interactive/trusted automation permissions;
   - сохранить явную backward-compatibility policy.
4. `harden-post-bootstrap-ux-and-runtime-diagnostics`
   - auth-only configure и actionable verifier output;
   - optional README/Git initialization;
   - effective Codex runtime diagnostic contract;
   - AGENTS size budget и guidance.

Предварительные зависимости: change 2 зависит от wiring contract change 1;
changes 3 и 4 могут проектироваться параллельно после принятия compatibility
policy, но final docs/release baseline объединяются после всех четырех.

## Triage Decisions
- Выбрать default POSIX path mode: absolute contract root или documented
  sibling-relative topology.
- Решить, является ли lock strict pin, compatibility range или advisory drift
  record для local development.
- Определить backward compatibility для текущего `all-surfaces` и
  `danger-full-access` bootstrap default.
- Решить, какие workspace/service artifacts входят в generic ChangeRail core,
  а какие остаются consumer-owned examples.
- Выбрать стабильный Codex runtime probe, который можно безопасно запускать
  локально и в CI после trust establishment.
- Установить warning/fail budgets для generated AGENTS с учетом Codex и Claude.

## Cross-card Decisions For Series 060
- `060-04` может добавить maintenance wiring как explicit additive
  `--with-maintenance` opt-in. Этот флаг ортогонален текущим `--kind`, surface
  policy и wiring backend и не считается реализацией будущих profile presets.
- Existing consumers и bootstrap без `--with-maintenance` не получают новые
  config/helper artifacts и остаются обратно совместимыми.
- `verify-project` определяет maintenance opt-in по наличию любого известного
  tracked maintenance artifact и требует полный schema/config/helper/ignore
  contract только в этом случае.
- Windows generated-copy manifest может владеть opted-in maintenance helper
  copies; POSIX и native Windows entrypoints используют уже существующие wiring
  backend contracts.
- Threshold, remediation guidance и structured producer для generated AGENTS
  instruction budget остаются в scope этой карточки `050`. `060-04` не вводит
  временный competing threshold, а `060-05` импортирует метрику только после
  появления стабильного producer contract.

## Change Set
- none yet

## Verify
- not started
- Planned focused checks:
  - `python3 scripts/smoke-bootstrap-project.py`
  - `python3 scripts/smoke-verify-project.py`
  - новый POSIX clean-clone consumer smoke в unrelated checkout topology
  - generated consumer CI fixture against declared lock
  - auth configure/repair smoke без credential output
  - profile/surface matrix smoke
  - AGENTS byte-budget boundary fixtures
  - `python3 scripts/run-release-baseline.py`
  - `python3 scripts/public-surface-scan.py`
  - `python3 scripts/public-surface-scan.py --history`
  - `git diff --check`

## Archive
- not started

## Related
- `bin/bootstrap-project`
- `bin/verify-project`
- `templates/project/`
- `scripts/smoke-bootstrap-project.py`
- `scripts/smoke-verify-project.py`
- `scripts/smoke-wiring-discovery.py`
- `docs/wiring-discovery.md`
- `docs/consumer-adoption-runbook.md`
- `docs/changerail-source-of-truth-architecture.md`
- `docs/migration-guide.md`
- `docs/compatibility.md`
- `openspec/board/4.done/02-bootstrap-and-templates.md`

## Result
not started

## Next
- Провести triage решений выше, назначить owner и подтвердить scope.
- После принятия scope запустить
  `$changerail-ff openspec/board/1.backlog/050-harden-greenfield-consumer-bootstrap.md`.

## Log
- 2026-08-05T14:14:56Z card created from sanitized greenfield consumer
  bootstrap, clean-clone CI and Codex setup review.
- 2026-08-09T17:56:40Z зафиксированы только cross-card решения, необходимые
  для `060-04`: additive maintenance opt-in разрешен без преждевременного
  выбора profile/path-mode/instruction-budget решений этой карточки.
