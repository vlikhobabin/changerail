# Design: review and publish finalization automation

The implementation will keep runtime orchestration compatible with current
agent surfaces:

- `changerail-deliver` gets an explicit fresh reviewer prompt template that
  includes scope, forbidden writes, verdict path and required validation.
- `changerail-pub` gets a deterministic finalization sequence that can be
  executed by the active session after the reviewed payload commit.
- The delivery manifest helper gets a small `publish-update` command for
  ignored manifest state and a `finalize-card` command for deterministic board
  metadata updates.

The helper does not make substantive docs/spec/code edits after a fresh `go`.
It only updates board metadata and ignored runtime manifest state.
