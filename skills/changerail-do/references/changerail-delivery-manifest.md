# ChangeRail Delivery Manifest

For card-level ChangeRail runs, delivery records an ignored runtime manifest at:

```text
.runtime/changerail/delivery-manifests/<card-id>.json
```

The canonical schema id is:

```text
changerail.delivery-manifest.v1
```

Use the board card filename without `.md` as `<card-id>`.

## Contents

Store repository-relative paths only. Do not record secrets, credentials,
customer data, full source payloads or large command output.

Record at minimum:

- `workspace.root` and repository identity when known;
- card id, path, title and status after moves;
- ordered planned changes with active or archive paths;
- `preexisting_dirty` from delivery-start `git status --short`;
- card-owned `committable_paths` for source, tests, docs, skills, schemas,
  specs, OpenSpec archives and board updates;
- `excluded_runtime_paths` for manifests, verdicts, raw logs, local evidence,
  temporary patches and runtime state.
- concise verification evidence summaries when useful, with command, observed
  outcome and runtime evidence path instead of raw logs.

Each `committable_paths` entry may include `operation`:

- `add`: path is newly introduced;
- `modify`: path existed and changed;
- `delete`: path is removed and must still be staged;
- `rename`: path moved and both source and target must be staged;
- `unknown`: legacy or reconstructed entry whose operation must be re-checked.

For `delete`, record `source_path`. For `rename`, record both `source_path` and
`target_path`. `path` remains present for compatibility and should usually be
the target path for adds/modifies/renames and the source path for deletes.

## Handoff

`changerail-pub` uses the manifest as an initial staging proposal, not as proof.
Publish must still compare the manifest with `git status`, exclude runtime
paths and stop if pre-existing dirty state cannot be isolated.

Review uses manifest evidence as audit input. It is acceptable to reference
ignored runtime evidence paths, but do not place raw command logs, secrets,
credentials, customer data or local traces in the manifest.
