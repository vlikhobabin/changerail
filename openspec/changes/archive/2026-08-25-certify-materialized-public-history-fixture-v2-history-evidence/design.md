## Context

The unpublished source card
`materialize-public-history-benchmark-fixture-v2` exhausted its only
card-owned reachable-history capture. Evidence id `public-history-final`
started after its tracked payload was finalized, timed out after `300.119`
seconds under the declared 300-second limit, produced zero output bytes and has
no exit code. It remains authentic timeout evidence and cannot be converted to
PASS or replaced inside that source lineage.

The repaired source payload is identified by:

- published base commit
  `f6b56f11593e56fddbd6a718f6abe5418ade9129`;
- source review diff fingerprint
  `sha256:ac7a7dad192e227a734f7ef715f8e57b1369f21a54b890e1bbf323c27ebcf88d`;
- review tree `d83870bb9de7d5bbaea1a1b6b9bdc6e62ac5549a`;
- fixture fingerprint
  `sha256:59f686b634dd16a443894995e6a05c6630688263f3335b24c3c116fdf5e0d128`;
- SHA-256 of exact `authority.json` bytes
  `6b02ffd9f6af7f4d18afb18ff11a34ac88add48bba41b66e5cc990725a0bbe79`.

This change supplies a separate certification lineage. It changes only public
documentation and evidence policy; ignored evidence and manifest records carry
the actual outcome. It does not create a new wire schema.

## Goals / Non-Goals

**Goals:**

- predeclare one outcome-independent reachable-history capture with a
  1200-second timeout;
- bind it to the exact source fingerprint and all seven authority path hashes
  before and after execution;
- define a complete JSON, exit-status and findings oracle;
- make PASS, FAIL, TIMEOUT and malformed/incomplete evidence terminal with no
  retry;
- permit only a one-way, review-only continuation of the unchanged source after
  a remote-reachable certification PASS;
- route the certification through `critical` final-certification review by a
  fresh Sol reviewer at `xhigh`, without a milestone audit or rescue budget.

**Non-Goals:**

- editing, copying, staging, committing or publishing any source-card file;
- changing the fixture, scanner, test, schema, skill, command or runtime code;
- running a candidate benchmark, performance warmup/sample/CV selection, full
  release baseline or any additional reachable-history scan during FF;
- treating the prior 300-second timeout or an ad hoc diagnostic command as
  successful certification;
- reviewing or publishing the certification policy before its governed capture
  has produced terminal evidence.

## Decisions

### 1. Certification is a separate one-shot lineage

The canonical capture id is `public-history-certification`. Before starting the
command, delivery must prove that this id has no existing attempt or retained
entry in the certification lineage. The configured timeout is exactly `1200`
seconds. The earlier authentic duration `627.163` seconds is used only to set
that limit; it is not a sample, oracle, success claim or permission to retry.

The source `public-history-final` entry is retained separately with
`status: timeout`, `exit_code: null`, `timed_out: true`, its empty output and
300-second policy. Neither entry replaces or mutates the other.

Alternative rejected: extend the source timeout and rerun its evidence id.
That lineage already exposed a terminal outcome, so a second attempt would
select evidence after observing the first result.

### 2. Policy is finalized and precommitted, but not pre-reviewed

Before capture, DO must finalize the tracked board/OpenSpec/spec policy bytes,
sync and archive the change, move the card to its review-pending state and
record their exact review fingerprint in the ignored manifest. The policy text
must already declare the source identities, command, timeout, terminal outcome
rules and no-retry rule. No outcome-dependent policy edit is allowed after the
command starts.

This is a precommitment to fixed tracked policy, not a claim that the policy is
already reviewed, published or remote-reachable. The fresh final-certification
review happens only after terminal capture evidence exists; publish happens
only after that review returns GO. Lifecycle-only finalization may not rewrite
the evidence oracle or source binding.

Alternative rejected: review or publish the policy first and later attach the
capture. That creates circular evidence because the final review could not have
audited the capture it is said to certify.

### 3. Exact source bytes are checked on both sides of the capture

Immediately before and immediately after the command, retain the exact source
review fingerprint, fixture fingerprint, authority digest and SHA-256 for these
seven paths:

| Path | Required SHA-256 |
| --- | --- |
| `schemas/changerail-public-history-fixture-recipe-v2.schema.json` | `ab9eddbfbf55ff533bea70110828739996e6c71786e762ad1131dc2dc3f1ea3c` |
| `fixtures/public-history-v2/recipe.json` | `8fe4ad9ef10001af374236f4211d41db99427bf98ece24a67b2fa06240bf0fab` |
| `fixtures/public-history-v2/materialize.py` | `c19b740af5c96a4c1a7c5508038006991cd79f040a4b5149129d2ed034c7826c` |
| `fixtures/public-history-v2/realization.jsonl` | `f912b237cfdec3d5112979e6f6df043b943953df6bc0c6f084f4fc680b838c39` |
| `fixtures/public-history-v2/benchmark.py` | `d4db8ecfea59bc8840908c842ec8a31b974b0e2c264232f5b904da02718c20ac` |
| `fixtures/public-history-v2/selftest.py` | `73863351d2b1753265eb3449171087244d05d9a7c2ba0517b054e77e24eef9a4` |
| `fixtures/public-history-v2/authority.json` | `6b02ffd9f6af7f4d18afb18ff11a34ac88add48bba41b66e5cc990725a0bbe79` |

All fourteen before/after path hashes must equal the table, both source review
fingerprints must equal
`sha256:ac7a7dad192e227a734f7ef715f8e57b1369f21a54b890e1bbf323c27ebcf88d`,
both fixture fingerprints must equal
`sha256:59f686b634dd16a443894995e6a05c6630688263f3335b24c3c116fdf5e0d128`,
and both authority digests must equal
`6b02ffd9f6af7f4d18afb18ff11a34ac88add48bba41b66e5cc990725a0bbe79`.
Any absence, mismatch or between-check drift is a terminal FAIL and forbids
source continuation. Certification never edits or copies these paths.

### 4. The capture has one exact command and a closed PASS oracle

The retained evidence entry uses `changerail.evidence-index.v1`, id
`public-history-certification`, timeout `1200` and executes in the exact source
worktree:

```text
python3 scripts/public-surface-scan.py --history --json
```

The evidence index, raw stdout/stderr and certification manifest remain under
the ignored certification workspace runtime root. The source worktree is the
read-only command cwd and receives no tracked file, evidence index, output,
cache or other runtime write.

PASS requires all of the following from that single attempt:

- completion before timeout with `exit_code: 0` and `timed_out: false`;
- stdout containing one complete JSON document with schema
  `changerail.public-surface-scan.v1` and `history: true`;
- `summary.status: pass`, `summary.findings: 0` and `findings: []`;
- no truncation, decode error, schema inconsistency or hidden second result;
- exact matching before/after source and authority identities from Decision 3.

An exit of `1` with a complete fail report is terminal FAIL. Any other nonzero
exit, malformed/incomplete output, timeout, launch failure, identity drift or
oracle inconsistency is terminal FAIL or TIMEOUT as observed and never becomes
PASS. The evidence index and ignored delivery manifest retain argv, capture id,
configured timeout, start/end/duration, status, exit code, timed-out flag, raw
stdout/stderr references, output digest/byte count, parsed schema and findings
count. Raw output remains ignored and is not copied into tracked artifacts.

### 5. Outcomes never authorize retry or evidence promotion

PASS, FAIL and TIMEOUT all consume the sole attempt. A casual scan, preflight
current-only scan, prior historical duration or later diagnostic cannot be
renamed, copied, upserted or promoted to `public-history-certification`.
Benchmark warmups, samples, CV replacement and favorable-set selection are not
applicable to this deterministic public-safety gate.

If capture is not PASS, the certification and source cards remain
non-publishable and there is no repair, rescue or rerun within this card:
limit/used/remaining is `0/0/0`, exhausted `true`.

### 6. PASS creates only a one-way review handoff

After capture PASS, the certification payload receives one fresh independent
Sol/`xhigh` final-certification review. With GO it may be published. Only after
the certification is remote-reachable may the unchanged original source
payload receive exactly one fresh cycle-2 Sol/`xhigh` review using the
certification as external retained evidence. The certification card points to
the source; no reciprocal tracked link or other source-card edit is permitted.

The source continuation runs no new source scan and permits no implementation
fix. Source cycle-2 GO may proceed to its own publish workflow; any source
NO-GO is terminal with no same-card repair.

### 7. FF remains planning-only

FF creates only the card and one apply-ready documentation/evidence-policy
change. It does not create ignored capture state and does not run reachable
history, fixture materialization, benchmark, candidate verification, full
baseline, review, archive, commit or push.

## Risks / Trade-offs

- **1200 seconds can still be insufficient.** The one-shot outcome is TIMEOUT;
  mitigation is terminal failure and a separately authorized future decision,
  not an in-card retry.
- **The source can drift during the long command.** Exact pre/post fingerprint
  and seven-path hashes fail closed even if scanner output itself says pass.
- **A complete report can disagree with its exit status.** PASS requires both
  the schema-valid report and exit 0; all inconsistencies fail closed.
- **A predeclared policy could be mistaken for prior certification.** Tracked
  prose explicitly distinguishes finalized precommitment from later independent
  review and publication.
- **Separate worktrees complicate evidence location.** The ignored manifest
  records source identity and evidence references; no machine-specific source
  path is added to tracked public artifacts.

## Migration Plan

1. DO finalizes and precommits all tracked policy artifacts, syncs/archives the
   delta and prepares ignored manifest/evidence locations without executing the
   history command.
2. DO verifies the absent capture id and exact pre-capture source identities,
   executes the sole capture with timeout 1200, then records post-capture
   identities and terminal outcome without changing policy.
3. On PASS only, run deterministic preflight and one fresh critical
   Sol/`xhigh` certification review, then publish the certification.
4. After remote reachability, hand the unchanged source to exactly one fresh
   cycle-2 Sol/`xhigh` review; GO may publish and NO-GO ends the source lineage.

Rollback is not applicable to terminal evidence. A non-PASS capture remains
retained and cannot be deleted or retried by this card.

## Open Questions

None. Capture identity, timeout, source bytes, output oracle, terminal behavior,
risk route and continuation policy are fixed by this change.
