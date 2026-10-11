# ClaimsLens Phase 3 Status

## Current stage

Human annotation pilot pending.

Do not freeze rules or generate the final locked benchmark until both annotators complete the 24-case pilot.

---

## Completed

- documentary-state ontology
- deterministic state engine
- evidence extractor
- AS_OF_DATE evidence availability rule
- authority-aware closure logic
- notification engine
- prioritized review queue
- ClaimsLens Assurance demo UI
- 3 calibration episodes
- 24 blinded pilot episodes
- Annotator A package
- Annotator B package
- annotation validator
- agreement-analysis script
- adjudication template
- rule-change log
- rule-freeze checklist
- freeze snapshot tool
- benchmark specification
- 120-slot benchmark framework
- B3 direct LLM runner
- structured-prompt runner
- B5 ClaimsLens runner
- prediction merger
- benchmark evaluator
- B5 extraction evaluator
- full controlled experiment runner
- run metadata capture

---

## Next real dependency

Receive completed:

- annotator_A_form.csv
- annotator_B_form.csv

Then:

1. validate both forms
2. calculate agreement
3. review Cohen's kappa
4. adjudicate disagreements
5. update rules only if justified
6. apply prespecified decision rule
7. freeze taxonomy and code
8. populate final benchmark
9. create development/locked-test split
10. run B3 vs STRUCTURED vs B5
11. analyze unsupported closure and failure modes

---

## Important

Do not use AI-generated labels as the final human gold standard.

Do not inspect locked-test performance before rules and prompts are frozen.

Do not claim patient outcome, cost, RTW, litigation, or product-market-fit benefits from the synthetic benchmark alone.
