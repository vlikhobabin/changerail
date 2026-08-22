## 1. Contract and implementation

- [x] 1.1 Specify safe reconciliation of a current published card on resume.
- [x] 1.2 Reuse queue success criteria before marking the card delivered/skipped.

## 2. Regression and verification

- [x] 2.1 Add a regression where retained state is blocked but the current card is published.
- [x] 2.2 Prove the old runner launches the done card and stops on `already_published_card_requested_for_delivery`.
- [x] 2.3 Run focused smoke, full delivery-runner smoke, strict OpenSpec and release baseline.
- [x] 2.4 Add branch-reaching divergent-upstream and permitted dirty-retained-resume negative cases.
