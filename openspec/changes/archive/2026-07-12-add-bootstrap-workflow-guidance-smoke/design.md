# Design: workflow guidance bootstrap smoke

`scripts/smoke-bootstrap-project.py` already creates a temporary generic
consumer under `.runtime` and runs `verify-project`. The new smoke can reuse
that generated project before cleanup and inspect:

- `AGENTS.md`;
- `openspec/board/README.md`.

The check should assert stable workflow tokens instead of brittle long prose:

- `explore -> ff -> do -> review -> pub`;
- `orchestrator`, `delivery worker`, or Russian equivalents where generated
  content is in Russian;
- fresh independent review or `fresh valid go`;
- `3.inprogress -> 4.done`.

Failures should identify the missing token and generated file.
