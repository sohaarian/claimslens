
import hashlib
import html
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="ClaimsLens | Nurse Workflow",
    page_icon="🩺",
    layout="wide"
)


# CLAIMSLENS NEXTGEN WORKSPACE START
import streamlit as st

_clx_mode = st.sidebar.radio(
    "Nurse workflow",
    ["Unified research workspace", "Original nurse workflow"],
    index=0,
    key="clx_workflow_mode"
)

if _clx_mode == "Unified research workspace":
    from claimslens_nextgen import render as _clx_render
    _clx_render()
    st.stop()

# CLAIMSLENS NEXTGEN WORKSPACE END


from claimslens_page_numbers import render_number
render_number('06_Nurse_Workflow')  # CLAIMSLENS_NUMBER_INSTALL


from claimslens_visual_system import show_page


from claimslens_translation_engine import analyze, VERSION


try:
    from claimslens_nav import sidebar_navigation
    sidebar_navigation()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research_outputs"
OUT.mkdir(exist_ok=True)
DB = OUT / "nurse_workflow_v1.sqlite3"

st.markdown("""
<style>
.block-container {
    max-width:1320px!important;
    padding:1rem 1.8rem 3rem!important
}
.cl-cap {
    font-size:.72rem;
    letter-spacing:.12em;
    font-weight:750;
    color:#66b6a3
}
.cl-title {
    font-size:clamp(1.5rem,2.6vw,2.2rem);
    font-weight:800;
    line-height:1.16;
    margin:.4rem 0;
    overflow-wrap:anywhere
}
.cl-lead {
    font-size:.95rem;
    line-height:1.6;
    opacity:.8;
    margin-bottom:1rem
}
.cl-action {
    border-left:4px solid #44b9a0;
    padding:12px 14px;
    border-radius:0 12px 12px 0;
    background:rgba(80,170,145,.1);
    margin:.6rem 0
}
.cl-source {
    border:1px solid rgba(130,173,149,.25);
    border-radius:12px;
    padding:12px;
    margin:9px 0
}
[data-testid="stMetric"] {
    border:1px solid rgba(130,173,149,.2);
    border-radius:12px;
    padding:.7rem
}
[data-baseweb="tab-list"] {
    flex-wrap:wrap
}
@media(max-width:700px) {
    .block-container {
        padding:1rem .7rem!important
    }
}
</style>
""", unsafe_allow_html=True)


# ==========================================================
# DATA STORAGE
# ==========================================================

def con():
    c = sqlite3.connect(DB, timeout=20)
    c.execute("PRAGMA busy_timeout=20000")

    c.execute("""
        CREATE TABLE IF NOT EXISTS added_notes (
            note_id TEXT PRIMARY KEY,
            action_id TEXT NOT NULL,
            document_date TEXT NOT NULL,
            source_type TEXT NOT NULL,
            document_text TEXT NOT NULL,
            reviewer TEXT NOT NULL,
            created TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS task_history (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_id TEXT NOT NULL,
            reviewer TEXT NOT NULL,
            task_type TEXT NOT NULL,
            owner TEXT NOT NULL,
            due_date TEXT,
            status TEXT NOT NULL,
            source_id TEXT,
            outcome TEXT NOT NULL,
            created TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS review_sessions (
            reviewer TEXT NOT NULL,
            action_id TEXT NOT NULL,
            condition TEXT NOT NULL,
            decision TEXT NOT NULL,
            source_id TEXT NOT NULL,
            seconds REAL NOT NULL,
            effort INTEGER NOT NULL,
            created TEXT NOT NULL,
            PRIMARY KEY(reviewer, action_id)
        )
    """)

    return c


@st.cache_data(show_spinner=False)
def inputs():
    aa = pd.read_csv(
        ROOT / "prototype_data" / "obligations.csv"
    ).fillna("")

    dd = pd.read_csv(
        ROOT / "prototype_data" / "documents.csv"
    ).fillna("")

    akeys = {
        "claim_id", "obligation_id",
        "obligation_name", "state"
    }

    dkeys = {
        "obligation_id", "document_text"
    }

    if (
        not akeys.issubset(aa.columns)
        or not dkeys.issubset(dd.columns)
    ):
        raise ValueError(
            "Expected source columns are missing."
        )

    for column in ("claim_id", "obligation_id"):
        aa[column] = aa[column].astype(str)

    dd["obligation_id"] = (
        dd["obligation_id"].astype(str)
    )

    for column in (
        "document_id", "event_date", "source_type"
    ):
        if column not in dd.columns:
            dd[column] = ""

    if aa["obligation_id"].duplicated().any():
        raise ValueError(
            "Duplicate medical action IDs detected."
        )

    return aa, dd


try:
    actions, original_docs = inputs()

    with con() as db:
        additions = pd.read_sql_query(
            "SELECT * FROM added_notes", db
        )

        history = pd.read_sql_query(
            "SELECT * FROM task_history "
            "ORDER BY task_id DESC",
            db
        )

        sessions = pd.read_sql_query(
            "SELECT * FROM review_sessions", db
        )

    extension = pd.DataFrame({
        "obligation_id": additions["action_id"].astype(str),
        "document_id": additions["note_id"],
        "event_date": additions["document_date"],
        "source_type": additions["source_type"],
        "document_text": additions["document_text"]
    })

    full_docs = pd.concat(
        [original_docs, extension],
        ignore_index=True
    )

    prior, prior_events = analyze(
        actions, original_docs
    )

    latest, events = analyze(
        actions, full_docs
    )

    work = latest.merge(
        prior[
            ["case_id", "prediction"]
        ].rename(
            columns={"prediction": "before"}
        ),
        on="case_id",
        validate="one_to_one"
    )

    work["changed"] = (
        work["prediction"] != work["before"]
    )

except Exception as error:
    st.error(
        "Could not open nurse workflow: "
        + str(error)
    )
    st.stop()


# ==========================================================
# PRODUCT INTRODUCTION
# ==========================================================

st.markdown(
    '<div class="cl-cap">'
    'CLAIMSLENS / CARE COORDINATION'
    '</div>'
    '<div class="cl-title">'
    'Know what to follow up. Know why.'
    '</div>'
    '<div class="cl-lead">'
    'One nurse workflow: find an open care question, '
    'review the dated records, document a follow-up, '
    'and see what changes when new evidence arrives.'
    '</div>',
    unsafe_allow_html=True
)

show_page('06_Nurse_Workflow')


m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Claims",
    actions["claim_id"].nunique()
)

m2.metric(
    "Care actions",
    len(work)
)

m3.metric(
    "Needs verification",
    int(
        work["prediction"].isin(
            ["OPEN", "UNVERIFIABLE"]
        ).sum()
    )
)

m4.metric(
    "New updates",
    len(additions)
)

st.caption(
    "Synthetic file review. Screening states do not "
    "establish that treatment did or did not occur."
)


worktab, case_tab, tasks_tab, outcomes_tab = st.tabs([
    "1. Find the gap",
    "2. Review the case",
    "3. Follow-up tasks",
    "4. See the impact"
])


# ==========================================================
# STEP 1 - WHAT NEEDS ATTENTION
# ==========================================================

with worktab:
    st.markdown(
        "### Which cases should the nurse check?"
    )

    st.write(
        "Use this list to find an unresolved question. "
        "These are documentary worklist suggestions, "
        "not a ranking of medical urgency."
    )

    q = st.text_input(
        "Search claim or care action",
        key="ncm_search",
        placeholder="Lumbar MRI, WC-1002..."
    )

    selected_status = st.multiselect(
        "Filter review status",
        sorted(
            work["prediction"].unique().tolist()
        )
    )

    queue = work.copy()

    if q:
        queue = queue[
            queue["claim_id"].str.contains(
                q, case=False, regex=False
            )
            |
            queue["action"].str.contains(
                q, case=False, regex=False
            )
        ]

    if selected_status:
        queue = queue[
            queue["prediction"].isin(
                selected_status
            )
        ]

    left, right = st.columns(
        [1.6, 1],
        gap="large"
    )

    with left:
        st.dataframe(
            queue[
                [
                    "claim_id",
                    "action",
                    "finding",
                    "prediction",
                    "records"
                ]
            ],
            use_container_width=True,
            hide_index=True,
            height=330
        )

    with right:
        dist = (
            work["prediction"]
            .value_counts()
            .rename_axis("Status")
            .reset_index(name="Actions")
        )

        st.bar_chart(
            dist,
            x="Status",
            y="Actions",
            height=330
        )

    st.info(
        "Next: open Review the case, choose a claim, "
        "and inspect the original notes and dated evidence."
    )


# ==========================================================
# STEP 2 - REVIEW WHAT HAPPENED
# ==========================================================

with case_tab:
    st.markdown(
        "### What actually happened?"
    )

    left, right = st.columns([1, 2])

    with left:
        claim = st.selectbox(
            "Claim",
            sorted(
                work["claim_id"].unique().tolist()
            ),
            key="ncm_claim"
        )

    available = work[
        work["claim_id"] == claim
    ]

    with right:
        action_id = st.selectbox(
            "Care action",
            available["case_id"].tolist(),
            format_func=lambda x: (
                available.loc[
                    available["case_id"] == x,
                    "action"
                ].iloc[0]
            ),
            key="ncm_action"
        )

    item = available.loc[
        available["case_id"] == action_id
    ].iloc[0]

    cases = full_docs[
        full_docs["obligation_id"] == action_id
    ].copy()

    if len(cases):
        cases["_sort"] = pd.to_datetime(
            cases["event_date"],
            errors="coerce"
        )

        cases = cases.sort_values(
            "_sort",
            na_position="last"
        )

    ev = events.get(action_id, [])

    st.markdown(
        '<div class="cl-action"><strong>'
        + html.escape(str(item["finding"]))
        + '</strong><div>'
        + html.escape(str(item["followup"]))
        + '</div></div>',
        unsafe_allow_html=True
    )

    a, b, c = st.columns(3)

    a.metric(
        "Original file state",
        str(item["stored_state"])
    )

    b.metric(
        "Screening now",
        str(item["prediction"])
    )

    c.metric(
        "Source records",
        len(cases)
    )

    if item["changed"]:
        st.warning(
            "A new saved note changed the screening state: "
            + str(item["before"])
            + " → "
            + str(item["prediction"])
            + ". Verify the new source before "
            "changing any clinical conclusion."
        )

    st.markdown(
        "#### The dated care story"
    )

    timeline = []

    for e in ev:
        timeline.append({
            "Date": e["date"],
            "Milestone": e["stage"],
            "Source": e["source_id"],
            "Screening": (
                "Candidate"
                if e["admitted"]
                else "Needs checking"
            )
        })

    if timeline:
        df_t = pd.DataFrame(timeline)

        try:
            import plotly.express as px

            graph = df_t.copy()

            graph["Date"] = pd.to_datetime(
                graph["Date"],
                errors="coerce"
            )

            graph = graph.dropna(
                subset=["Date"]
            )

            if len(graph):
                fig = px.scatter(
                    graph,
                    x="Date",
                    y="Milestone",
                    color="Screening",
                    hover_data=["Source"],
                    color_discrete_map={
                        "Candidate": "#20bf86",
                        "Needs checking": "#edaa58"
                    }
                )

                fig.update_traces(
                    marker_size=13
                )

                fig.update_layout(
                    height=280,
                    margin=dict(
                        t=15, l=10, r=10, b=15
                    ),
                    legend=dict(
                        orientation="h",
                        y=-.28
                    )
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        "displayModeBar": False
                    }
                )

        except ImportError:
            st.dataframe(
                df_t,
                use_container_width=True,
                hide_index=True
            )

    else:
        st.info(
            "No event phrase matched the current "
            "screening rules. Read the full records."
        )

    left, right = st.columns(
        [1.5, 1],
        gap="large"
    )

    with left:
        st.markdown(
            "#### Exact evidence and original records"
        )

        select_stage = st.selectbox(
            "Show event type",
            ["All"] + sorted(
                set(e["stage"] for e in ev)
            ),
            key="ncm_stage"
        )

        shown = [
            e for e in ev
            if (
                select_stage == "All"
                or e["stage"] == select_stage
            )
        ]

        for event in shown:
            flags = [
                label
                for label, condition in [
                    (
                        "Negated",
                        event["negated"]
                    ),
                    (
                        "Future or planned",
                        event["future"]
                    ),
                    (
                        "Wrong action",
                        not event["relevant"]
                    ),
                    (
                        "Source not sufficient",
                        not event["source_proxy"]
                    ),
                    (
                        "Instruction-like wording",
                        event["injection"]
                    )
                ]
                if condition
            ]

            st.markdown(
                '<div class="cl-source"><small>'
                + html.escape(
                    event["date"]
                    + " · "
                    + event["source_id"]
                    + " · "
                    + event["stage"]
                )
                + '</small><div>'
                + html.escape(event["quote"])
                + '</div></div>',
                unsafe_allow_html=True
            )

            if flags:
                st.caption(
                    "Review flag: "
                    + ", ".join(flags)
                )

        with st.expander(
            "Full source documents"
        ):
            for _, doc in cases.iterrows():
                st.markdown(
                    "**"
                    + html.escape(
                        str(doc["document_id"])
                        + " · "
                        + str(doc["event_date"])
                    )
                    + "**"
                )

                st.text(
                    str(doc["document_text"])
                )

    with right:
        st.markdown(
            "#### Add a synthetic record update"
        )

        st.caption(
            "Demonstrates what happens when a new report "
            "arrives. The original dataset is never overwritten."
        )

        with st.form("ncm_add_record"):
            reviewer = st.text_input(
                "Your reviewer ID",
                key="ncm_doc_reviewer"
            )

            typ = st.selectbox(
                "Document type",
                [
                    "radiology_report",
                    "specialist_report",
                    "clinic_encounter",
                    "authorization_record",
                    "scheduling_note",
                    "other"
                ]
            )

            dated = st.date_input(
                "Document date",
                value=date.today()
            )

            content = st.text_area(
                "New synthetic note text",
                height=145,
                placeholder=(
                    "Example: Lumbar MRI performed. "
                    "Radiology report finalized."
                )
            )

            add = st.form_submit_button(
                "Save new record",
                type="primary"
            )

        if add:
            if (
                not reviewer.strip()
                or len(content.strip()) < 12
            ):
                st.error(
                    "Enter a reviewer ID and "
                    "a meaningful synthetic record."
                )

            else:
                now = datetime.now(
                    timezone.utc
                ).isoformat()

                digest = hashlib.sha256(
                    (
                        action_id
                        + typ
                        + dated.isoformat()
                        + content.strip()
                    ).encode()
                ).hexdigest()[:16]

                try:
                    with con() as db:
                        db.execute(
                            "INSERT OR IGNORE INTO added_notes "
                            "VALUES(?,?,?,?,?,?,?)",
                            (
                                "NEW-" + digest,
                                action_id,
                                dated.isoformat(),
                                typ,
                                content.strip(),
                                reviewer.strip(),
                                now
                            )
                        )

                    st.success(
                        "Saved. The care timeline and "
                        "screening will update."
                    )

                    st.rerun()

                except sqlite3.Error as error:
                    st.error(str(error))


# ==========================================================
# STEP 3 - MAKE THE FOLLOW-UP ACTIONABLE
# ==========================================================

with tasks_tab:
    st.markdown(
        "### Own the next step"
    )

    st.write(
        "A useful worklist needs an owner, a task, "
        "a result, and a source. This records the work "
        "instead of just flagging another note."
    )

    def task_label(value):
        matching = work.loc[
            work["case_id"] == value
        ].iloc[0]

        return (
            str(matching["claim_id"])
            + " — "
            + str(matching["action"])
        )

    select_action = st.selectbox(
        "Care action to follow up",
        work["case_id"].tolist(),
        format_func=task_label,
        key="ncm_follow_action"
    )

    chosen = work.loc[
        work["case_id"] == select_action
    ].iloc[0]

    st.info(
        str(chosen["finding"])
        + " — "
        + str(chosen["followup"])
    )

    with st.form("ncm_task"):
        reviewer = st.text_input(
            "Reviewer ID",
            key="ncm_task_reviewer"
        )

        owner = st.text_input(
            "Assigned to",
            placeholder="Nurse case manager"
        )

        task = st.selectbox(
            "Next coordination task",
            [
                "Confirm appointment outcome",
                "Request completed imaging report",
                "Clarify contradictory note",
                "Confirm referral completion",
                "Verify authorization",
                "Review changed work restrictions",
                "Confirm cancellation/replacement",
                "No further follow-up after review"
            ]
        )

        due = st.date_input(
            "Target follow-up date",
            value=date.today(),
            key="ncm_due"
        )

        status = st.selectbox(
            "Task progress",
            [
                "To do",
                "Waiting on provider",
                "Waiting on patient",
                "Resolved"
            ]
        )

        sid = st.text_input(
            "Document supporting this task",
            placeholder="Document ID or evidence gap"
        )

        outcome = st.text_area(
            "Reason or response received"
        )

        sent = st.form_submit_button(
            "Save care coordination log",
            type="primary"
        )

    if sent:
        if (
            not reviewer.strip()
            or not owner.strip()
            or not outcome.strip()
        ):
            st.error(
                "Reviewer, owner and reason are required."
            )

        else:
            with con() as db:
                db.execute(
                    "INSERT INTO task_history "
                    "(action_id,reviewer,task_type,owner,"
                    "due_date,status,source_id,outcome,created) "
                    "VALUES(?,?,?,?,?,?,?,?,?)",
                    (
                        select_action,
                        reviewer.strip(),
                        task,
                        owner.strip(),
                        due.isoformat(),
                        status,
                        sid.strip(),
                        outcome.strip(),
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                    )
                )

            st.success(
                "Coordination update saved."
            )

            st.rerun()

    if len(history):
        st.markdown(
            "#### Recent follow-ups"
        )

        st.dataframe(
            history[
                [
                    "action_id",
                    "task_type",
                    "owner",
                    "due_date",
                    "status",
                    "source_id",
                    "outcome"
                ]
            ],
            hide_index=True,
            use_container_width=True,
            height=320
        )

    else:
        st.info(
            "No care coordination actions recorded yet."
        )


# ==========================================================
# STEP 4 - SHOW THE WORKFLOW VALUE
# ==========================================================

with outcomes_tab:
    st.markdown(
        "### Does the tool deliver useful work?"
    )

    st.write(
        "Measure what was actually saved and checked. "
        "Time savings and clinical effectiveness require "
        "a properly controlled reviewer study."
    )

    left, right = st.columns(2)

    with left:
        st.markdown(
            "#### Work completed and waiting"
        )

        if len(history):
            counts = (
                history["status"]
                .value_counts()
                .rename_axis("Status")
                .reset_index(name="Updates")
            )

            st.bar_chart(
                counts,
                x="Status",
                y="Updates",
                height=285
            )

        else:
            st.info(
                "Follow-up activity will appear here."
            )

    with right:
        st.markdown(
            "#### Record updates by type"
        )

        if len(additions):
            counts = (
                additions["source_type"]
                .value_counts()
                .rename_axis("Source")
                .reset_index(name="Notes")
            )

            st.bar_chart(
                counts,
                x="Source",
                y="Notes",
                height=285
            )

        else:
            st.info(
                "New record analytics will appear here."
            )

    st.markdown(
        "#### Changes in documentary screening "
        "after new notes"
    )

    changed = work[
        work["changed"]
    ]

    if len(changed):
        st.dataframe(
            changed[
                [
                    "claim_id",
                    "action",
                    "before",
                    "prediction",
                    "records"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:
        st.caption(
            "No screening status has changed since "
            "the original synthetic dataset."
        )

    st.divider()

    st.markdown(
        "#### Research readiness"
    )

    refdb = (
        OUT / "research_studio.sqlite3"
    )

    adjudicated = 0

    if refdb.exists():
        try:
            with sqlite3.connect(refdb) as db:
                adjudicated = db.execute(
                    "SELECT COUNT(*) FROM adjudication"
                ).fetchone()[0]
        except sqlite3.Error:
            pass

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Adjudicated labels",
        adjudicated
    )

    c2.metric(
        "Reviewer observations",
        len(sessions)
    )

    c3.metric(
        "Clinical benefit shown",
        "Not yet"
    )

    st.write(
        "**What is valuable today:** Each case can "
        "lead to a documented follow-up, and new "
        "synthetic records can visibly change the "
        "file-review finding. "
        "**What remains unproven:** Whether this "
        "reduces missed care or review time for "
        "real nurse case managers."
    )

    if (
        ROOT / "pages/91_Clinical_Evidence_Study.py"
    ).exists():
        st.page_link(
            "pages/91_Clinical_Evidence_Study.py",
            label="Open independent reference labeling"
        )


st.divider()

st.caption(
    "ClaimsLens | Synthetic workflow demonstration | "
    "Original records unchanged | "
    "Human verification required"
)

# CLAIMSLENS ASSURANCE REVIEW EXTENSION V1
from claimslens_assurance_review import show_workspace
show_workspace()
