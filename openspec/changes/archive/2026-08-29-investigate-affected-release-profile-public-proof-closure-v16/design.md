## Context

Fresh v15 cycle 2 подтвердил exact CI, selector production guards и authority,
но отклонил proof architecture: coordinated lists могли drift-ить вместе,
runtime проверялся после Git, public evidence заменяло production functions, а
scheduler/ownership matrices не были замкнуты.

## Goals / Non-Goals

**Goals:** одна typed truth, zero-mutation admission до Git, independently
observable ledgers, real Git fixtures, complete public protocol matrices и
closed raw execution graph.

**Non-Goals:** исправлять/publish-ить v15, переносить forensic artifacts,
выполнять release/history/live/certification evidence или менять authority.

## Decisions

1. Physical task record владеет literal argv, typed operands, origins, owners и
   logical IDs. Production извлекает operands из argv/embedded AST и сравнивает
   их с тем же record; test expectation authored отдельно и не импортирует
   production constants.
2. Aggregate order закрыт: repository/origin/package → runtime/task roots → Git
   → plan → scheduler. Ни один failure report не является ledger evidence.
3. Clean child устанавливает audit/profile hooks до import; hooks и external
   filesystem snapshots наблюдают process, Git, scheduler-call и mutation sites
   без function replacement.
4. Selector разделён на public pure stream boundary и real-Git collector.
   Disposable repositories дают actual four-stream states и resolved-base
   faults; pure boundary делает source mutants дешёвыми и non-semantic.
5. Summary validator — public pure protocol boundary. Independent normative
   rows и cases исчерпывающе генерируют valid neighbors и one-field mutants.
6. Ownership oracle фиксирует exact AST graph и raw execution sites четырёх
   modules; каждый mutant хранит node path и canonical before/after digest.
7. Parsed exact CI v15 переносится без изменения.

## Risks / Trade-offs

- Proof surface велик. → Matrices data-driven, но requirement/case maps authored
  независимо и IDs сравниваются bidirectionally.
- Test hooks могут стать новой подменой. → Они только наблюдают interpreter/OS
  events и не заменяют production symbols, constants или return values.
- Public pure boundaries расширяют API. → Они не дают authority и вызываются
  тем же `main`; closed graph доказывает единственный semantic activation.

## Migration Plan

Publish investigation, затем отдельную docs-only authorization v16. Только
после remote publication создать clean implementation v16 с новым original RED.
На fresh GO опубликовать implementation и перейти к единственной certification.

## Open Questions

None.
