---
name: changerail-pub
description: "Run the final ChangeRail publish loop for a reviewed board card: validate its risk-appropriate gate, confirm reviewed docs, create a scoped commit and push unless disabled."
---

# ChangeRail Pub

## Purpose

Finalize a delivered and risk-appropriately reviewed ChangeRail board card:

```text
$changerail-review <card-path>  # fresh-context go/no-go verdict
$changerail-pub <card-path>     # scoped commit and push
$changerail-pub <card-path> --resume-release  # resume pushed release payload
```

Normal `$changerail-pub` invocation is explicit permission to create a scoped
commit and push unless `--no-push` is supplied or project policy forbids
pushing. `--resume-release` authorizes only continuation of the already
reviewed and pushed release transaction; it does not authorize staging, a new
payload commit, another provider, credential type, execution target, wire
schema or mutation outside that transaction.

## Project Context

Resolve the repository root from the current working directory or
`CODEX_WORKDIR`. Read:

1. `openspec/config.yaml` if present.
2. `AGENTS.md`, `AGENTS.shared.md`, board docs and local workflow docs that
   affect docs, checks, commit style, branch policy or repo boundaries.
3. The target card and archived card-owned changes.
4. Existing docs likely affected by the implemented behavior.

## Inputs

Expected form:

```text
$changerail-pub <card-path>
```

Useful flags:

```text
$changerail-pub <card-path> --no-push
$changerail-pub <card-path> --message "type(scope): summary"
$changerail-pub <card-path> --docs-only
$changerail-pub <card-path> --allow-unarchived
$changerail-pub <card-path> --resume-release
```

Accept legacy prompt forms such as `/changerail:pub <card>`, `changerail:pub <card>` and
`changerail:ship <card>` as equivalent, but present Codex CLI instructions with
`$changerail-pub`.

## Entry Routing

Resolve the entry mode before the Review Gate or any working-tree scope check.
Without `--resume-release`, use the normal entry below. With
`--resume-release`, skip the entire Normal Entry Review Gate and Normal Entry
Workflow and use only Post-Commit Release Resume Entry.

Resume is incompatible with `--no-push`, `--message`, `--docs-only`,
`--allow-unarchived` or any option that stages, commits or broadens scope.
Unknown or conflicting flags stop before mutation. Resume is also forbidden
from a dirty or pre-commit state and never normalizes state through force,
rebase, reset, stash, replacement objects, a new commit or a clean-HEAD LLM
review.

## Operating Mode

- Work in the foreground.
- Never run `git add .`, `git commit -a`, force-push, reset or checkout
  commands that discard changes.
- Commit only files tied to the named card, archived changes, synced specs,
  docs, tests and board state.
- Stop if unrelated dirty files cannot be separated confidently.
- When `CHANGERAIL_PROGRESS_EVENT_PATH` is set, emit value-free publish progress
  with `bin/changerail-delivery-runner progress-event publish finalizing` before
  final verification/staging and `publish complete` after successful push or
  explicit `--no-push` publish metadata. Do not include prose, commands, paths,
  environment values or output excerpts in progress.

## Normal Entry Review Gate

Read `../changerail-review/references/changerail-review-verdict.md` before publishing.

At the start of publish, before documentation edits change the working tree,
rerun deterministic preflight without normalization:

```bash
bin/changerail-review-verdict preflight "<card-path>" --workspace . \
  --output ".runtime/changerail/review-preflights/<card-id>.json" --json
```

For an explicitly deterministic/process payload, fresh `machine-reviewed` is
the required payload gate and no LLM verdict exists. For ordinary or critical
risk, validate the verdict:

```bash
bin/changerail-review-verdict validate \
  ".runtime/changerail/reviews/<card-id>.json" --check-fresh --workspace . --json
```

For ordinary or critical risk, if the verdict is absent, stale, invalid or not `result: go`, stop before
staging. A verdict whose reviewed `workspace.tree_sha` is missing or differs
from the current publish tree is stale for review-gated publish and requires a
fresh review. This early admission is provisional: the same canonical preflight,
fresh verdict and working-tree scope gates run again after final verification
immediately before explicit staging. Never stage the verdict file.

If the project declares `.changerail/execution-target.json`, deterministic
preflight must also prove current declaration, manifest and retained evidence
have one exact matching target identity. Missing, multiple or mismatched target
identity blocks publish; do not stage or propose provider substitution.

## Normal Entry Workflow

### 1. Read Final State

Run:

```bash
git status --short
git branch --show-current
git remote -v
bin/openspec list --json
```

Read the target card, delivery manifest when present, and archived change
artifacts. Verify card-owned changes are archived unless `--allow-unarchived`
is present.

Build a publish scope from manifest `committable_paths`, archive paths, synced
specs, card state, docs and changed files. Exclude runtime paths and unrelated
active OpenSpec changes.

When a delivery manifest exists and the helper supports `scope-check`, compare
the manifest with the working tree before staging:

```bash
bin/changerail-delivery-manifest scope-check \
  ".runtime/changerail/delivery-manifests/<card-id>.json" \
  --target working-tree --json
```

Stop before staging if the result reports missing, extra or mismatched
committable paths.

### 2. Documentation Check

Confirm durable docs that changed user-facing commands, workflow, contracts or
setup are already part of the reviewed payload. Prefer existing docs. For
review-gated cards, do not make substantive code, docs, specs, schema, script
or test edits after a fresh `go` verdict; stop and send the card back through
delivery/review if such edits are required. If no docs need updates, record
that reason in the card or final summary.

### 3. Final Verification

Run:

```bash
git diff --check
bin/openspec validate --all --strict
```

Also run focused checks required by tasks, project config or affected code.
Rerun the complete project-declared verification suite immediately before final
publish (and separately before live admission when applicable); focused
re-review may reuse prior suite evidence only while its payload hash is
unchanged. Do not add a clean-HEAD LLM audit here unless this is the single
milestone explicitly declared by the card.
Do not commit while final verification is failing unless the operator
explicitly requests publishing a known failing state and the card records the
residual risk.

### 4. Commit

Review:

```bash
git status --short
git diff --stat
git diff --cached --stat
```

After final verification and the review above, immediately before any `git
add`, rerun the canonical deterministic preflight, fresh verdict validation and
working-tree scope gate on the unchanged bytes:

```bash
bin/changerail-review-verdict preflight "<card-path>" --workspace . \
  --output ".runtime/changerail/review-preflights/<card-id>.json" --json
bin/changerail-review-verdict validate \
  ".runtime/changerail/reviews/<card-id>.json" --check-fresh --workspace . --json
bin/changerail-delivery-manifest scope-check \
  ".runtime/changerail/delivery-manifests/<card-id>.json" \
  --target working-tree --json
```

Any same-path byte change after the early gate or during final verification
makes this final gate fail before staging, commit or push. Do not reuse the
early result. Stage explicit paths only after all three commands pass:

```bash
git add -- <path> ...
git diff --cached --stat
git diff --cached --check
bin/changerail-delivery-manifest scope-check \
  ".runtime/changerail/delivery-manifests/<card-id>.json" \
  --target staged --json
git commit -m "<message>"
```

If staged scope reconciliation reports any missing, extra or mismatched path,
unstage the incorrect explicit path set only after confirming it is safe, then
return to scope review. Never include unrelated staged paths in the commit.

Use `--message` when provided. Otherwise derive a concise message from the
card summary and local commit style.

### 5. Card Sync

After a successful payload commit, update the card with stable result, log
entry and the documented `4.done` board move when local board conventions
require it. Do not write the card's own exact final commit hash or mutable push
status into tracked card text; exact payload/published commit and push metadata
belongs in the ignored delivery manifest. This post-publish card metadata is
deterministic finalization, not a substantive change to the reviewed payload. If
this creates a new card-only diff before push, amend only the card with explicit
staging.

When the workspace provides `bin/changerail-delivery-manifest`, prefer
helper-assisted finalization through the shared Python runtime selector:

```bash
bin/changerail-delivery-manifest finalize-card "<card-path>" \
  --commit "<payload-commit>" --remote "<remote>" --branch "<branch>" \
  --push-status pending --timestamp "<utc>"
git add -- <old-card-path> <new-card-path>
git commit --amend --no-edit
```

This helper may only move/update board metadata: `Status`, `Owner`,
`OpenSpec Stage`, `Result`, `Next` and `Log`. If finalization would require
substantive code, docs, specs, schemas, scripts or tests changes, stop and send
the card back through delivery/review.

If the reviewed card acceptance explicitly requires a release tag, hosted
release or public assets, defer this entire card-sync step until the reviewed
release continuation below succeeds. Push the reviewed payload commit while
the card remains in `3.inprogress`; do not amend that commit after creating a
release tag. `--no-push` cannot complete an externally published release card.

### 6. Push

Skip only with `--no-push`.

```bash
git branch --show-current
git rev-parse --abbrev-ref --symbolic-full-name @{u}
git push
```

If no upstream exists and project policy permits it, use `git push -u origin
HEAD`. Never force-push.

When `--no-push` is supplied, do not claim remote publication readiness. After
the card-only amend, update the ignored manifest with skipped local-only publish
evidence when the helper exists:

```bash
bin/changerail-delivery-manifest publish-update \
  ".runtime/changerail/delivery-manifests/<card-id>.json" \
  --status skipped --payload-commit "<payload-commit>" \
  --published-commit "<local-final-commit>" \
  --reason "push skipped by --no-push" --mode local-only
```

After push, update ignored manifest publish metadata when the helper exists:

```bash
bin/changerail-delivery-manifest publish-update \
  ".runtime/changerail/delivery-manifests/<card-id>.json" \
  --status pushed --payload-commit "<payload-commit>" \
  --published-commit "<published-commit>" --remote "<remote>" \
  --branch "<branch>" --pushed-at "<utc>" --mode review-gated
```

Never stage the ignored manifest.

### 7. Normal Reviewed Release Continuation

Run this continuation only when all of the following are true:

- reviewed card acceptance explicitly names the tag, hosted release and asset
  contract;
- the operator invocation authorizes that external publication;
- the fresh review gate approved the exact payload and was validated with
  `--check-fresh` immediately before staging;
- the reviewed payload commit is reachable from the authorized remote branch.

Before mutation, derive the expected tag name, annotation, hosted-release
title/notes and exact asset basenames from reviewed tracked artifacts. Confirm
the remote URL is credential-free, publication credentials are available, and
read-only queries for both the remote tag and hosted release succeed. Absence
is the expected first-publication state. Exact reviewed identity MUST pin the
tag annotation, hosted-release title and tracked notes source. An existing
object may be accepted only as an idempotent resume when its target,
annotated-object type, annotation, title, exact notes body,
public/non-draft/non-prerelease state and every present asset match the reviewed
contract. Present asset basenames MUST be unique and a subset of the contracted
set; any unexpected, duplicate or byte-mismatched asset is a hard stop. Missing
contracted basenames may be resumed as described below. Stop without rewriting
anything when identity is unexpected or cannot be proved. Never force-update
or replace a tag, release or asset.

Perform the transaction in this order:

1. Use the pre-staging canonical freshness validation and complete project
   verification results. After commit, do not call the clean committed state
   fresh: instead require the payload commit parent to equal the verdict's
   recorded `head_commit`, require `git --no-replace-objects rev-parse
   <payload>^{tree}` to equal
   `verdict.workspace.tree_sha`, and confirm the current remote branch identity.
2. Create the annotated tag on the reviewed payload commit when absent, push
   only that tag without force, and prove through a fresh remote query that its
   dereferenced target is the payload commit.
3. Build assets into a new ignored output directory from the dereferenced tag
   commit. Run the tracked local checksum check and verify source revision,
   version, license and exact asset basenames.
4. If a hosted release already exists with matching tag/title/notes/state and
   only contracted unique asset names, download every present asset into a new
   ignored directory and compare its bytes with the locally built counterpart.
   Upload only contracted basenames proved absent. If the release is absent,
   create it from the pinned title and tracked notes source and upload all
   contracted assets. Never replace a present asset.
5. Query the hosted release read-only and require the exact tag, title, notes,
   state and complete contracted asset-name set with no duplicate/unexpected
   names. Download every contracted asset into a new ignored directory,
   compare downloaded bytes with the locally built assets, rerun the checksum
   check, and confirm remote branch/tag targets.

If any step fails, leave the card in `3.inprogress`, preserve the exact safe
handoff in ignored manifest/evidence, and stop. A partially completed but
identity-matching transaction may be resumed from its first missing step after
the same read-only checks; a mismatch is a hard safety stop.

Only after all release proofs pass, run helper-assisted card finalization from
section 5, explicitly stage only the old/new card paths, and create a separate
deterministic card-only commit instead of amending the tagged payload commit.
Push normally, prove the final branch commit read-only, and record both payload
and finalization commits in the ignored manifest. The immutable release tag
MUST continue to dereference to the reviewed payload commit.

## Post-Commit Release Resume Entry

Resume accepts only a clean exact payload commit already pushed to the
authorized feature branch. Before any tag, hosted-release or asset mutation:

Run the admission commands in this order and stop on any missing/mismatched
result. `refs/replace/` must be empty and the common Git directory must have no
non-empty `info/grafts`; these checks precede all lineage/source reads. All
commit identity, parent, tree and diff reads use raw-object semantics:

```bash
bin/changerail-review-verdict validate \
  ".runtime/changerail/reviews/<card-id>.json" --json
bin/changerail-delivery-manifest validate \
  ".runtime/changerail/delivery-manifests/<card-id>.json" --json
git status --porcelain
git for-each-ref --format='%(refname)' refs/replace/
git rev-parse --git-common-dir
git --no-replace-objects rev-list --parents -n 1 "<payload-commit>"
git --no-replace-objects rev-parse "<payload-commit>^{tree}"
bin/changerail-delivery-manifest scope-check \
  ".runtime/changerail/delivery-manifests/<card-id>.json" \
  --target committed --commit "<payload-commit>" --json
git ls-remote "<authorized-remote>" "refs/heads/<authorized-branch>"
```

Require positive verdict result and complete recorded head/tree, pushed
manifest payload/remote/branch identity, empty status, exactly one live
`3.inprogress` successor card in checkout and payload, one raw parent equal to
the verdict head, raw tree equal to the verdict tree, exact committed scope and
remote branch equality. The manifest helper and source-distribution builder
also reject replacement/graft state and disable replacement processing.

After admission, re-query every existing object and continue from the first
proved absent step: create/push an absent annotated `v1.0.0` tag with exact
annotation `ChangeRail 1.0.0`; build the three contracted assets in a fresh
ignored directory from the dereferenced tag; create an absent public
non-draft/non-prerelease release with title `ChangeRail 1.0.0` and the full
tracked `docs/releases/1.0.0.md` body; upload only proved absent unique asset
basenames; finally download and byte-compare the complete exact asset set.
Every present tag, release and asset must match its full reviewed identity
before the next mutation. Resume never replaces a present object or creates a
second payload commit.

Controlled interruption handoffs are deterministic:

| Observed state | First permitted absent step |
|---|---|
| After payload push | create and push the exact annotated tag |
| After tag creation | build exact assets and create the hosted release |
| After hosted release creation | upload the first absent contracted asset |
| After partial asset upload | upload remaining absent assets, then final proof |

On a safe interruption, retain ignored evidence and re-enter through the same
admission. Controlled negative fixtures are: Dirty or pre-commit; Invalid or
negative verdict; Wrong parent or tree; Committed scope mismatch; Wrong card
path or status; Divergent remote branch; replacement/graft state; unexpected
tag/release state; duplicate/unexpected asset; byte mismatch. Every case must
stop before mutation; staging, commit and push counters remain zero. Do not
substitute provider, credential, target or authority.

Only after the complete external identity proof succeeds may the existing
deterministic card-only finalization run. It remains a separate normal push;
the immutable tag continues to dereference to the reviewed payload commit.

## Safety Stops

Stop when:

- the risk-appropriate machine receipt or semantic review verdict is absent,
  stale, invalid or negative;
- declared execution target evidence is missing, mismatched or substituted;
- planned card-owned changes are not archived and `--allow-unarchived` is not
  present;
- final verification fails;
- staged files include unrelated work;
- commit identity is not configured;
- branch is detached, no allowed push target exists, or push is rejected;
- a release card lacks explicit operator mutation authority, publication
  credentials or a provably matching tag/release/asset identity;
- a required release proof fails or card finalization would precede it;
- a destructive git operation would be needed;
- the user asks to pause, review or change direction.

## Output

Summarize:

- card path;
- review gate result;
- docs updated or skipped;
- checks run and outcomes;
- commit hash and message;
- push target/result or `--no-push`;
- for a reviewed release continuation, tag object/target, hosted release URL,
  exact assets/checksums, downloaded proof and finalization commit;
- excluded runtime artifacts;
- unrelated dirty files left untouched.
