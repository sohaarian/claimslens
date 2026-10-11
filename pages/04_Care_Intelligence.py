
"""ClaimsLens CareGraph: nurse workflow + research evaluation."""
import html
import hashlib
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from claimslens_caregraph import (
    VERSION, analyze, safety_suite
)

st.set_page_config(
    page_title="ClaimsLens | Care Intelligence",
    page_icon="◎",
    layout="wide"
)

from claimslens_visual_system import show_page




try:
    from claimslens_nav import sidebar_navigation
    sidebar_navigation()
except ImportError:
    pass

try:
    from claimslens_ui import install_ui
    install_ui()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research_outputs"
DB = OUT / "caregraph_v2.sqlite3"
OUT.mkdir(exist_ok=True)


def connect():
    c = sqlite3.connect(DB, timeout=20)

    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            case_id TEXT, reviewer TEXT,
            task TEXT, status TEXT,
            source_id TEXT, rationale TEXT,
            updated TEXT,
            PRIMARY KEY(case_id, reviewer)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS reviews(
            reviewer TEXT, case_id TEXT,
            condition TEXT, decision TEXT,
            elapsed_seconds REAL, rationale TEXT,
            created TEXT,
            PRIMARY KEY(reviewer, case_id)
        )
    """)

    return c


@st.cache_data(show_spinner=False)
def load():
    a = pd.read_csv(
        ROOT / "prototype_data/obligations.csv"
    ).fillna("")

    d = pd.read_csv(
        ROOT / "prototype_data/documents.csv"
    ).fillna("")

    if not {
        "claim_id", "obligation_id", "obligation_name", "state"
    }.issubset(a.columns):
        raise ValueError("Missing medical action columns")

    if not {
        "obligation_id", "document_text"
    }.issubset(d.columns):
        raise ValueError("Missing source document columns")

    for col in ["claim_id", "obligation_id"]:
        a[col] = a[col].astype(str)

    d["obligation_id"] = d["obligation_id"].astype(str)

    if a["obligation_id"].duplicated().any():
        raise ValueError("Duplicate action identifiers")

    return a, d


try:
    actions, docs = load()
    work, events_by_id = analyze(actions, docs)
except Exception as error:
    st.error(str(error))
    st.stop()


st.markdown("""
<style>
.block-container {
    max-width: 1280px !important;
    padding-top: 1.1rem !important;
}
[data-testid="stMetric"] {
    border: 1px solid rgba(120,160,140,.28);
    padding: .75rem !important;
    border-radius: 12px;
}
.cl-header {
    padding: 1rem 0 1.25rem;
    border-bottom: 1px solid rgba(130,170,144,.22);
    margin-bottom: 1.2rem;
}
.cl-header h1 {
    font-size: 2rem;
    margin: .3rem 0;
    letter-spacing: -.04em;
}
.cl-proof {
    padding: .85rem 1rem;
    border-left: 3px solid #64ad82;
    background: rgba(75,120,89,.14);
    margin: .65rem 0;
    border-radius: 0 10px 10px 0;
}
[data-baseweb="tab-list"] {
    gap: .5rem !important;
    flex-wrap: wrap !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="cl-header">'
    '<small>CLAIMSLENS / CLINICAL CARE INTELLIGENCE</small>'
    '<h1>Find missing care. Verify the evidence.</h1>'
    '<div>Clinical record review for nurse case managers.</div>'
    '</div>',
    unsafe_allow_html=True
)

show_page('04_Care_Intelligence')


st.caption(
    "Synthetic records and experimental screening. "
    "No automated medical or coverage decisions."
)

with connect() as c:
    tasks = pd.read_sql_query(
        "SELECT * FROM tasks", c
    )

a, b, c, d = st.columns(4)
a.metric("Claims", work["claim_id"].nunique())
b.metric("Clinical actions", len(work))
c.metric(
    "Unresolved or uncertain",
    int(work["prediction"].isin(
        ["OPEN", "UNVERIFIABLE"]
    ).sum())
)
d.metric("Reviewer follow-ups", len(tasks))

care, analytics, science = st.tabs([
    "Care review",
    "Clinical analytics",
    "Research & safety"
])


def case_name(case_id):
    match = work[work["case_id"] == case_id].iloc[0]
    return (
        match["claim_id"] + "  |  "
        + match["medical_action"]
    )


with care:
    st.subheader("Care coordination worklist")

    left, right = st.columns([1.6, 1], gap="large")

    with left:
        search = st.text_input(
            "Search claims or medical actions"
        )

        queue = work.copy()

        if search.strip():
            queue = queue[
                queue["claim_id"].str.contains(
                    search, case=False, regex=False
                )
                | queue["medical_action"].str.contains(
                    search, case=False, regex=False
                )
            ]

        st.dataframe(
            queue[
                ["claim_id", "medical_action", "finding",
                 "prediction", "records"]
            ],
            hide_index=True,
            use_container_width=True,
            height=310
        )

    with right:
        counts = (
            work["finding"]
            .value_counts()
            .rename_axis("Finding")
            .reset_index(name="Actions")
        )

        st.bar_chart(
            counts, x="Finding", y="Actions",
            height=300
        )

    st.divider()

    oid = st.selectbox(
        "Open a medical action",
        work["case_id"].tolist(),
        format_func=case_name
    )

    current = work[work["case_id"] == oid].iloc[0]
    events = events_by_id[oid]
    related = docs[docs["obligation_id"] == oid]

    st.markdown("### Clinical evidence pathway")

    stages = [
        "ORDERED", "AUTHORIZED", "SCHEDULED",
        "COMPLETED", "CANCELLED", "SUPERSEDED"
    ]

    cols = st.columns(6)

    found = {
        e["stage"] for e in events
        if e["supported_candidate"]
    }

    for col, stage in zip(cols, stages):
        with col:
            st.metric(
                stage.title(),
                "Detected" if stage in found
                else "No proof"
            )

    try:
        import plotly.graph_objects as go

        fig = go.Figure()

        for stage in stages:
            matching = [
                e for e in events
                if e["stage"] == stage
                and e["timestamp"]
            ]

            if matching:
                fig.add_trace(
                    go.Scatter(
                        x=[e["date"] for e in matching],
                        y=[stage] * len(matching),
                        mode="markers",
                        name=stage.title(),
                        marker=dict(
                            size=12,
                            symbol=[
                                "circle"
                                if e["supported_candidate"]
                                else "x"
                                for e in matching
                            ]
                        ),
                        customdata=[
                            [e["source_id"], e["quote"][:100]]
                            for e in matching
                        ],
                        hovertemplate=(
                            "%{x} · %{y}"
                            "<br>%{customdata[0]}"
                            "<br>%{customdata[1]}"
                            "<extra></extra>"
                        )
                    )
                )

        fig.update_layout(
            height=280,
            margin=dict(l=5, r=5, t=10, b=10),
            showlegend=False
        )

        st.plotly_chart(
            fig, use_container_width=True,
            config={"displayModeBar": False}
        )

    except ImportError:
        st.info("Timeline requires Plotly.")

    st.info(
        "**" + current["finding"] + "**. "
        + current["next_action"]
    )

    left, right = st.columns([1.5, 1], gap="large")

    with left:
        st.markdown("#### Source evidence")

        category = st.selectbox(
            "Event to inspect",
            ["ALL"] + stages
        )

        visible = [
            e for e in events
            if category == "ALL" or e["stage"] == category
        ]

        if not visible:
            st.caption(
                "No matching evidence found. "
                "That does not prove care did not occur."
            )

        for e in visible:
            flags = [
                label for label, condition in [
                    ("Negated", e["negated"]),
                    ("Future event", e["prospective"]),
                    ("Action mismatch", not e["relevant"]),
                    ("Source needs checking", not e["source_proxy"]),
                    ("Instruction-like wording", e["instruction_like"])
                ] if condition
            ]

            st.markdown(
                '<div class="cl-proof"><small>'
                + html.escape(
                    e["date"] + " | "
                    + e["source_type"] + " | "
                    + e["source_id"]
                )
                + '</small><div>'
                + html.escape(e["quote"])
                + '</div></div>',
                unsafe_allow_html=True
            )

            if flags:
                st.caption(
                    "Review: " + ", ".join(flags)
                )

        with st.expander("Original records"):
            for _, source in related.iterrows():
                st.markdown(
                    "**"
                    + html.escape(
                        str(source.get("document_id", ""))
                    )
                    + "**"
                )
                st.write(
                    str(source["document_text"])
                )

    with right:
        st.markdown("#### Nurse follow-up")

        with st.form("care_followup"):
            reviewer = st.text_input("Reviewer ID")

            action = st.selectbox(
                "Coordination action",
                [
                    "Confirm visit outcome",
                    "Request completion report",
                    "Contact treating provider",
                    "Check authorization",
                    "Investigate conflicting notes",
                    "No further action"
                ]
            )

            task_state = st.selectbox(
                "Task status",
                ["To do", "Waiting", "Resolved"]
            )

            citation = st.text_input(
                "Relevant source ID",
                value=current["citation"]
            )

            rationale = st.text_area(
                "Evidence and reason"
            )

            submitted = st.form_submit_button(
                "Save follow-up",
                type="primary"
            )

        if submitted:
            if not reviewer.strip() or not rationale.strip():
                st.error(
                    "Reviewer ID and rationale required."
                )
            else:
                with connect() as db:
                    db.execute(
                        "INSERT OR REPLACE INTO tasks "
                        "VALUES(?,?,?,?,?,?,?)",
                        (
                            oid, reviewer.strip(), action,
                            task_state, citation.strip(),
                            rationale.strip(),
                            datetime.now(
                                timezone.utc
                            ).isoformat()
                        )
                    )
                st.success("Follow-up saved locally.")


with analytics:
    st.subheader("Clinical operations analytics")

    left, right = st.columns(2)

    with left:
        st.markdown("#### Documented states")
        counts = (
            work["stored_state"].value_counts()
            .rename_axis("Status")
            .reset_index(name="Actions")
        )
        st.bar_chart(
            counts, x="Status", y="Actions",
            height=280
        )

    with right:
        st.markdown("#### Evidence conclusions")
        counts = (
            work["prediction"].value_counts()
            .rename_axis("Status")
            .reset_index(name="Actions")
        )
        st.bar_chart(
            counts, x="Status", y="Actions",
            height=280
        )

    left, right = st.columns(2)

    with left:
        st.markdown("#### Source records per action")
        counts = (
            work["records"].value_counts()
            .sort_index()
            .rename_axis("Documents")
            .reset_index(name="Actions")
        )
        counts["Documents"] = counts["Documents"].astype(str)
        st.bar_chart(
            counts, x="Documents", y="Actions",
            height=280
        )

    with right:
        st.markdown("#### Most common medical actions")
        counts = (
            work["medical_action"].value_counts()
            .head(10)
            .rename_axis("Action")
            .reset_index(name="Count")
        )
        st.bar_chart(
            counts, x="Action", y="Count",
            height=280
        )

    st.markdown("#### Care coordination records")

    if tasks.empty:
        st.info("No reviewer follow-ups yet.")
    else:
        st.dataframe(
            tasks,
            hide_index=True,
            use_container_width=True
        )

    st.caption(
        "Analytics describe synthetic records. "
        "They are not observed patient outcomes."
    )


with science:
    st.subheader("Clinical AI evaluation")

    st.markdown("#### Safety regression checks")

    checks = safety_suite()

    st.dataframe(
        checks,
        hide_index=True,
        use_container_width=True
    )

    st.metric(
        "Developer checks passed",
        f"{int(checks['Pass'].sum())}/{len(checks)}"
    )

    st.caption(
        "These tests check expected behavior on "
        "developer-written examples. They are not "
        "independent clinical validation."
    )

    reference_db = (
        OUT / "research_studio.sqlite3"
    )

    reference = pd.DataFrame(
        columns=["case_id", "reference_state"]
    )

    if reference_db.exists():
        try:
            with sqlite3.connect(reference_db) as conn:
                reference = pd.read_sql_query(
                    "SELECT case_id, state AS reference_state "
                    "FROM adjudication", conn
                )
        except sqlite3.Error:
            pass

    st.markdown("#### Reference-standard comparison")

    if reference.empty:
        st.warning(
            "No adjudicated reference answers exist. "
            "No model accuracy is reported."
        )

    else:
        reference["case_id"] = (
            reference["case_id"].astype(str)
        )

        valid = work.merge(
            reference,
            on="case_id",
            how="inner",
            validate="one_to_one"
        )

        if not valid.empty:
            rows = []

            for method, column in [
                ("Simple keyword baseline", "keyword"),
                ("CareGraph 2", "prediction")
            ]:
                correct = (
                    valid[column] == valid["reference_state"]
                )

                unsupported = (
                    (valid[column] == "CLOSED")
                    & (valid["reference_state"] != "CLOSED")
                )

                missed_completion = (
                    (valid["reference_state"] == "CLOSED")
                    & (valid[column] != "CLOSED")
                )

                rows.append({
                    "Method": method,
                    "Cases": len(valid),
                    "Agreement": float(correct.mean()),
                    "Unsupported closures": int(unsupported.sum()),
                    "Missed completions": int(missed_completion.sum()),
                    "Abstentions": int(
                        (valid[column] == "UNVERIFIABLE").sum()
                    )
                })

            st.dataframe(
                pd.DataFrame(rows),
                hide_index=True,
                use_container_width=True
            )

            st.warning(
                "Development comparison only. "
                "Stored adjudications are not automatically "
                "an independently authored locked test set."
            )

    st.divider()

    st.markdown("#### Reviewer usefulness pilot")

    reviewer = st.text_input(
        "Reviewer pseudonym",
        key="research_reviewer"
    )

    case = st.selectbox(
        "Review case",
        work["case_id"].tolist(),
        format_func=case_name,
        key="research_case"
    )

    token = (reviewer.strip() + ":" + case).encode("utf-8")

    condition = (
        "Assisted"
        if int(hashlib.sha256(token).hexdigest()[:8], 16) % 2
        else "Manual"
    )

    st.write("Assigned condition: **" + condition + "**")

    if st.button("Begin timed review"):
        st.session_state["review_start"] = time.monotonic()
        st.session_state["review_case"] = case
        st.session_state["reviewer_id"] = reviewer.strip()

    active = (
        "review_start" in st.session_state
        and st.session_state.get("review_case") == case
        and st.session_state.get("reviewer_id") == reviewer.strip()
    )

    if active:
        records = docs[
            docs["obligation_id"] == case
        ]

        for _, note in records.iterrows():
            st.markdown(
                "**" + str(note.get("document_id", "")) + "**"
            )
            st.write(str(note["document_text"]))

        if condition == "Assisted":
            result = work[
                work["case_id"] == case
            ].iloc[0]

            st.info(
                result["finding"] + ": "
                + result["next_action"]
            )

        with st.form("research_response"):
            decision = st.selectbox(
                "Your conclusion",
                [
                    "OPEN", "CLOSED", "CANCELLED",
                    "SUPERSEDED", "UNVERIFIABLE"
                ]
            )

            rationale = st.text_area(
                "Evidence supporting your conclusion"
            )

            finish = st.form_submit_button(
                "Finish and save review"
            )

        if finish:
            if not reviewer.strip() or not rationale.strip():
                st.error(
                    "Reviewer ID and rationale required."
                )
            else:
                elapsed = (
                    time.monotonic()
                    - st.session_state["review_start"]
                )

                with connect() as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO reviews "
                        "VALUES(?,?,?,?,?,?,?)",
                        (
                            reviewer.strip(),
                            case,
                            condition,
                            decision,
                            elapsed,
                            rationale.strip(),
                            datetime.now(
                                timezone.utc
                            ).isoformat()
                        )
                    )

                del st.session_state["review_start"]
                st.success(
                    f"Review recorded: {elapsed:.1f} seconds."
                )

    with connect() as conn:
        trial = pd.read_sql_query(
            "SELECT * FROM reviews", conn
        )

    if not trial.empty:
        summary = (
            trial.groupby("condition", as_index=False)
            .agg(
                Reviews=("case_id", "count"),
                Median_seconds=("elapsed_seconds", "median")
            )
        )

        st.markdown("#### Observed pilot review times")

        st.bar_chart(
            summary,
            x="condition",
            y="Median_seconds",
            height=250
        )

        st.caption(
            "Pilot observations are not a randomized "
            "clinical effectiveness study. Reviewer "
            "experience and case difficulty may differ."
        )

    st.divider()

    st.markdown("#### Research and risk requirements")

    st.write(
        "Predefine primary outcomes, independently construct "
        "the reference cohort, have two qualified reviewers "
        "label without seeing model predictions, adjudicate "
        "disagreements, and lock the test set before final "
        "evaluation. Compare keyword, trained NLP, versioned "
        "LLM, and CareGraph approaches on the same cases. "
        "Report unsupported closures, missed completions, "
        "unresolved-care recall, abstention coverage, valid "
        "quotations, and clustered confidence intervals."
    )

    st.write(
        "Clinical implementation also requires privacy, "
        "security, access control, source validation, "
        "human oversight, intended-use review, and "
        "regulatory assessment as applicable."
    )

    st.warning(
        "ClaimsLens remains research software. "
        "No independent clinical superiority or "
        "patient-benefit result is established."
    )
