
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

from claimslens_product import style

st.set_page_config(
    page_title="ClaimsLens | Evidence Study",
    page_icon="◎",
    layout="wide"
)

from claimslens_page_numbers import render_number
render_number('91_Clinical_Evidence_Study')  # CLAIMSLENS_NUMBER_INSTALL


from claimslens_visual_system import show_page
show_page('91_Clinical_Evidence_Study')



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


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research_outputs"
OUT.mkdir(exist_ok=True)

DB = OUT / "research_studio.sqlite3"

STATES = [
    "OPEN",
    "CLOSED",
    "CANCELLED",
    "SUPERSEDED",
    "UNVERIFIABLE"
]


def connect():
    con = sqlite3.connect(DB, timeout=15)

    con.execute("PRAGMA journal_mode=WAL")

    con.execute(
        "CREATE TABLE IF NOT EXISTS annotations "
        "(case_id TEXT NOT NULL, "
        "annotator TEXT NOT NULL, "
        "state TEXT NOT NULL, "
        "citation TEXT, notes TEXT, "
        "created TEXT NOT NULL, "
        "PRIMARY KEY(case_id,annotator))"
    )

    con.execute(
        "CREATE TABLE IF NOT EXISTS adjudication "
        "(case_id TEXT PRIMARY KEY, "
        "adjudicator TEXT NOT NULL, "
        "state TEXT NOT NULL, "
        "citation TEXT, notes TEXT, "
        "created TEXT NOT NULL)"
    )

    return con


@st.cache_data
def source_data():
    obls = pd.read_csv(
        ROOT / "prototype_data" / "obligations.csv"
    ).fillna("")

    docs = pd.read_csv(
        ROOT / "prototype_data" / "documents.csv"
    ).fillna("")

    obls["obligation_id"] = (
        obls["obligation_id"].astype(str)
    )

    docs["obligation_id"] = (
        docs["obligation_id"].astype(str)
    )

    return obls, docs


try:
    obligations, documents = source_data()

except Exception as exc:
    st.error(str(exc))
    st.stop()

if obligations.empty:
    st.warning("No synthetic actions available.")
    st.stop()


st.title("Clinical Evidence Study")

st.write(
    "**Build measurable research evidence.** "
    "Two different people independently review a case, "
    "a third reviewer adjudicates its reference label, "
    "and predictions can then be evaluated against "
    "those adjudicated answers."
)

st.caption(
    "Local research workspace using synthetic records. "
    "No CSV downloads required. Reviewer independence "
    "must be established through study procedures; "
    "pseudonyms alone do not guarantee independence."
)

t1, t2, t3 = st.tabs([
    "01 · Independent labeling",
    "02 · Resolve disagreements",
    "03 · Evidence and evaluation"
])


# ==========================================================
# INDEPENDENT ANNOTATION
# ==========================================================

with t1:
    st.subheader("What does the record support?")

    st.write(
        "Read the source documents before deciding. "
        "Do not copy the existing system prediction."
    )

    reviewer = st.text_input(
        "Reviewer ID (use a pseudonym)"
    )

    oid = st.selectbox(
        "Clinical action",
        obligations["obligation_id"].tolist(),
        format_func=lambda x: (
            str(x)
            + " · "
            + str(
                obligations.loc[
                    obligations["obligation_id"] == x,
                    "obligation_name"
                ].iloc[0]
            )
        )
    )

    selected = obligations[
        obligations["obligation_id"] == oid
    ].iloc[0]

    st.markdown(
        "**Clinical action:** "
        + str(selected["obligation_name"])
    )

    notes = documents[
        documents["obligation_id"] == oid
    ]

    for _, doc in notes.iterrows():
        with st.expander(
            str(doc.get("event_date", "Undated"))
            + " · "
            + str(doc.get("document_id", "Source")),
            expanded=True
        ):
            st.write(
                str(doc.get("document_text", ""))
            )

    doc_ids = notes[
        "document_id"
    ].astype(str).tolist()

    with st.form("annotation_form"):
        label = st.selectbox(
            "Your documentary conclusion",
            STATES
        )

        citations = st.multiselect(
            "Which source IDs support your conclusion?",
            doc_ids
        )

        reason = st.text_area(
            "Evidence justification / uncertainties",
            placeholder=(
                "What establishes or fails to "
                "establish completion?"
            )
        )

        submitted = st.form_submit_button(
            "Save independent annotation",
            type="primary"
        )

    if submitted:
        if not reviewer.strip() or not reason.strip():
            st.error(
                "Enter a reviewer ID and reasoning."
            )
        else:
            now = datetime.now(
                timezone.utc
            ).isoformat()

            with connect() as con:
                con.execute(
                    "INSERT OR REPLACE INTO annotations "
                    "VALUES(?,?,?,?,?,?)",
                    (
                        oid,
                        reviewer.strip(),
                        label,
                        ";".join(citations),
                        reason,
                        now
                    )
                )

            st.success(
                "Annotation saved inside ClaimsLens."
            )


# ==========================================================
# ADJUDICATION
# ==========================================================

with t2:
    st.subheader(
        "Independent agreement and adjudication"
    )

    with connect() as con:
        annotations = pd.read_sql_query(
            "SELECT * FROM annotations",
            con
        )

    st.metric(
        "Independent annotations",
        len(annotations)
    )

    st.metric(
        "Unique labeled cases",
        annotations["case_id"].nunique()
        if not annotations.empty else 0
    )

    if annotations.empty:
        st.info(
            "Collect at least two independent "
            "annotations per case."
        )

    else:
        counts = (
            annotations.groupby("case_id")
            .agg(
                reviewers=("annotator", "nunique"),
                distinct_states=("state", "nunique")
            )
            .reset_index()
        )

        eligible = counts[
            counts["reviewers"] >= 2
        ]["case_id"].tolist()

        st.dataframe(
            counts,
            hide_index=True,
            use_container_width=True
        )

        if eligible:
            cid = st.selectbox(
                "Case to adjudicate",
                eligible
            )

            pair = annotations[
                annotations["case_id"] == cid
            ]

            st.dataframe(
                pair[
                    [
                        "annotator",
                        "state",
                        "citation",
                        "notes"
                    ]
                ],
                hide_index=True,
                use_container_width=True
            )

            adjudicator = st.text_input(
                "Adjudicator ID (different from "
                "independent reviewers)"
            )

            decision = st.selectbox(
                "Final adjudicated state",
                STATES
            )

            available_docs = documents.loc[
                documents["obligation_id"] == cid,
                "document_id"
            ].astype(str).tolist()

            final_citations = st.multiselect(
                "Final evidence document IDs",
                available_docs
            )

            justification = st.text_area(
                "Why is this the defensible final label?"
            )

            if st.button(
                "Save adjudicated gold label",
                type="primary"
            ):
                if (
                    not adjudicator.strip()
                    or adjudicator.strip()
                    in pair["annotator"].tolist()
                    or not justification.strip()
                ):
                    st.error(
                        "A different identified adjudicator "
                        "and written rationale are required."
                    )

                else:
                    with connect() as con:
                        con.execute(
                            "INSERT OR REPLACE INTO "
                            "adjudication VALUES(?,?,?,?,?,?)",
                            (
                                cid,
                                adjudicator.strip(),
                                decision,
                                ";".join(final_citations),
                                justification,
                                datetime.now(
                                    timezone.utc
                                ).isoformat()
                            )
                        )

                    st.success(
                        "Adjudicated reference label saved."
                    )


# ==========================================================
# COMPARATIVE EVALUATION
# ==========================================================

with t3:
    st.subheader(
        "Measured evidence, not invented accuracy"
    )

    with connect() as con:
        gold = pd.read_sql_query(
            "SELECT * FROM adjudication",
            con
        )

    st.metric(
        "Adjudicated cases",
        len(gold)
    )

    st.caption(
        "Future study target: 250–500 separately "
        "designed synthetic episodes, a prespecified "
        "test split, locked reference labels, "
        "and blinded external model comparisons. "
        "Sample size must ultimately be justified "
        "by study-design calculations."
    )

    if gold.empty:
        st.info(
            "No benchmark result yet. "
            "Collect and adjudicate independent "
            "labels first."
        )

    else:
        case_ids = gold["case_id"].tolist()

        st.dataframe(
            gold[
                [
                    "case_id",
                    "state",
                    "citation",
                    "adjudicator"
                ]
            ],
            hide_index=True,
            use_container_width=True
        )

        st.markdown(
            "#### Compare against a keyword baseline"
        )

        truth = gold.set_index(
            "case_id"
        )["state"]

        def keyword_prediction(cid):
            note_text = " ".join(
                documents.loc[
                    documents["obligation_id"] == cid,
                    "document_text"
                ].astype(str)
            ).lower()

            return (
                "CLOSED"
                if any(
                    term in note_text
                    for term in (
                        "completed",
                        "performed",
                        "obtained"
                    )
                )
                else "OPEN"
            )

        rows = [
            {
                "case_id": cid,
                "gold": truth[cid],
                "keyword": keyword_prediction(cid)
            }
            for cid in case_ids
        ]

        comp = pd.DataFrame(rows)

        comp["correct"] = (
            comp["gold"] == comp["keyword"]
        )

        comp["unsupported_close"] = (
            (comp["keyword"] == "CLOSED")
            & (comp["gold"] != "CLOSED")
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Keyword exact accuracy",
            f"{comp['correct'].mean():.1%}"
        )

        c2.metric(
            "Unsupported closures",
            int(comp["unsupported_close"].sum())
        )

        c3.metric(
            "Evaluated cases",
            len(comp)
        )

        st.dataframe(
            comp,
            hide_index=True,
            use_container_width=True
        )

        st.warning(
            "This is a potentially development-overlapping "
            "pilot, not externally validated clinical "
            "effectiveness. Independent held-out "
            "evaluation is required."
        )

        st.markdown(
            "#### Compare another system without files"
        )

        system_name = st.text_input(
            "System label",
            value="External model"
        )

        editor = comp[["case_id"]].copy()

        editor["pred_state"] = "UNVERIFIABLE"

        editor = st.data_editor(
            editor,
            hide_index=True,
            use_container_width=True,
            disabled=["case_id"],
            column_config={
                "pred_state":
                    st.column_config.SelectboxColumn(
                        "Predicted status",
                        options=STATES,
                        required=True
                    )
            },
            key="prediction_editor"
        )

        if st.button("Evaluate these predictions"):
            predictions = editor.set_index(
                "case_id"
            )["pred_state"]

            measured = gold.copy()

            measured["pred_state"] = (
                measured["case_id"].map(predictions)
            )

            measured["correct"] = (
                measured["state"]
                == measured["pred_state"]
            )

            measured["unsupported_close"] = (
                (measured["pred_state"] == "CLOSED")
                & (measured["state"] != "CLOSED")
            )

            st.metric(
                system_name + " exact accuracy",
                f"{measured['correct'].mean():.1%}"
            )

            st.metric(
                "Unsupported closures",
                int(
                    measured["unsupported_close"].sum()
                )
            )

            st.dataframe(
                measured[
                    [
                        "case_id",
                        "state",
                        "pred_state",
                        "correct"
                    ]
                ],
                hide_index=True,
                use_container_width=True
            )

            st.caption(
                "Results describe only locally "
                "adjudicated cases. They do not establish "
                "clinical generalizability."
            )
