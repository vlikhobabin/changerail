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

Repository identity and endpoint diagnostics must be sanitized before runtime
write. Do not store raw URL userinfo, passwords, access tokens, sensitive query
values or private operator identity from remotes or connectivity URLs. Raw child
stdout/stderr logs, when retained, remain ignored runtime evidence and are not
public artifacts.

Record at minimum:

- `workspace.root` and repository identity when known;
- card id, path, title and status after moves;
- ordered planned changes with active or archive paths;
- `preexisting_dirty` from delivery-start `git status --short`;
- card-owned `committable_paths` for source, tests, docs, skills, schemas,
  specs, OpenSpec archives and board updates;
- publish ledger state including distinct reviewed `payload_commit` and final
  `published_commit` when publish has reached those points;
- `excluded_runtime_paths` for manifests, verdicts, raw logs, local evidence,
  temporary patches and runtime state.
- concise verification evidence summaries when useful, with command, observed
  outcome and runtime evidence path instead of raw logs.
- concise review and final card state summaries when copied from validated
  review/publish handoff evidence.

Each `committable_paths` entry may include `operation`:

- `add`: path is newly introduced;
- `modify`: path existed and changed;
- `delete`: path is removed and must still be staged;
- `rename`: path moved and both source and target must be staged;
- `unknown`: legacy or reconstructed entry whose operation must be re-checked.

For `delete`, record `source_path`. For `rename`, record both `source_path` and
`target_path`. `path` remains present for compatibility and should usually be
the target path for adds/modifies/renames and the source path for deletes.

Derived manifests must preserve exact repository-relative paths from
machine-readable git status output. Spaces, quotes, Unicode and literal ` -> `
text in filenames are valid path content, not parser delimiters. Untracked
directories must be represented as exact untracked file paths or rejected before
they become a staging proposal.

## Handoff

`changerail-pub` uses the manifest as an initial staging proposal, not as proof.
Publish must still compare the manifest with `git status`, exclude runtime
paths and stop if pre-existing dirty state cannot be isolated. When the helper
supports `scope-check`, delivery/review/publish can compare manifest scope with
Git state explicitly:

```bash
bin/changerail-delivery-manifest scope-check \
  .runtime/changerail/delivery-manifests/<card-id>.json \
  --target working-tree --json
bin/changerail-delivery-manifest scope-check \
  .runtime/changerail/delivery-manifests/<card-id>.json \
  --target staged --json
```

The JSON result reports `missing`, `extra` and `mismatched` path operations for
each target and must be treated as fail-closed before publish.

Review uses manifest evidence as audit input. It is acceptable to reference
ignored runtime evidence paths, including `bin/changerail-evidence` ids and
`.runtime/changerail/evidence/<scope>/index.json` paths, but do not place raw
command logs, secrets, credentials, customer data or local traces in the
manifest.

Use `handoff-update` for concise `verification_summary`, `review_summary` or
`final_card_state` updates when the helper provides it. Verification command
summaries may include structured `evidence` references with an id, index path
and raw output path. Raw command logs and review history remain separate ignored
runtime artifacts.

Tracked done-card text should contain only stable completion state. Exact final
commit hashes, mutable push status and timestamps are retained in this ignored
manifest ledger so card-only finalization cannot invalidate itself.

When publish records `status: pushed`, helper validation must fail closed unless
`payload_commit`, `published_commit`, `remote`, `branch` and `pushed_at` are all
present.

When publish is explicitly local-only with `--no-push`, the manifest publish
ledger must use `status: skipped`, `mode: local-only` and a reason such as
`push skipped by --no-push` instead of claiming remote publication readiness.
