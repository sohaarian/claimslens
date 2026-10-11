
from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="ClaimsLens | Study Design",
    page_icon="◎",
    layout="wide"
)

from claimslens_page_numbers import render_number
render_number('01_Study_Design')  # CLAIMSLENS_NUMBER_INSTALL


from claimslens_visual_system import show_page
show_page('01_Study_Design')


from claimslens_nav import sidebar_navigation

sidebar_navigation()

try:
    from claimslens_ui import install_ui
    install_ui()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent

st.title("Study Design")

st.write(
    "ClaimsLens tests a specific question: "
    "can software tell the difference between "
    "medical care that was mentioned and care "
    "that the file actually proves occurred?"
)

st.caption(
    "Workers' compensation medical records. "
    "Synthetic research data. "
    "Human review required."
)

st.divider()

st.subheader("The clinical problem")

st.write(
    "A doctor's note says an MRI was ordered. "
    "Another document says it was authorized. "
    "Neither statement, by itself, proves the "
    "MRI was performed. ClaimsLens tries to "
    "find that distinction before an unfinished "
    "follow-up is overlooked."
)

a, b, c = st.columns(3)

with a:
    with st.container(border=True):
        st.markdown("**1. Read the records**")
        st.write(
            "Identify imaging, consultations, "
            "authorizations, and other care events."
        )

with b:
    with st.container(border=True):
        st.markdown("**2. Check the evidence**")
        st.write(
            "Compare sources, dates, and conflicting "
            "statements before assigning a status."
        )

with c:
    with st.container(border=True):
        st.markdown("**3. Verify the answer**")
        st.write(
            "Compare that status with a reference "
            "answer established by independent reviewers."
        )

st.divider()

st.subheader("What would make this a valid experiment?")

st.write(
    "Each system must receive the same test cases. "
    "Its predictions must be compared with reference "
    "labels created without seeing those predictions."
)

st.markdown("""
| Component | Required evidence |
|---|---|
| Reference standard | Two independent reviewers and documented adjudication |
| Baseline comparison | Keyword rules and a trained text classifier |
| Main approach | Source-aware clinical event and status verification |
| Additional comparison | A separately evaluated LLM baseline |
| Test separation | Locked cases separated by claim and source-generation family |
| Safety outcomes | Unsupported closures, missed unresolved actions, temporal and negation errors |
| Clinical usefulness | Review accuracy and time with versus without ClaimsLens |
""")

st.divider()

st.subheader("Research readiness")

data = ROOT / "prototype_data" / "obligations.csv"
database = (
    ROOT / "research_outputs"
    / "research_studio.sqlite3"
)

total = 0
claim_count = 0
adjudicated = 0
double_labeled = 0

if data.is_file():
    try:
        frame = pd.read_csv(data)

        total = len(frame)

        if "claim_id" in frame.columns:
            claim_count = (
                frame["claim_id"]
                .astype(str)
                .nunique()
            )
    except Exception as exc:
        st.warning(
            "Could not inspect synthetic data: "
            + str(exc)
        )

if database.is_file():
    try:
        with sqlite3.connect(database) as con:
            tables = set(
                pd.read_sql_query(
                    "SELECT name FROM sqlite_master "
                    "WHERE type = 'table'",
                    con
                )["name"]
            )

            if "adjudication" in tables:
                result = pd.read_sql_query(
                    "SELECT COUNT(*) AS n "
                    "FROM adjudication",
                    con
                )
                adjudicated = int(
                    result["n"].iloc[0]
                )

            if "annotations" in tables:
                result = pd.read_sql_query(
                    "SELECT COUNT(*) AS n FROM ("
                    "SELECT case_id "
                    "FROM annotations "
                    "GROUP BY case_id "
                    "HAVING COUNT(DISTINCT annotator) >= 2"
                    ")",
                    con
                )
                double_labeled = int(
                    result["n"].iloc[0]
                )

    except Exception as exc:
        st.warning(
            "Could not read local reviewer database: "
            + str(exc)
        )

c1, c2, c3, c4 = st.columns(4)

c1.metric("Synthetic actions", total)
c2.metric("Synthetic claims", claim_count)
c3.metric("Double-labeled cases", double_labeled)
c4.metric("Adjudicated answers", adjudicated)

if adjudicated == 0:
    st.warning(
        "Independent reference labels are not yet "
        "available in this study workspace. "
        "ClaimsLens is not ready to report "
        "an independently verified accuracy result."
    )
else:
    st.info(
        "Adjudicated cases are present. "
        "This alone does not establish reviewer "
        "independence, held-out validity, or "
        "clinical generalizability."
    )

st.markdown("#### What results do we need?")

st.write(
    "The main outcome is exact documentary status "
    "accuracy against adjudicated labels. "
    "Safety outcomes include unsupported closures "
    "and missed unresolved care. "
    "A later reviewer study must measure accuracy "
    "and review time."
)

st.markdown("#### What would distinguish ClaimsLens?")

st.write(
    "Its strongest research idea is source-grounded, "
    "time-aware reasoning. Rather than treating "
    "the latest mention as the truth, the system "
    "must identify which source proves an event, "
    "when it occurred, and what remains uncertain."
)

st.divider()

left, right = st.columns(2)

with left:
    if (
        ROOT / "pages"
        / "91_Clinical_Evidence_Study.py"
    ).is_file():
        st.page_link(
            "pages/91_Clinical_Evidence_Study.py",
            label="Continue to Reference Labels"
        )

with right:
    if (
        ROOT / "pages"
        / "93_Model_Study.py"
    ).is_file():
        st.page_link(
            "pages/93_Model_Study.py",
            label="Open Model Comparison"
        )

st.caption(
    "No patient outcomes, independent validation, "
    "or superiority over external systems are claimed."
)
