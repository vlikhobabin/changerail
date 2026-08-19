## Context

`changerail-deliver` запускает child-агента в consumer workspace. Current
runner уже передает active run identifiers, чтобы child не читал собственный
runtime JSONL, но skill guidance still allows broad repository discovery. In a
large generated-source repository, broad `rg` output reached hundreds of KB per
command, was truncated, and then could not serve as reliable evidence.

This change addresses the agent contract first: children need a bounded
discovery policy they can follow before runner telemetry can report violations
or amplification symptoms.

## Goals / Non-Goals

**Goals:**
- Make bounded discovery the default delivery behavior.
- Require agents to treat truncated command output as inconclusive.
- Provide a generic discovery budget/policy handoff from runner to child.
- Keep policy independent from shell interception and codebase language.

**Non-Goals:**
- Implement a universal shell sandbox.
- Prevent every possible large command from executing.
- Delete or stop retaining raw ignored stdout/stderr evidence.
- Add repository-specific/generated-source heuristics.

## Decisions

1. Skill text is the source of truth for agent behavior. `skills/changerail-deliver/SKILL.md`
   will require scoped paths, `rg -l`, counts and bounded excerpts before any
   broad content search. This is the surface child agents actually read.
2. Truncation is an evidence state, not a failed negative proof. If command
   output is truncated, the child must narrow the query or use structured
   follow-up evidence before claiming implementation presence or absence.
3. Runner policy handoff stays advisory and public-safe. `bin/changerail-delivery-runner`
   may pass a compact environment variable or prompt block with threshold and
   recommended command patterns, but it will not intercept every shell command.
4. The policy remains generic. It describes search shape and evidence quality,
   not language-specific source layouts.

## Risks / Trade-offs

- [Agents can still ignore guidance] -> Smoke coverage should assert that
  generated child instructions include the policy, and review can audit
  command/outcome evidence for truncated-output claims.
- [Policy may slow first discovery] -> Recommended commands prioritize file
  names and counts, which are cheaper than ingesting full matching lines.
- [Thresholds may not fit every repository] -> The policy uses documented
  defaults with operator override paths rather than a single hard-coded global
  size.

## Migration Plan

Delivery skill updates apply to new invocations after bootstrap or skill sync.
No existing runtime records need migration. Consumer projects that copy skills
receive the policy through their normal ChangeRail refresh path.

## Open Questions

- Which exact default byte threshold should be documented before measurements
  from runner metadata are available?
- Should runner policy be passed only through prompt text, only through
  environment, or both for compatibility with non-Codex children?
