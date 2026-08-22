# {{PROJECT_NAME}}

ChangeRail bootstrap profile: `{{PROJECT_PROFILE}}`.

Verify the project from the repository root:

```bash
bin/verify-project .
bin/openspec validate --all --strict
```

If the project uses specialized source formats, review source classification
profiles explicitly:

```bash
bin/changerail-source-classification detect --json
bin/changerail-source-classification materialize --profile <id>@<version> --json
bin/changerail-source-classification check --json
```
