import pandas as pd
import streamlit as st
from pathlib import Path


from claimslens_ui import install_ui, brand_hero, first_time_guide, page_purpose
st.set_page_config(
    page_title="ClaimsLens Portfolio",
    page_icon="◎",
    layout="wide",
)

install_ui()

brand_hero(
    "Coordination Integrity Intelligence",
    "CLAIMS",
    "LENS",
    "ClaimsLens tests whether the claim file contains enough authoritative, "
    "timely, and dependency-complete evidence to support consequential "
    "workers' compensation states. It shows the conclusion, the evidence "
    "behind it, the evidence gap, and what the reviewer should verify next.",
    "DOCUMENTARY STATE / EVIDENCE AUTHORITY / HUMAN REVIEW",
)

page_purpose(
    "What this page is for",
    "This is the operational workspace. Start with Claims Needing Review, "
    "select a claim, and use Claim Review to understand the Documentary State, "
    "Evidence Reviewed, Current Blocker, Missing Proof, and next verification step."
)

first_time_guide("claims")


st.markdown('\n<style>\n.stApp {\n    background:\n        radial-gradient(circle at 85% -10%,\n        rgba(190,255,55,.055), transparent 30%),\n        #080a08;\n    color: #f2f4ef;\n}\n\n.block-container {\n    max-width: 1220px;\n    padding-top: 2.8rem;\n    padding-bottom: 5rem;\n}\n\nhtml, body, [class*="css"] {\n    font-family:\n        Inter,\n        -apple-system,\n        BlinkMacSystemFont,\n        "Segoe UI",\n        sans-serif;\n}\n\nh1, h2, h3 {\n    color: #f3f5f0 !important;\n    letter-spacing: -.03em;\n}\n\nh1 {\n    font-weight: 650 !important;\n}\n\nh2 {\n    margin-top: 2.6rem !important;\n}\n\np, li, label {\n    color: #a6aea5;\n}\n\nsection[data-testid="stSidebar"] {\n    background: #090b09 !important;\n    border-right: 1px solid rgba(255,255,255,.08);\n}\n\ndiv[data-baseweb="select"] > div,\ndiv[data-baseweb="input"] > div,\ndiv[data-testid="stTextInput"] input {\n    background: #0d100d !important;\n    border: 1px solid rgba(255,255,255,.10) !important;\n    border-radius: 3px !important;\n    color: white !important;\n}\n\ndiv[data-testid="stMetric"] {\n    border-top: 1px solid rgba(255,255,255,.10);\n    padding-top: 1rem;\n}\n\ndiv[data-testid="stMetricLabel"] {\n    color: #7d877d !important;\n    text-transform: uppercase;\n    letter-spacing: .08em;\n    font-size: .68rem;\n}\n\ndiv[data-testid="stMetricValue"] {\n    color: #f4f6f1 !important;\n}\n\ndiv[data-testid="stExpander"] {\n    border: 1px solid rgba(255,255,255,.09) !important;\n    border-radius: 3px !important;\n    background: #0b0e0b !important;\n}\n\ndiv[data-testid="stDataFrame"] {\n    border: 1px solid rgba(255,255,255,.09);\n    border-radius: 3px;\n    overflow: hidden;\n}\n\nhr {\n    border-color: rgba(255,255,255,.08) !important;\n}\n\n#MainMenu {\n    visibility: hidden;\n}\n\nfooter {\n    visibility: hidden;\n}\n</style>\n', unsafe_allow_html=True)


DATA_DIR = Path("prototype_data")

claims = pd.read_csv(DATA_DIR / "claims.csv")
obligations = pd.read_csv(DATA_DIR / "obligations.csv")
documents = pd.read_csv(DATA_DIR / "documents.csv")


st.markdown(
    """
    <style>
    .stApp {
        background: #080b10;
        color: #f5f7fb;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .eyebrow {
        font-size: 0.8rem;
        letter-spacing: 0.14em;
        color: #8f9bad;
        text-transform: uppercase;
    }

    .hero-title {
        font-size: 3.8rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        color: #9ba7b8;
        font-size: 1rem;
        max-width: 900px;
        margin-bottom: 1.8rem;
    }

    .metric-card {
        background: #0f141c;
        border: 1px solid #1e2938;
        border-radius: 16px;
        padding: 1.2rem 1.3rem;
        min-height: 120px;
    }

    .metric-number {
        font-size: 2.1rem;
        font-weight: 800;
    }

    .metric-label {
        color: #9aa7b8;
        font-size: 0.88rem;
    }

    .claim-card {
        background: #0f141c;
        border: 1px solid #1e2938;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.7rem;
    }

    .evidence-box {
        background: #101722;
        border-left: 3px solid #73e3ff;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.6rem;
    }

    .missing-box {
        background: #15130b;
        border-left: 3px solid #dfff54;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
    }

    .pill {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        border: 1px solid #2b3747;
        background: #151c27;
        margin-right: 0.35rem;
        font-size: 0.78rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="eyebrow">Coordination Integrity Intelligence</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-title">ClaimsLens Portfolio</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-subtitle">
    Portfolio-level documentary assurance for workers' compensation claims.
    Review unresolved, unsupported, contradictory, cancelled, and superseded
    obligations across the claim population.
    </div>
    """,
    unsafe_allow_html=True,
)


st.warning(
    "Synthetic portfolio simulation: these 200 claims are generated "
    "prototype data used to demonstrate the ClaimsLens workflow. "
    "They are not 200 real workers' compensation claims and should not "
    "be interpreted as real-world clinical validation."
)


# ---------------------------------------------------------
# Portfolio metrics
# ---------------------------------------------------------

total_claims = claims["claim_id"].nunique()
total_obligations = len(obligations)

unverifiable = (
    obligations["state"] == "UNVERIFIABLE"
).sum()

open_count = (
    obligations["state"] == "OPEN"
).sum()

contradictions = (
    obligations["reason"] == "CONTRADICTORY_EVIDENCE"
).sum()

expected_passed = (
    obligations["expected_event_passed"] == "YES"
).sum()


metrics = [
    (total_claims, "Claims"),
    (total_obligations, "Obligations"),
    (unverifiable, "Unverifiable obligations"),
    (open_count, "Open obligations"),
    (contradictions, "Contradictory obligations"),
    (expected_passed, "Expected events passed"),
]

for start in range(0, len(metrics), 3):
    columns = st.columns(3)

    for column, (value, label) in zip(
        columns,
        metrics[start:start + 3],
    ):
        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-number">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


st.markdown("## Claims needing review")


st.caption(
    "Portfolio states and supporting documents are generated from the "
    "same synthetic scenario definitions so displayed blockers, missing "
    "proof, and documentary evidence remain internally consistent."
)



# ---------------------------------------------------------
# Filters
# ---------------------------------------------------------

f1, f2, f3, f4 = st.columns(4)

with f1:
    state_filter = st.multiselect(
        "Documentary state",
        sorted(obligations["state"].dropna().unique()),
    )

with f2:
    obligation_filter = st.multiselect(
        "Obligation type",
        sorted(
            obligations["obligation_type"]
            .dropna()
            .unique()
        ),
    )

with f3:
    adjuster_filter = st.multiselect(
        "Adjuster",
        sorted(claims["adjuster"].dropna().unique()),
    )

with f4:
    ncm_filter = st.multiselect(
        "Nurse case manager",
        sorted(claims["ncm"].dropna().unique()),
    )


search_text = st.text_input(
    "Search claim, employer, worker alias, or obligation",
    placeholder="Search the portfolio...",
)


# ---------------------------------------------------------
# Build filtered portfolio
# ---------------------------------------------------------

portfolio = obligations.merge(
    claims,
    on="claim_id",
    how="left",
)

def assurance_issue(row):
    state = str(row.get("state", "")).strip()
    reason = str(row.get("reason", "")).strip()
    blocker = str(row.get("blocker", "")).strip()
    missing = str(row.get("missing_proof", "")).strip()

    if reason == "CONTRADICTORY_EVIDENCE":
        return "Conflicting authoritative evidence"

    if reason == "NON_AUTHORITATIVE_EVIDENCE_ONLY":
        return "Completion supported only by non-authoritative evidence"

    if reason == "TEMPORALLY_INDETERMINATE":
        return "Event sequence cannot be established"

    if reason == "NO_EVIDENCE":
        if str(row.get("expected_event_passed", "")).strip() == "YES":
            return "Expected event passed without closure evidence"
        return "Required closure evidence is missing"

    if state == "OPEN" and blocker:
        return f"Blocked by: {blocker}"

    if state == "OPEN":
        return "Obligation remains unresolved"

    if state == "SUPERSEDED":
        return "Obligation replaced by later action"

    if state == "CANCELLED":
        return "Obligation explicitly cancelled"

    if state == "CLOSED":
        return "Closure supported by documentary evidence"

    if missing:
        return f"Missing: {missing}"

    return "Documentary review required"


def assurance_priority(row):
    state = str(row.get("state", "")).strip()
    reason = str(row.get("reason", "")).strip()
    passed = str(row.get("expected_event_passed", "")).strip()
    blocker = str(row.get("blocker", "")).strip()

    if reason == "CONTRADICTORY_EVIDENCE":
        return 100

    if passed == "YES" and state == "UNVERIFIABLE":
        return 95

    if reason == "NON_AUTHORITATIVE_EVIDENCE_ONLY":
        return 90

    if reason == "TEMPORALLY_INDETERMINATE":
        return 85

    if state == "OPEN" and blocker:
        return 80

    if state == "UNVERIFIABLE":
        return 75

    if state == "OPEN":
        return 65

    if state == "SUPERSEDED":
        return 40

    if state == "CANCELLED":
        return 30

    return 10


portfolio["assurance_issue"] = portfolio.apply(
    assurance_issue,
    axis=1,
)

portfolio["priority"] = portfolio.apply(
    assurance_priority,
    axis=1,
)

filtered = portfolio.copy()

if state_filter:
    filtered = filtered[
        filtered["state"].isin(state_filter)
    ]

if obligation_filter:
    filtered = filtered[
        filtered["obligation_type"].isin(
            obligation_filter
        )
    ]

if adjuster_filter:
    filtered = filtered[
        filtered["adjuster"].isin(adjuster_filter)
    ]

if ncm_filter:
    filtered = filtered[
        filtered["ncm"].isin(ncm_filter)
    ]

if search_text.strip():
    query = search_text.lower()

    mask = (
        filtered["claim_id"].astype(str).str.lower().str.contains(query)
        | filtered["worker_alias"].astype(str).str.lower().str.contains(query)
        | filtered["employer"].astype(str).str.lower().str.contains(query)
        | filtered["obligation_name"].astype(str).str.lower().str.contains(query)
    )

    filtered = filtered[mask]


filtered = filtered.sort_values(
    ["priority", "claim_id"],
    ascending=[False, True],
)

st.caption(
    f"Showing {filtered['claim_id'].nunique()} claims "
    f"and {len(filtered)} obligations. Claims requiring the most "
    f"evidence review appear first."
)

st.caption(
    "The worklist is your starting point. Select a claim below to understand "
    "why an obligation was flagged, which evidence ClaimsLens reviewed, and "
    "what still needs to be verified."
)


display_columns = [
    "claim_id",
    "obligation_name",
    "obligation_type",
    "state",
    "assurance_issue",
    "adjuster",
    "ncm",
]

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True,
    height=420,
)


# ---------------------------------------------------------
# Claim drill-down
# ---------------------------------------------------------

st.markdown('\n<style>\n.claim-card {\n    margin-top: 1.8rem !important;\n    margin-bottom: 1.6rem !important;\n    padding: 1.5rem 1.6rem !important;\n}\n\n.missing-box {\n    margin-top: 1.2rem !important;\n    margin-bottom: 1.2rem !important;\n    padding: 1.25rem 1.35rem !important;\n}\n\ndiv[data-testid="stExpander"] {\n    margin-top: 1rem !important;\n    margin-bottom: 1.6rem !important;\n}\n\n[data-testid="stCaptionContainer"] {\n    line-height: 1.6;\n}\n\nhr {\n    margin-top: 3rem !important;\n    margin-bottom: 2.2rem !important;\n}\n</style>\n', unsafe_allow_html=True)

st.markdown("## Claim review")

st.write(
    "Claim Review turns a portfolio alert into an evidence-based explanation. "
    "For each obligation, ClaimsLens shows the documentary state, explains why "
    "that state was assigned, identifies unresolved evidence requirements, and "
    "shows the source records used to reach the conclusion."
)

st.markdown("### How to use Claim Review")

guide1, guide2, guide3, guide4 = st.columns(4)

with guide1:
    st.markdown("**1. Finding**")
    st.caption(
        "Start with the Documentary State and the technical reason ClaimsLens "
        "assigned to the obligation."
    )

with guide2:
    st.markdown("**2. Evidence Reviewed**")
    st.caption(
        "Inspect the source documents ClaimsLens used to reconstruct what the "
        "claim file currently supports."
    )

with guide3:
    st.markdown("**3. Evidence Gap**")
    st.caption(
        "Identify the blocker, missing proof, contradiction, or timing issue "
        "preventing a stronger documentary conclusion."
    )

with guide4:
    st.markdown("**4. Reviewer Action**")
    st.caption(
        "Use the identified evidence gap to determine what should be verified, "
        "requested, or reviewed next."
    )

st.divider()


available_claims = sorted(
    filtered["claim_id"].unique()
)

if not available_claims:
    st.info("No claims match the current filters.")
else:
    selected_claim = st.selectbox(
        "Select claim",
        available_claims,
    )

    claim_row = claims[
        claims["claim_id"] == selected_claim
    ].iloc[0]

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"**Claim:** {selected_claim}")
        st.markdown(f"**Worker:** {claim_row['worker_alias']}")

    with c2:
        st.markdown(f"**Adjuster:** {claim_row['adjuster']}")
        st.markdown(
            f"**Nurse case manager:** {claim_row['ncm']}"
        )

    st.caption(
        f'{claim_row["employer"]} · '
        f'Injury date {claim_row["injury_date"]}'
    )

    claim_obligations = obligations[
        obligations["claim_id"] == selected_claim
    ]

    st.markdown(
        f"### Obligations requiring review ({len(claim_obligations)})"
    )

    st.caption(
        "Each obligation is evaluated separately because different events can "
        "require different evidence, authority, timing, and prerequisites."
    )

    for obligation_index, (_, obligation) in enumerate(
        claim_obligations.iterrows(),
        start=1,
    ):

        reason = (
            obligation["reason"]
            if pd.notna(obligation["reason"])
            and obligation["reason"]
            else "—"
        )

        blocker = (
            obligation["blocker"]
            if pd.notna(obligation["blocker"])
            else ""
        )

        missing = (
            obligation["missing_proof"]
            if pd.notna(obligation["missing_proof"])
            else ""
        )

        obligation_state = str(
            obligation["state"]
        ).strip()

        obligation_reason = str(
            reason
        ).strip()

        if obligation_reason == "CONTRADICTORY_EVIDENCE":
            finding_explanation = (
                "ClaimsLens found authoritative evidence that conflicts. "
                "The record cannot support one documentary conclusion until "
                "the contradiction is resolved."
            )

        elif obligation_reason == "NON_AUTHORITATIVE_EVIDENCE_ONLY":
            finding_explanation = (
                "The record contains information suggesting the event occurred, "
                "but the available source does not have sufficient authority "
                "to prove that specific event."
            )

        elif obligation_reason == "TEMPORALLY_INDETERMINATE":
            finding_explanation = (
                "Relevant evidence exists, but ClaimsLens cannot establish "
                "the timing or sequence of events with sufficient certainty."
            )

        elif obligation_reason == "NO_EVIDENCE":
            finding_explanation = (
                "ClaimsLens could not locate the closure-critical evidence "
                "required to support completion of this obligation."
            )

        elif obligation_state == "OPEN":
            finding_explanation = (
                "The obligation remains unresolved because the record does not "
                "yet contain the evidence required to support completion."
            )

        elif obligation_state == "CLOSED":
            finding_explanation = (
                "The available record contains sufficient documentary evidence "
                "to support closure of this obligation."
            )

        elif obligation_state == "CANCELLED":
            finding_explanation = (
                "The record explicitly documents that this obligation "
                "was cancelled."
            )

        elif obligation_state == "SUPERSEDED":
            finding_explanation = (
                "A later documented action replaced this obligation, so the "
                "earlier obligation is no longer the active requirement."
            )

        else:
            finding_explanation = (
                "ClaimsLens identified this obligation for documentary review."
            )

        st.divider()

        st.caption(
            f"OBLIGATION {obligation_index:02d} / "
            f"{obligation['obligation_type']}"
        )

        st.markdown(
            f"### {obligation['obligation_name']}"
        )

        state_col, explanation_col = st.columns(
            [1, 2],
            gap="large",
        )

        with state_col:
            st.markdown("**Documentary State**")
            st.code(
                obligation_state,
                language=None,
            )

            if obligation_reason != "—":
                st.caption(
                    f"Technical reason: {obligation_reason}"
                )

        with explanation_col:
            st.markdown("**What ClaimsLens found**")
            st.write(
                finding_explanation
            )

        st.markdown("#### Evidence Gap")

        gap_left, gap_right = st.columns(
            2,
            gap="large",
        )

        with gap_left:
            st.markdown("**Current blocker**")

            if blocker:
                st.write(blocker)
                st.caption(
                    "A blocker is an unresolved prerequisite that may prevent "
                    "a later documentary conclusion from being supported."
                )
            else:
                st.caption(
                    "No explicit prerequisite blocker was identified."
                )

        with gap_right:
            st.markdown("**Missing proof**")

            if missing:
                st.write(missing)
                st.caption(
                    "This is the evidence ClaimsLens still needs before the "
                    "record can support the relevant documentary conclusion."
                )
            else:
                st.caption(
                    "No additional closure-critical proof is currently identified."
                )

        st.markdown("#### Evidence Reviewed")

        st.write(
            "These are the source records ClaimsLens used to reconstruct this "
            "obligation."
        )

        st.caption(
            "A document can support one part of the evidence chain without "
            "being sufficient to prove the entire event. Review each document "
            "for its source, assertion, timing, and authority."
        )

        obligation_docs = documents[
            documents["obligation_id"]
            == obligation["obligation_id"]
        ]

        with st.expander(
            f"Open evidence review · {len(obligation_docs)} documents"
        ):
            for _, doc in obligation_docs.iterrows():
                event_date = doc["event_date"]

                if pd.isna(event_date) or not str(event_date).strip():
                    event_date = "Date not documented"

                st.markdown(
                    f"""
                    <div class="evidence-box">
                        <strong>{doc["document_id"]}</strong><br>
                        {event_date} · {doc["source_type"]}<br>
                        {doc["document_text"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


st.divider()

st.caption(
    "Research prototype · Synthetic records only · "
    "ClaimsLens reconstructs documentary state and evidence provenance; "
    "it does not determine undocumented real-world events."
)
