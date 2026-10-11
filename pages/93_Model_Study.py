
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="ClaimsLens | Care Coordination Intelligence",
    page_icon="◎",
    layout="wide"
)

from claimslens_page_numbers import render_number
render_number('93_Model_Study')  # CLAIMSLENS_NUMBER_INSTALL


from claimslens_visual_system import show_page
show_page('93_Model_Study')




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
OUT.mkdir(exist_ok=True)
DB = OUT / "nurse_care_worklist.sqlite3"

st.markdown("""
<style>
.block-container {
    max-width:1200px !important;
    padding:1.2rem 1.7rem 3rem !important;
}
.block-container * {
    box-sizing:border-box;
    min-width:0;
}
.cl-product {
    border:1px solid rgba(166,207,147,.25);
    border-radius:17px;
    padding:1.15rem 1.45rem;
    background:linear-gradient(120deg,#12261b,#203c29);
    margin-bottom:1rem;
}
.cl-product small {
    color:#b5e39f;
    font-weight:700;
    letter-spacing:.12em;
}
.cl-product h2 {
    color:#f0f8ec;
    font-size:1.75rem;
    letter-spacing:-.035em;
    margin:.3rem 0;
}
.cl-product p {
    color:#d3e0d2;
    line-height:1.55;
    margin:0;
}
[data-testid="stMetric"] {
    border:1px solid rgba(160,200,151,.19);
    border-radius:12px;
    padding:.8rem !important;
}
[data-baseweb="tab-list"] {
    gap:.55rem !important;
    flex-wrap:wrap !important;
}
</style>
<div class="cl-product">
  <small>CLAIMSLENS / CLINICAL CARE COORDINATION</small>
  <h2>Know what needs follow-up.</h2>
  <p>
    Review the medical evidence behind each care action,
    identify unresolved questions, and prepare your
    next coordination task.
  </p>
</div>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load():
    actions = pd.read_csv(
        ROOT / "prototype_data/obligations.csv"
    ).fillna("")

    docs = pd.read_csv(
        ROOT / "prototype_data/documents.csv"
    ).fillna("")

    needed_actions = {
        "claim_id", "obligation_id",
        "obligation_name", "state"
    }
    needed_docs = {
        "obligation_id", "document_text"
    }

    if not needed_actions.issubset(actions.columns):
        raise ValueError("Medical action columns missing.")

    if not needed_docs.issubset(docs.columns):
        raise ValueError("Source document columns missing.")

    actions["claim_id"] = actions["claim_id"].astype(str)
    actions["obligation_id"] = (
        actions["obligation_id"].astype(str)
    )
    actions["state"] = actions["state"].astype(str)

    docs["obligation_id"] = (
        docs["obligation_id"].astype(str)
    )

    if actions["obligation_id"].duplicated().any():
        raise ValueError("Duplicate medical action IDs.")

    return actions, docs


try:
    actions, docs = load()
except Exception as exc:
    st.error(str(exc))
    st.stop()


def connection():
    con = sqlite3.connect(DB, timeout=15)
    con.execute("""
        CREATE TABLE IF NOT EXISTS followups (
            obligation_id TEXT NOT NULL,
            reviewer TEXT NOT NULL,
            task TEXT NOT NULL,
            outcome TEXT NOT NULL,
            notes TEXT NOT NULL,
            updated TEXT NOT NULL,
            PRIMARY KEY(obligation_id, reviewer)
        )
    """)
    return con


def source_records(oid):
    part = docs.loc[
        docs["obligation_id"] == str(oid)
    ].copy()

    if "event_date" in part.columns:
        part["_sort"] = pd.to_datetime(
            part["event_date"],
            errors="coerce"
        )
        part = part.sort_values(
            "_sort", na_position="last"
        )

    return part


# This is a transparent screening baseline.
# It is not a validated clinical NLP system.
PATTERNS = {
    "Ordered": r"\b(ordered|requested|referred)\b",
    "Approved": r"\b(approved|authorized)\b",
    "Scheduled": r"\b(scheduled|booked)\b",
    "Completed": r"\b(performed|completed|underwent|obtained)\b"
}
NEGATION = re.compile(
    r"\b(no|not|never|without|pending|awaiting|"
    r"wasn't|hasn't|hadn't|didn't)\b",
    re.I
)


def mentions(oid):
    results = []

    for _, doc in source_records(oid).iterrows():
        content = str(doc.get("document_text", ""))

        sentences = re.split(
            r"(?<=[.!?])\s+|\n+",
            content
        )

        for sentence in sentences:
            sentence = sentence.strip()

            if not sentence:
                continue

            for stage, pattern in PATTERNS.items():
                hit = re.search(pattern, sentence, re.I)

                if hit:
                    preceding = sentence[
                        max(0, hit.start() - 65):
                        hit.start()
                    ]

                    results.append({
                        "Milestone": stage,
                        "Date": str(
                            doc.get("event_date", "")
                        ),
                        "Source": str(
                            doc.get("document_id", "")
                        ),
                        "Source type": str(
                            doc.get("source_type", "")
                        ),
                        "Exact excerpt": sentence,
                        "Possible negation": bool(
                            NEGATION.search(preceding)
                        )
                    })

    return results


def care_question(row, evidence):
    state = row["state"]

    affirmative_complete = any(
        item["Milestone"] == "Completed"
        and not item["Possible negation"]
        for item in evidence
    )

    if state == "UNVERIFIABLE":
        return (
            "Evidence needs clarification",
            "Identify the missing or inconsistent "
            "documentation and confirm the clinical "
            "action with the appropriate source.",
            1
        )

    if state == "OPEN":
        return (
            "Care status needs follow-up",
            "Confirm whether this care action "
            "has been scheduled or completed.",
            2
        )

    if state == "CLOSED" and not affirmative_complete:
        return (
            "Completion proof needs review",
            "The record is marked completed, but this "
            "basic text screen did not find an affirmative "
            "completion mention. Inspect the actual "
            "report or encounter documentation.",
            1
        )

    if state == "SUPERSEDED":
        return (
            "Replacement action needs checking",
            "Confirm which newer order or care plan "
            "replaced this action.",
            3
        )

    if state == "CANCELLED":
        return (
            "Cancellation needs confirmation",
            "Check the reason and whether a replacement "
            "plan is documented.",
            3
        )

    return (
        "Documented status requires verification",
        "Confirm the stored status against the "
        "actual source records.",
        4
    )


@st.cache_data(show_spinner=False)
def build_worklist(action_frame, document_frame):
    # Input data is used by the cached computation
    # through the current source_records and mentions
    # helpers. The dataframe arguments invalidate
    # the cache when the underlying data changes.
    rows = []

    for _, action in action_frame.iterrows():
        evidence = mentions(action["obligation_id"])
        concern, next_action, rank = care_question(
            action, evidence
        )

        rows.append({
            "claim_id": action["claim_id"],
            "obligation_id": action["obligation_id"],
            "Medical action": action["obligation_name"],
            "File status": action["state"],
            "Review question": concern,
            "Suggested follow-up": next_action,
            "Priority": rank,
            "Linked records": len(
                source_records(action["obligation_id"])
            )
        })

    return pd.DataFrame(rows)


work = build_worklist(actions, docs)
work = work.sort_values(
    ["Priority", "claim_id"]
).reset_index(drop=True)

with connection() as con:
    saved = pd.read_sql_query(
        "SELECT * FROM followups", con
    )

a, b, c, d = st.columns(4)

a.metric("Claims", actions["claim_id"].nunique())
b.metric("Care actions", len(work))
c.metric(
    "Open or unverifiable",
    int(
        actions["state"].isin(
            ["OPEN", "UNVERIFIABLE"]
        ).sum()
    )
)
d.metric("Follow-ups saved", len(saved))

st.caption(
    "All records are synthetic. Priority represents "
    "documentary review needs, not clinical severity."
)

queue, evidence_tab, results = st.tabs([
    "Care Worklist",
    "Evidence Review",
    "Research & Outcomes"
])


with queue:
    left, right = st.columns(
        [1.5, 1], gap="large"
    )

    with left:
        st.subheader("What needs attention?")

        search = st.text_input(
            "Search claims and care actions",
            placeholder="MRI, referral, consultation, claim ID"
        )

        priority_filter = st.multiselect(
            "Show file statuses",
            sorted(work["File status"].unique())
        )

        view = work.copy()

        if search.strip():
            mask = (
                view["claim_id"].str.contains(
                    search, case=False, regex=False
                )
                | view["Medical action"].astype(str).str.contains(
                    search, case=False, regex=False
                )
            )
            view = view[mask]

        if priority_filter:
            view = view[
                view["File status"].isin(priority_filter)
            ]

        st.dataframe(
            view[
                [
                    "claim_id",
                    "Medical action",
                    "File status",
                    "Review question",
                    "Linked records"
                ]
            ],
            hide_index=True,
            use_container_width=True,
            height=380
        )

    with right:
        st.subheader("Portfolio at a glance")

        distribution = (
            actions["state"]
            .value_counts()
            .rename_axis("Status")
            .reset_index(name="Actions")
        )

        st.bar_chart(
            distribution,
            x="Status",
            y="Actions",
            horizontal=True,
            height=320
        )

        st.caption(
            "Stored documentary classifications, "
            "not independently verified outcomes."
        )

    st.info(
        "Choose a claim under Evidence Review to "
        "investigate the records behind a follow-up."
    )


with evidence_tab:
    st.subheader("Review one care action")

    claim = st.selectbox(
        "Claim",
        sorted(actions["claim_id"].unique())
    )

    current = work[
        work["claim_id"] == claim
    ]

    oid = st.selectbox(
        "Medical action",
        current["obligation_id"].tolist(),
        format_func=lambda value: str(
            current.loc[
                current["obligation_id"] == value,
                "Medical action"
            ].iloc[0]
        )
    )

    item = current.loc[
        current["obligation_id"] == oid
    ].iloc[0]

    note_rows = source_records(oid)
    evidence = mentions(oid)

    st.markdown("#### Care pathway")

    stages = [
        "Ordered",
        "Approved",
        "Scheduled",
        "Completed"
    ]

    observed = {
        m["Milestone"]
        for m in evidence
        if not m["Possible negation"]
    }

    cols = st.columns(4)

    for col, stage in zip(cols, stages):
        with col:
            with st.container(border=True):
                st.markdown(
                    "**" + stage + "**"
                )
                if stage in observed:
                    st.success("Mention found")
                else:
                    st.caption("Not confirmed")

    st.caption(
        "Detected mentions are not verified clinical "
        "events. These stages are not assumed to "
        "occur in order."
    )

    st.warning(
        "**Question:** "
        + item["Review question"]
        + "\n\n"
        + item["Suggested follow-up"]
    )

    left, right = st.columns(
        [1.35, 1], gap="large"
    )

    with left:
        st.markdown("#### Source records")

        if note_rows.empty:
            st.info("No linked notes.")
        else:
            for i, (_, doc) in enumerate(
                note_rows.iterrows()
            ):
                heading = (
                    str(doc.get("event_date", "Undated"))
                    + " | "
                    + str(doc.get("source_type", "Record"))
                )

                with st.expander(
                    heading,
                    expanded=i == 0
                ):
                    st.caption(
                        "Document: "
                        + str(doc.get("document_id", ""))
                    )
                    st.write(
                        str(doc.get("document_text", ""))
                    )

        st.markdown("#### Extracted evidence mentions")

        if evidence:
            st.dataframe(
                pd.DataFrame(evidence),
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info(
                "No event phrases matched the "
                "current lexical patterns."
            )

    with right:
        st.markdown("#### Record the follow-up")

        with st.form("care_followup_form"):
            reviewer = st.text_input("Reviewer ID")

            task = st.selectbox(
                "Follow-up",
                [
                    "Confirm care completion",
                    "Request missing report",
                    "Confirm scheduled appointment",
                    "Contact medical provider",
                    "Contact nurse case manager",
                    "Investigate conflicting records",
                    "No follow-up after review"
                ]
            )

            outcome = st.selectbox(
                "Current work status",
                [
                    "To do",
                    "Waiting for response",
                    "Resolved after review"
                ]
            )

            rationale = st.text_area(
                "What needs to be checked and why?",
                height=135
            )

            submit = st.form_submit_button(
                "Save reviewer action",
                type="primary"
            )

        if submit:
            if not reviewer.strip() or not rationale.strip():
                st.error(
                    "Enter a reviewer ID and explanation."
                )
            else:
                with connection() as con:
                    con.execute(
                        "INSERT OR REPLACE INTO followups "
                        "VALUES(?,?,?,?,?,?)",
                        (
                            oid,
                            reviewer.strip(),
                            task,
                            outcome,
                            rationale.strip(),
                            datetime.now(
                                timezone.utc
                            ).isoformat()
                        )
                    )

                st.success(
                    "Follow-up saved."
                )
                st.rerun()

        st.caption(
            "Saving a task does not modify "
            "the underlying clinical record."
        )


with results:
    st.subheader(
        "Is this system helping nurse case managers?"
    )

    st.write(
        "That is the question the research needs "
        "to answer. A working prototype alone "
        "does not establish clinical benefit."
    )

    a, b, c = st.columns(3)

    a.metric("Synthetic actions", len(actions))

    reference_n = 0

    reference_db = (
        OUT / "research_studio.sqlite3"
    )

    if reference_db.exists():
        try:
            with sqlite3.connect(reference_db) as con:
                reference_n = con.execute(
                    "SELECT COUNT(*) FROM adjudication"
                ).fetchone()[0]
        except sqlite3.Error:
            pass

    b.metric("Adjudicated answers", reference_n)
    c.metric("Clinical benefit measured", "Not yet")

    st.markdown("#### Follow-up activity")

    with connection() as con:
        followups = pd.read_sql_query(
            "SELECT * FROM followups",
            con
        )

    if not followups.empty:
        status = (
            followups["outcome"]
            .value_counts()
            .rename_axis("Outcome")
            .reset_index(name="Tasks")
        )

        st.bar_chart(
            status,
            x="Outcome",
            y="Tasks"
        )

        st.dataframe(
            followups,
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info(
            "No reviewer actions recorded yet."
        )

    st.divider()

    st.markdown("#### Clinical evaluation targets")

    goals = pd.DataFrame([
        {
            "Outcome": "Missed care follow-ups",
            "Measure": "Number of unresolved actions overlooked"
        },
        {
            "Outcome": "Unsupported completion",
            "Measure": "Cases incorrectly called completed"
        },
        {
            "Outcome": "Reviewer accuracy",
            "Measure": "Agreement with independent clinical answers"
        },
        {
            "Outcome": "Review efficiency",
            "Measure": "Time to make a correct review decision"
        },
        {
            "Outcome": "Automation bias",
            "Measure": "Incorrect reviewer agreement with AI suggestions"
        }
    ])

    st.dataframe(
        goals,
        hide_index=True,
        use_container_width=True
    )

    st.page_link(
        "pages/91_Clinical_Evidence_Study.py",
        label="Open independent reference labeling"
    )

    st.caption(
        "This page provides pilot workflow infrastructure. "
        "It does not prove reduced workload, "
        "fewer errors or improved patient outcomes."
    )

st.divider()

st.caption(
    "ClaimsLens Care Coordination Intelligence. "
    "Synthetic research data. Human review required."
)
