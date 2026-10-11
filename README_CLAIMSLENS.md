# ClaimsLens

## Evidence-Aware Medical AI for Documentary State Reconstruction

ClaimsLens is a Medical AI research-engineering system and working prototype
for reconstructing what longitudinal healthcare and workers' compensation
records actually prove about consequential care-coordination obligations.

The research problem is not generic summarization.

It is:

> Can an AI-assisted system determine what a longitudinal record actually
> proves about a consequential care-coordination obligation while respecting
> source authority, temporal availability, dependencies, contradictions,
> missing evidence, and uncertainty?

## Architecture

Documents
→ LLM evidence extraction
→ grounding
→ deterministic normalization
→ proposition authority
→ temporal reasoning
→ dependency graph
→ deterministic documentary state
→ safety-aware abstention
→ provenance
→ human review
→ audit trail

## Research engineering

ClaimsLens includes:

- DEV / holdout separation;
- repeated stochastic runs;
- state stability;
- bootstrap confidence intervals;
- safety-weighted errors;
- false-reassurance analysis;
- excessive-abstention analysis;
- ablation planning;
- adversarial testing;
- slice analysis;
- temporal reasoning;
- proposition-specific authority;
- documentary dependencies;
- artifact hashes;
- environment manifests;
- threat modeling;
- model/system card;
- data card;
- external-validation protocol.

## Prototype

The Streamlit prototype demonstrates:

portfolio
→ claim
→ obligation
→ documentary state
→ evidence chain
→ authority
→ broken dependency
→ reason flagged
→ human review
→ auditability.

## Important limitation

Current benchmark results are synthetic.

ClaimsLens is not represented as a clinically validated or HIPAA-ready
production system.
