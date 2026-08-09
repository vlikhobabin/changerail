# Codex Scheduled Maintenance Audit Example

Use a scheduled task to run read-only audit against an isolated checkout:

```bash
cd /opt/example-project
./bin/changerail-maintenance-runner scan --timeout 900 --json
```

Preferred setup:

- Use an isolated worktree or clone for recurring audit.
- Keep `.runtime/changerail/maintenance/` ignored and upload or inspect it as
  runtime evidence.
- Do not grant commit, push, issue-comment or pull-request authority to a
  read-only audit task.

Local active-checkout mode is useful for manual diagnostics, but a scheduled
run can observe uncommitted operator work in that checkout. Use an isolated
worktree when that risk matters.
