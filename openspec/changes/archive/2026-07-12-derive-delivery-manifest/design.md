# Design: derived delivery manifests

The helper will add a `derive` command:

```bash
python3 scripts/changerail_delivery_manifest.py derive <card-path> \
  --workspace . --write --json
```

The command will:

- resolve the card and derive `<card-id>` from its filename;
- parse `# title`, `## Status`, `## Change Set` and ordered `## Change N:`
  sections;
- classify referenced changes as `active`, `archived` or `planned`;
- read `git status --porcelain` for non-ignored changed paths;
- map status entries to manifest operations (`add`, `modify`, `delete`,
  `rename`, `unknown`);
- include excluded runtime paths for manifest, review verdict and review
  history;
- write `.runtime/changerail/delivery-manifests/<card-id>.json` when `--write`
  is supplied.

The derived manifest is still a reviewable proposal, not an authorization to
stage everything blindly. `changerail-pub` still validates scope before staging.
