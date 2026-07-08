# OPSX Delivery Manifest

For card-level OPSX runs, delivery records an ignored runtime manifest at:

```text
.runtime/opsx/delivery-manifests/<card-id>.json
```

The canonical schema id is:

```text
opsx.delivery-manifest.v1
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

## Handoff

`opsx-pub` uses the manifest as an initial staging proposal, not as proof.
Publish must still compare the manifest with `git status`, exclude runtime
paths and stop if pre-existing dirty state cannot be isolated.
