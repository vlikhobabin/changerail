## Context

`bootstrap-project` is the user-facing entry point for new standalone OPSX
consumer projects. It depends on tracked templates and `verify-project`.

## Command Shape

```text
bin/bootstrap-project <path> --name <project-name> --kind <project-kind>
bin/bootstrap-project <path> --name <project-name> --kind generic --dry-run
bin/bootstrap-project <path> --name <project-name> --kind generic --backup-existing
```

The default `--opsx-root` is the parent of the wrapper's `bin/` directory.

## Flow

1. Resolve and validate target path.
2. Refuse existing non-empty targets unless `--backup-existing` is supplied.
3. In dry-run mode, print planned operations and do not write files.
4. Create directories for agent wiring, `bin` and OpenSpec.
5. Render `*.tpl` templates with placeholder values.
6. Copy the OpenSpec skeleton.
7. Create symlink-и for Claude commands/skills, Codex skill directories and
   helper wrappers.
8. Run `bin/verify-project <target>`.
9. Print next steps: `git init`, first commit and remote setup.

## Backup Behavior

`--backup-existing` moves an existing target to a sibling timestamped
`<name>.backup-YYYYMMDDTHHMMSSZ` path before creating the new project. The
backup path is printed. The command fails if the backup target already exists.

## Smoke

`scripts/smoke-bootstrap-project.py` creates a project under
`.runtime/opsx/bootstrap-smoke/<run-id>/example-project`, runs bootstrap,
verifies the generated project, checks `--dry-run` leaves no target and checks
the refuse-on-existing failure path. The script prints the runtime report path
and exits non-zero on any failed check.

## Public Safety

Smoke output stays ignored. Public docs use only `/opt/opsx` and
`/opt/example-project`.
