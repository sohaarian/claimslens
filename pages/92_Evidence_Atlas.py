
from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st

from claimslens_product import style

st.set_page_config(
    page_title="ClaimsLens | Evidence Atlas",
    page_icon="◎",
    layout="wide"
)

from claimslens_visual_system import show_page
show_page('92_Evidence_Atlas')



# CLAIMSLENS RESEARCH NAVIGATION V9
from claimslens_nav import sidebar_navigation
sidebar_navigation()

try:
    from claimslens_ui import install_ui
    install_ui()
except ImportError:
    pass

style()
# CLAIMSLENS NAV V7
from claimslens_product import product_navigation

product_navigation()


root = Path(__file__).resolve().parent.parent

st.title("Evidence Atlas")

st.write(
    "A visual view of the questions that matter: "
    "what care was documented, where evidence is "
    "missing, and which cases need review."
)

try:
    obs = pd.read_csv(
        root / "prototype_data" / "obligations.csv"
    ).fillna("")

    docs = pd.read_csv(
        root / "prototype_data" / "documents.csv"
    ).fillna("")

except Exception as e:
    st.error(f"Cannot load research data: {e}")
    st.stop()

for frame, col in [
    (obs, "obligation_id"),
    (docs, "obligation_id")
]:
    frame[col] = frame[col].astype(str)

counts = (
    docs.groupby("obligation_id")
    .size()
    .rename("Records")
)

work = obs.join(
    counts,
    on="obligation_id"
)

work["Records"] = (
    work["Records"]
    .fillna(0)
    .astype(int)
)

a, b, c = st.columns(3)

a.metric(
    "Medical actions",
    len(work)
)

b.metric(
    "No linked records",
    int((work["Records"] == 0).sum())
)

c.metric(
    "Unverifiable actions",
    int(
        work["state"]
        .astype(str)
        .eq("UNVERIFIABLE")
        .sum()
    )
)

st.caption(
    "These counts summarize the existing synthetic "
    "dataset, not real patients."
)

left, right = st.columns(2, gap="large")

with left:
    st.subheader("What is the file saying?")

    plot = (
        work["state"]
        .astype(str)
        .value_counts()
        .rename_axis("State")
        .reset_index(name="Actions")
    )

    st.bar_chart(
        plot.set_index("State"),
        height=300
    )

    st.caption(
        "These are stored documentary states, "
        "not new model predictions."
    )

with right:
    st.subheader("How much evidence is linked?")

    bins = pd.cut(
        work["Records"],
        [-1, 0, 1, 2, 4, 10**6],
        labels=[
            "None",
            "One",
            "Two",
            "Three to four",
            "Five or more"
        ]
    )

    plot2 = (
        bins.value_counts()
        .sort_index()
        .rename_axis("Linked records")
        .reset_index(name="Actions")
    )

    st.bar_chart(
        plot2.set_index("Linked records"),
        height=300
    )

    st.caption(
        "Number of linked records does not prove "
        "they support completion."
    )

st.divider()

st.subheader("Inspect a medical action")

claim = st.selectbox(
    "Synthetic claim",
    sorted(
        work["claim_id"]
        .astype(str)
        .unique()
    ),
    key="atlas_claim"
)

subset = work[
    work["claim_id"].astype(str) == str(claim)
]

ids = subset["obligation_id"].tolist()

selected = st.selectbox(
    "Medical action",
    ids,
    format_func=lambda x: str(
        subset.loc[
            subset["obligation_id"] == x,
            "obligation_name"
        ].iloc[0]
    )
)

item = subset[
    subset["obligation_id"] == selected
].iloc[0]

related = docs[
    docs["obligation_id"] == selected
].copy()

related["_date"] = pd.to_datetime(
    related["event_date"],
    errors="coerce"
)

related = related.sort_values(
    "_date",
    na_position="last"
)

st.markdown("#### Source timeline")

if related.empty:
    st.warning(
        "No source records linked. "
        "Follow up for documentation."
    )

else:
    for _, d in related.iterrows():
        heading = (
            str(d.get("event_date", "Undated"))
            + " · "
            + str(d.get("source_type", "Source"))
            + " · "
            + str(d.get("document_id", ""))
        )

        with st.expander(heading):
            st.write(
                str(d.get("document_text", ""))
            )

st.info(
    "Current file status: "
    + str(item.get("state", "Unknown"))
    + ". Review the sources before treating "
    "this as a verified clinical outcome."
)

st.divider()

st.subheader("Where the research stands")

db = (
    root
    / "research_outputs"
    / "research_studio.sqlite3"
)

n = 0

if db.exists():
    try:
        with sqlite3.connect(db) as conn:
            result = pd.read_sql_query(
                "SELECT COUNT(*) AS n FROM adjudication",
                conn
            )

            n = int(
                result["n"].iloc[0]
            )

    except (
        sqlite3.DatabaseError,
        KeyError,
        IndexError
    ):
        pass

st.metric(
    "Adjudicated reference cases in local study",
    n
)

st.write(
    "This is the critical next step. More attractive "
    "graphics cannot replace independent labels, "
    "held-out testing and measured reviewer benefit."
)

st.page_link(
    "pages/91_Clinical_Evidence_Study.py",
    label="Open the clinical evidence study"
)
