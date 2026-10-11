# ClaimsLens Benchmark Plan

## Purpose

Evaluate whether explicit evidence-constrained documentary-state reconstruction reduces unsupported closure and improves traceability compared with direct LLM reasoning over the same longitudinal workers' compensation records.

---

## 1. Benchmark size

Target:

100 to 150 synthetic obligation episodes.

Final size will be chosen after the 24-episode human annotation pilot and taxonomy review.

The final benchmark will not be frozen until the human reliability pilot is complete.

---

## 2. Evaluation domain

Workers' compensation longitudinal records.

Pilot obligation classes:

- SPECIALIST_CONSULT
- DIAGNOSTIC_IMAGING
- AUTHORIZATION_REQUEST

Obligation discovery remains out of scope.

Each benchmark episode will provide the obligation to be evaluated.

---

## 3. Documentary states

Exactly one:

- OPEN
- CLOSED
- CANCELLED
- SUPERSEDED
- UNVERIFIABLE

If state = UNVERIFIABLE, assign one reason:

- NO_EVIDENCE
- NON_AUTHORITATIVE_EVIDENCE_ONLY
- CONTRADICTORY_EVIDENCE
- TEMPORALLY_INDETERMINATE

---

## 4. Dataset split

Use approximately:

- 40% development set
- 60% locked test set

The locked test set must not be used to revise prompts, state rules, extraction rules, or thresholds.

---

## 5. Methods

### B3 — Direct LLM + rules in context

Give the LLM:

- the longitudinal record
- obligation type
- AS_OF_DATE
- documentary-state definitions
- authority rules
- closure rules

The LLM directly predicts:

- documentary state
- UNVERIFIABLE reason if applicable
- evidence span
- blocker
- missing proof

No external deterministic state engine.

---

### Structured-prompt baseline

Use the same LLM as B3.

Require the model to reason through an ordered sequence:

1. identify available evidence as of AS_OF_DATE
2. identify source authority
3. identify initiation evidence
4. identify blockers
5. identify closure-critical requirements
6. identify contradictions
7. identify temporal ambiguity
8. assign documentary state

The model still makes the final state decision itself.

No external deterministic state engine.

---

### B5 — ClaimsLens architecture

Use the same LLM for evidence extraction only.

Pipeline:

1. LLM extracts evidence
2. evidence is normalized
3. AS_OF_DATE availability is enforced
4. source authority is determined
5. deterministic state signals are constructed
6. deterministic state engine assigns documentary state
7. evidence provenance, blockers, and missing proof are returned

The LLM does not directly decide the documentary state.

---

## 6. Primary outcome

Primary metric:

Macro-F1 across the five documentary states.

States:

- OPEN
- CLOSED
- CANCELLED
- SUPERSEDED
- UNVERIFIABLE

---

## 7. Safety outcome

Primary safety metric:

Unsupported Closure Rate

Definition:

Number of episodes predicted CLOSED without sufficient benchmark-supported closure evidence
divided by
number of episodes predicted CLOSED.

Also report:

- unsupported closure count
- CLOSED precision
- CLOSED recall

This is a major ClaimsLens safety outcome.

---

## 8. Secondary outcomes

Measure:

- overall exact-match accuracy
- per-state precision
- per-state recall
- per-state F1
- UNVERIFIABLE reason accuracy
- blocker precision
- blocker recall
- missing-proof accuracy
- expected-event-passed accuracy
- evidence attribution accuracy
- evidence-span overlap

---

## 9. Extraction evaluation for B5

Because B5 separates extraction from state reconstruction, evaluate the extraction layer independently.

Measure:

- evidence-type accuracy
- assertion-status accuracy
- evidence-span overlap
- source-authority accuracy
- event-date extraction accuracy
- received-date extraction accuracy

This helps distinguish:

A. extraction failures

from

B. deterministic state-engine failures.

---

## 10. Rare states

If CANCELLED or SUPERSEDED contain fewer than approximately 20 test examples, report their results as exploratory.

Do not overinterpret unstable estimates from very small classes.

---

## 11. Temporal rules

Evidence may only be used if:

received_date <= AS_OF_DATE

Event dates may occur earlier than document receipt dates.

Future information must never leak into an earlier documentary-state reconstruction.

---

## 12. Expected-event rule

If:

- an event was scheduled
- its scheduled date passed before AS_OF_DATE
- no later evidence establishes the outcome

classify according to available evidence.

Under the current strict policy, the expected default is:

UNVERIFIABLE / NO_EVIDENCE

and:

expected_event_passed = YES

Do not classify this as TEMPORALLY_INDETERMINATE merely because the date passed.

---

## 13. Authority-first rule

When evidence conflicts:

1. authoritative evidence outranks non-authoritative evidence for the same proposition
2. unresolved conflict between sufficiently authoritative sources produces:

UNVERIFIABLE / CONTRADICTORY_EVIDENCE

Silence does not cancel, supersede, or close an obligation.

---

## 14. Benchmark construction principles

Include:

- straightforward cases
- difficult boundary cases
- non-authoritative completion statements
- delayed document receipt
- passed scheduled dates
- explicit cancellation
- explicit supersession
- conflicting authoritative evidence
- genuine temporal ambiguity
- blockers
- missing closure proof

Avoid making all cases solvable through obvious keywords.

---

## 15. Difficulty

Each episode should receive a prespecified difficulty label:

- EASY
- MODERATE
- HARD

Difficulty should reflect documentary ambiguity, not model performance.

Do not relabel difficulty after seeing model results.

---

## 16. Human gold standard

The final benchmark gold labels should be created only after:

1. the 24-episode human annotation pilot is completed
2. agreement is calculated
3. disagreements are adjudicated
4. the annotation manual is revised if needed
5. the strict-policy rules are frozen

The benchmark should not silently use AI-generated labels as human ground truth.

---

## 17. Prespecified human-reliability decision rule

State not applicable under the researcher-adjudicated design:

- approximately 0.70 or higher:
  proceed

- 0.60 to below 0.70:
  revise manual, create new pilot episodes, and retest

- below 0.60:
  redesign the taxonomy before benchmark construction

---

## 18. Core research question

Can explicit evidence-constrained reconstruction of documentary obligation state reduce unsupported closure compared with direct LLM reasoning over the same longitudinal record?

---

## 19. Research interpretation

A strong result would support the claim that separating evidence extraction from deterministic documentary-state reconstruction improves reliability under the tested synthetic conditions.

A negative result is also informative.

Do not claim:

- improved patient outcomes
- reduced workers' compensation costs
- prevention of missed medical care
- clinical validation

without separate evidence.

---

## 20. Commercial interpretation

The benchmark tests technical reliability.

It does not by itself establish product-market fit or ROI.

A later commercial study would need to test whether ClaimsLens identifies consequential documentation failures earlier or more reliably than existing workflows and whether those findings produce measurable operational value.


## Researcher-Adjudicated Gold Standard

The benchmark uses researcher-adjudicated synthetic gold labels rather than a human inter-rater reliability study.

Gold labels are assigned using prespecified rules for:
- obligation type
- documentary state
- source authority
- timing and AS_OF_DATE
- blockers
- closure requirements
- missing proof
- contradictions
- temporal indeterminacy

Each benchmark episode includes a documented rationale for its assigned gold state.

The first 12 benchmark cases were used for development and tuning and are permanently restricted to the DEV split.

The final benchmark contains:
- 120 total episodes
- 48 DEV episodes
- 72 LOCKED_TEST episodes

The LOCKED_TEST cases must not be used to modify prompts, extraction logic, deterministic rules, or evaluation logic before final evaluation.

No claim of human inter-rater reliability is made.

Because the benchmark is synthetic, results are limited to controlled documentary-state reconstruction performance and must not be interpreted as evidence of clinical effectiveness, real-world claims outcomes, cost savings, litigation outcomes, return-to-work improvement, or product-market validation.
