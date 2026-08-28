## Context

Investigation v13 опубликована на exact commit
`1be1c2534c2d6553ad87532371ea852d2f2bd84b` и нормативно закрывает два
последних proof gap: raw RED содержит одну exact contiguous exception line, а
Unicode 16.0.0 oracle владеет отдельно написанным 235-scalar dataset и точным
digest preimage. Investigation остаётся decision source и не разрешает
production mutation сама по себе.

Authorization должна быть отдельным docs-only publish gate. Она связывает
один successor, ceiling и protocol allowance так, чтобы будущий preflight мог
проверить exact tracked source вместо вывода authority из prose или terminal
payload. Terminal v12 artifacts/runtime evidence не являются входом.

## Goals / Non-Goals

**Goals:**

- опубликовать один exact six-field authorization object для implementation v13;
- зафиксировать единственный two-field reference, exact dependencies, sole
  downstream block и максимум 499 production LOC;
- перенести original RED chronology, independent Unicode/digest и lexical
  connected activation без ослабления;
- сохранить v11 runtime/scheduler и accumulated affected-profile floor;
- оставить authorization dormant и docs-only до отдельного successor.

**Non-Goals:**

- создавать implementation card, focused test, production, CI или authority;
- читать или переносить terminal v12 payload/evidence;
- запускать history, full/affected baseline, benchmark, live matrix или
  certification;
- изменять full-only publication authority.

## Decisions

### 1. Authority задаётся одним exact object

Tracked authorization source содержит ровно:

```json
{"investigation_card":"openspec/board/4.done/investigate-affected-release-profile-unicode-matrix-activation-closure-v13.md","investigation_id":"investigate-affected-release-profile-unicode-matrix-activation-closure-v13","successor_card":"openspec/board/3.inprogress/implement-bounded-affected-release-profile-v13.md","successor_id":"implement-bounded-affected-release-profile-v13","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":true}
```

Дополнительные keys, wrapper, alternate path/id, другой successor или ceiling
невалидны. Future implementation ссылается только на опубликованную card через
exact two-field object и начинается от authorization-publishing HEAD.

Альтернатива — наследовать authority непосредственно от investigation —
отклонена: preflight требует отдельный clean `4.done` authorization source.

### 2. RED chronology остаётся original и line-exact

До executable mutation future v13 разрешены только implementation card,
same-slug OpenSpec и focused test. Прямой evidence capture сначала печатает
fingerprint, затем запускает настоящий failing import без exit masking.
Original retained entry связывает failed status, non-zero exit, fingerprint,
existing saved tree и raw line, целиком равную:

```text
ModuleNotFoundError: No module named 'changerail_release_affected_profile'
```

Fragment matching, reconstruction и поздняя reproduction не создают chronology.

### 3. Unicode oracle и activation являются обязательными successor gates

Future implementation фиксирует exact Unicode 16.0.0 `Cc|Cf` inventory:
23 ordered non-overlapping ranges, 235 scalars, U+11F00 nonmember и digest
`7fb5126f7973cc51a27f62c8712c11401ace15b9d40afdf02f1575945dc1da81`.
Digest bytes строятся из ascending `START-END` records, endpoints — ровно шесть
uppercase ASCII hex digits, delimiter — один ASCII `;`, без whitespace, BOM,
newline или trailing delimiter.

Expected membership принадлежит отдельно написанному test-only literal set из
235 scalars, sourced directly from frozen Unicode 16.0.0 categories. Он не
может быть generated/copied/derived из production table/digest/helper или
общего production-derived artifact и самостоятельно выводит ranges/preimage.

В `profile.main` разрешён ровно один lexical depth-one direct call к unaliased
`run_plan`. Structural proof дополняется connected public runner → profile →
scheduler observation; guarded, wrapped, indirect, alternate, replacement и
disconnected формы fail closed.

### 4. Authorization не расширяет executable scope

Изменяются только card, same-slug artifacts, synchronized release-CI spec и
archive metadata. Future implementation зависит ровно от investigation v13,
integration decision, scheduler v1, authorization v11 и этой authorization;
блокирует только certification и добавляет максимум 499 production LOC.

## Risks / Trade-offs

- **[Risk]** Successor может частично повторить object в другом месте. →
  **Mitigation:** only exact two-field reference принимается preflight/review.
- **[Risk]** Independent Unicode source может быть заменён production-derived
  generator. → **Mitigation:** ownership/provenance и forbidden data paths
  являются normative acceptance.
- **[Risk]** Direct call может быть синтаксически видим, но недостижим. →
  **Mitigation:** lexical AST shape и connected public-chain proof обязательны
  одновременно.
- **[Risk]** Docs-only card ошибочно трактуется как executable authority. →
  **Mitigation:** authorization разрешает только создание отдельно reviewed
  successor; affected artifacts остаются non-authoritative.

## Migration Plan

1. Синхронизировать authorization requirements в main release-CI spec.
2. Архивировать same-slug change и получить fresh ordinary/high review.
3. Опубликовать card и remote branch.
4. Только после exact remote publication создать clean implementation v13 от
   authorization HEAD.

Rollback — не публиковать authorization; executable state отсутствует.

## Open Questions

- Нет. Source, successor, ceiling, proof floor и dormancy определены точно.
