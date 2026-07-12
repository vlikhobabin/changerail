## ADDED Requirements

### Requirement: Delivery metrics reports performance summary
The delivery metrics helper MUST report structured performance details from
delivery run records and review-cycle evidence without scraping raw logs.

#### Scenario: Performance summary is available
- **WHEN** a delivery run record includes slow-command and review timing data
- **THEN** text metrics output includes a per-run slow-command summary and
  review-cycle timeline
- **AND** CSV output includes stable columns for those values

#### Scenario: Performance summary is unavailable
- **WHEN** a delivery run record lacks optional performance fields
- **THEN** metrics output renders the missing values as `unknown`

### Requirement: Delivery metrics reports token breakdown
The delivery metrics helper MUST report available token usage breakdowns and
derive display totals when enough structured usage data exists.

#### Scenario: Explicit total is absent
- **WHEN** a run record has `input_tokens` and `output_tokens` but no
  `total_tokens`
- **THEN** metrics output displays `total_tokens` as their sum

#### Scenario: Breakdown fields are available
- **WHEN** a run record has cached input, uncached input, output or reasoning
  token counts
- **THEN** metrics output displays those counts in text and CSV output
