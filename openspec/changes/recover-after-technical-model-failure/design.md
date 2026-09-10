## Context

Текущая доставка остановилась после завершения групп 1–2: группа 3 не стартовала,
а model session завершилась `Selected model is at capacity`. В run уже есть evidence
и verification attempts, поэтому ранний runtime-repair и plan-restoration неприменимы.

## Decisions

1. Ввести `technical-recovery-prepare/apply` для точного run. Eligibility требует
   terminal session error из allowlist, отсутствие `change-N starting`, завершённую
   предыдущую группу, неизменный payload и отсутствие writer/review/final intent.
2. Prepare сохраняет immutable receipt с predecessor hash, session ID, group number,
   failure class, fallback model и payload fingerprint. Apply создаёт единственный
   successor атомарно; старые файлы не меняются.
3. Fallback модели задаётся операторским профилем и фиксируется в receipt; это
   технический маршрут, не semantic repair и не новый review.
4. Повтор apply/recovery reconcile допускается только для той же receipt. Любой
   drift, живой процесс или неизвестный результат fail-closed.
5. Установленные runtime и обычный install не получают право такого recovery сами.

## Verification

Синтетические tests: model capacity failure до группы, отказ после writer, duplicate
apply, race, payload drift, existing evidence/checkpoints, fallback model binding,
foreign run and no extra review. E2E должен продолжить следующую группу без повтора
групп 1–2 и сохранить hashes старого run.
