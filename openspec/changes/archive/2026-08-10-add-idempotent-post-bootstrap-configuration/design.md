## Context

Initial bootstrap refuse-on-existing защищает project-owned files, но из-за
этого auth handoff и POSIX repair нельзя повторить штатной командой. README
намеренно исключен из generated outputs, а Git next steps остаются prose.

## Goals / Non-Goals

**Goals:**
- добавить bounded existing-project configure path;
- сделать auth/wiring remediation executable и idempotent;
- дать empty project explicit README/Git conveniences;
- сохранить no-publish и credential-redaction boundaries.

**Non-Goals:**
- merge или overwrite произвольных project-owned configs;
- автоматически создавать remote repository;
- commit, push, PR, publish или deployment;
- читать credential contents.

## Decisions

### Separate configure mode

`bin/bootstrap-project <path> --configure-existing` не запускает template
generation. Он принимает только allowlisted actions: `--link-codex-auth` и
`--refresh-wiring`/repair. Любые bootstrap-only flags в этом mode fail closed.

Repeated invocation считается success, если desired ignored auth symlink и
manifest-owned wiring уже совпадают. Real file at auth marker, project-owned
wiring path, parent scope escape или unrelated dirty state останавливают run.

### Actionable auth diagnostic

Verifier печатает generic command с фактическим ChangeRail helper path label и
ссылается на ChangeRail source runbook, а не на отсутствующий consumer-relative
doc. Output содержит marker name, но не source path или secret value.

### Optional README

`--with-readme` рендерит минимальный project README только если target path
отсутствует. Existing README никогда не заменяется. Template source становится
обычным `.tpl` artifact вместо исключенного documentation-only файла.

### Optional Git initialization

`--init-git` доступен для bootstrap target; `--default-branch` и `--remote`
требуют `--init-git`. Existing repository должен либо совпадать с requested
state, либо операция fail closed. Helper не выполняет add/commit/push.

## Risks / Trade-offs

- [Configure mode grows into migration engine] -> fixed allowlist и запрет
  template rendering удерживают boundary.
- [Remote URL may disclose private data in logs] -> output сообщает только
  remote name/status; public fixtures используют generic URL.
- [Git init partially succeeds] -> preflight validates options, rollback removes
  only repository metadata created by current run when safe.

## Migration Plan

1. Выделить action preflight/plan model.
2. Добавить configure actions и idempotency fixtures.
3. Добавить README/Git opt-ins и rollback/no-publish tests.
4. Обновить auth diagnostics и runbook.

## Open Questions

- none
