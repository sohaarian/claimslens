import json
from pathlib import Path

import pandas as pd
import streamlit as st

from claimslens_ui import install_ui, brand_hero, first_time_guide, page_purpose
ROOT = Path(__file__).resolve().parents[1]

st.set_page_config(
    page_title="ClaimsLens Research Engineering",
    page_icon="🧬",
    layout="wide",
)

from claimslens_visual_system import show_page



# CLAIMSLENS RESEARCH NAVIGATION V9
from claimslens_nav import sidebar_navigation

sidebar_navigation()

install_ui()

brand_hero(
    "Research / Engineering",
    "BUILD",
    "LOGIC",
    "This is the technical layer. It explains how ClaimsLens converts "
    "longitudinal records into grounded evidence, evaluates authority and timing, "
    "reconstructs documentary state, and applies safety-aware assurance.",
    "SYSTEM ARCHITECTURE / ASSURANCENET / RELEASE GATES",
)

show_page('3_Research_Engineering')


page_purpose(
    "What this page is for",
    "You do not need this page to review a claim. Use it when you want the "
    "technical architecture, experimental ML results, dependency logic, "
    "authority rules, safety mechanisms, and research release criteria."
)

first_time_guide("engineering")


st.markdown('\n<style>\n.stApp {\n    background:\n        radial-gradient(circle at 85% -10%,\n        rgba(190,255,55,.055), transparent 30%),\n        #080a08;\n    color: #f2f4ef;\n}\n\n.block-container {\n    max-width: 1220px;\n    padding-top: 2.8rem;\n    padding-bottom: 5rem;\n}\n\nhtml, body, [class*="css"] {\n    font-family:\n        Inter,\n        -apple-system,\n        BlinkMacSystemFont,\n        "Segoe UI",\n        sans-serif;\n}\n\nh1, h2, h3 {\n    color: #f3f5f0 !important;\n    letter-spacing: -.03em;\n}\n\nh1 {\n    font-weight: 650 !important;\n}\n\nh2 {\n    margin-top: 2.6rem !important;\n}\n\np, li, label {\n    color: #a6aea5;\n}\n\nsection[data-testid="stSidebar"] {\n    background: #090b09 !important;\n    border-right: 1px solid rgba(255,255,255,.08);\n}\n\ndiv[data-testid="stMetric"] {\n    border-top: 1px solid rgba(255,255,255,.10);\n    padding-top: 1rem;\n}\n\ndiv[data-testid="stMetricLabel"] {\n    color: #7d877d !important;\n    text-transform: uppercase;\n    letter-spacing: .08em;\n    font-size: .68rem;\n}\n\ndiv[data-testid="stMetricValue"] {\n    color: #f4f6f1 !important;\n}\n\ndiv[data-testid="stExpander"] {\n    border: 1px solid rgba(255,255,255,.09) !important;\n    border-radius: 3px !important;\n    background: #0b0e0b !important;\n}\n\ndiv[data-testid="stDataFrame"] {\n    border: 1px solid rgba(255,255,255,.09);\n    border-radius: 3px;\n    overflow: hidden;\n}\n\nhr {\n    border-color: rgba(255,255,255,.08) !important;\n}\n\n#MainMenu {\n    visibility: hidden;\n}\n\nfooter {\n    visibility: hidden;\n}\n</style>\n', unsafe_allow_html=True)



st.caption(
    "Medical AI documentary-assurance architecture • "
    "Frozen V1 validation • AssuranceNet V6 experimental development"
)

st.warning(
    "Research prototype using synthetic benchmark data. "
    "Not a clinical decision-support system and not a production HIPAA deployment."
)

summary_path = (
    ROOT
    / "research_engineering"
    / "results"
    / "DEV_TECHNICAL_SUMMARY.txt"
)

release_path = (
    ROOT
    / "research_engineering"
    / "release"
    / "release_gate.json"
)

authority_path = (
    ROOT
    / "research_engineering"
    / "config"
    / "authority_matrix.csv"
)

slice_path = (
    ROOT
    / "research_engineering"
    / "results"
    / "dev_slice_analysis.csv"
)

error_path = (
    ROOT
    / "research_engineering"
    / "results"
    / "dev_error_taxonomy.csv"
)

dependency_path = (
    ROOT
    / "research_engineering"
    / "config"
    / "dependency_graph.json"
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "System",
    "Evaluation",
    "Evidence Authority",
    "Dependency Reasoning",
    "Safety & Governance",
])

with tab1:
    st.subheader("Medical AI System Architecture")

    st.code(
        """
Longitudinal healthcare / claims documents
                ↓
        LLM evidence extraction
                ↓
        Literal evidence grounding
                ↓
      Consequential-event normalization
                ↓
     Proposition-specific source authority
                ↓
        Temporal / AS_OF reasoning
                ↓
      Documentary dependency graph
                ↓
          Failure propagation
                ↓
    Deterministic documentary-state engine
                ↓
       Safety-aware abstention
                ↓
        Evidence provenance
                ↓
          Human review
                ↓
            Audit trail
        """,
        language=None,
    )

    st.markdown(
        """
### Research question

**Can an AI-assisted system reconstruct what a longitudinal healthcare
record actually proves about consequential care-coordination obligations
while respecting provenance, authority, timing, prerequisites,
contradictions, and uncertainty?**
"""
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Documentary states", "5")
    c2.metric("Obligation classes", "3")
    c3.metric("Repeated runs / episode", "5")

with tab2:
    st.subheader("V2 Development Evaluation")

    st.info(
        "These results are development evidence. "
        "They are not a fresh final V2 holdout."
    )

    if summary_path.exists():
        st.code(summary_path.read_text(), language=None)

    if release_path.exists():
        gate = json.loads(release_path.read_text())

        st.subheader("Predefined Release Gates")

        gate_rows = []

        for name, spec in gate["gates"].items():
            gate_rows.append({
                "Gate": name,
                "Observed DEV": spec.get("observed_dev"),
                "Threshold": (
                    f"≥ {spec.get('threshold')}"
                    if "threshold" in spec
                    else f"≤ {spec.get('threshold_max')}"
                ),
                "Pass": spec.get("pass"),
                "Status": spec.get("status", ""),
            })

        st.dataframe(
            pd.DataFrame(gate_rows),
            use_container_width=True,
            hide_index=True,
        )

    if slice_path.exists():
        st.subheader("Slice Analysis")
        st.dataframe(
            pd.read_csv(slice_path),
            use_container_width=True,
            hide_index=True,
        )

    if error_path.exists():
        st.subheader("Failure Analysis")
        err = pd.read_csv(error_path)

        if len(err):
            st.dataframe(
                err,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.success("No errors recorded in this evaluation file.")

with tab3:
    st.subheader("Proposition-Specific Evidence Authority")

    st.markdown(
        """
ClaimsLens does **not** assume that a document source is globally trustworthy.

Authority is evaluated relative to the proposition being asserted.

For example:

- an imaging facility can establish that imaging occurred;
- a radiology report can establish that a report exists;
- a payer can establish its authorization decision;
- an NCM note may establish coordination activity but does not automatically
  establish clinical completion;
- a worker-reported event remains useful evidence without being treated as
  equivalent to provider documentation.
"""
    )

    if authority_path.exists():
        st.dataframe(
            pd.read_csv(authority_path),
            use_container_width=True,
            hide_index=True,
        )

with tab4:
    st.subheader("Documentary Dependency Reasoning")

    if dependency_path.exists():
        graph = json.loads(dependency_path.read_text())

        obligation = st.selectbox(
            "Obligation class",
            list(graph),
        )

        data = graph[obligation]

        for i, node in enumerate(data["nodes"], start=1):
            critical = (
                "closure-critical"
                if node in data["closure_critical"]
                else "supporting"
            )

            st.markdown(
                f"**{i}. {node}** — {critical}"
            )

            if i < len(data["nodes"]):
                st.markdown("↓")

    st.markdown(
        """
### Failure propagation

If a closure-critical upstream dependency cannot be verified, ClaimsLens
does not infer downstream completion from silence.

That lets the system distinguish:

**task tracking**

from

**documentary coordination assurance**.
"""
    )

with tab5:
    st.subheader("Safety Model")

    st.markdown(
        """
#### False reassurance

The highest-severity error is predicting **CLOSED** when the documentary
evidence does not justify closure.

#### Excessive abstention

The opposite risk is labeling too many cases **UNVERIFIABLE**, making the
system operationally unhelpful.

ClaimsLens therefore evaluates both safety and usability rather than
optimizing accuracy alone.
"""
    )

    st.subheader("Human Oversight")

    st.markdown(
        """
A ClaimsLens finding should tell the reviewer:

1. what changed;
2. why it was flagged;
3. what evidence supports it;
4. what evidence is missing;
5. which source authority rule applied;
6. which dependency is unresolved;
7. which system version produced the conclusion.
"""
    )

    st.subheader("Clinical boundary")

    st.error(
        "ClaimsLens does not diagnose, prescribe treatment, determine "
        "medical necessity, or replace clinical or claims judgment."
    )


st.divider()

st.markdown("## Core assurance capabilities")

left, right = st.columns(2)

with left:
    st.markdown("### Documentary State Engine")
    st.write(
        "Separates what may have happened in the real world from what "
        "the available claim file can actually establish."
    )

    st.markdown("### Decision-Time Replay")
    st.write(
        "Reconstructs what the record could support at a historical point "
        "using only evidence available at that time."
    )

with right:
    st.markdown("### State Transition Challenger")
    st.write(
        "Tests whether consequential transitions such as OPEN to CLOSED "
        "are supported by sufficient authoritative evidence."
    )

    st.markdown("### Evidence Sufficiency Graph")
    st.write(
        "Links evidence, authority, proposition, dependency, and documentary "
        "state to identify broken proof chains."
    )

st.divider()

st.markdown("## AssuranceNet V6 development")

st.warning(
    "Experimental development result only. V6 passed 10 of 12 "
    "prespecified development gates. Release was refused, so no new "
    "locked test was run."
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Accuracy", "95.94%")
    st.metric("Blocker F1", "1.000")

with m2:
    st.metric("Macro F1", "96.65%")
    st.metric("Assurance PR-AUC", "0.9945")

with m3:
    st.metric("CLOSED precision", "1.000")
    st.metric("Assurance ECE", "0.0158")

with m4:
    st.metric("Unsupported closures", "0")
    st.metric("Development gates", "10 / 12")

st.markdown("### What remains unresolved")

st.write(
    "**Environment robustness** — V6 did not beat the strongest baseline "
    "in every development environment."
)

st.write(
    "**Assurance ROC-AUC** — correctness ranking reached 0.8809, "
    "below the prespecified 0.97 release threshold."
)

st.markdown("### V6 model flow")

st.code(
    """LR / RF / GB expert models
        |
        v
Robust committee
        |
        +---- AssuranceNet residual candidate
        |
        v
Cross-fitted model-benefit selector
        |
        v
Authority + temporal + dependency checks
        |
        v
CLOSED safety veto
        |
        v
Correctness assurance + calibration
        |
        v
Human review + provenance"""
)

st.caption(
    "Synthetic development performance only. "
    "These results do not establish clinical validation or production readiness."
)
