"""ClaimsLens integrated evidence-constrained research workspace.

Synthetic research use only.
No autonomous treatment decisions.
No automatic confirmation of completed care.
No automatic clinical urgency calculation.
"""

from pathlib import Path
from datetime import datetime, timezone
import json
import re
import secrets
import sqlite3
import time

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "prototype_data"
DB = ROOT / "research_outputs" / "pathway_research.sqlite3"

STAGES = (
    "ORDERED",
    "AUTHORIZED",
    "SCHEDULED",
    "COMPLETED",
    "CANCELLED",
    "SUPERSEDED"
)

REFERENCE_STATES = [
    "OPEN",
    "CLOSED",
    "CANCELLED",
    "SUPERSEDED",
    "UNVERIFIABLE"
]


def now():
    return datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )


def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)

    cx = sqlite3.connect(str(DB), timeout=20)

    cx.execute("PRAGMA busy_timeout=20000")
    cx.execute("PRAGMA journal_mode=WAL")

    cx.executescript("""
    CREATE TABLE IF NOT EXISTS pathway_tasks (
        id INTEGER PRIMARY KEY,
        action_id TEXT NOT NULL,
        claim_id TEXT NOT NULL,
        source_id TEXT NOT NULL,
        owner TEXT NOT NULL,
        reason TEXT NOT NULL,
        type TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'OPEN',
        created_at TEXT NOT NULL,
        closed_at TEXT
    );

    CREATE UNIQUE INDEX IF NOT EXISTS one_open_pathway_task
    ON pathway_tasks(action_id)
    WHERE status='OPEN';

    CREATE TABLE IF NOT EXISTS pathway_reviews (
        action_id TEXT NOT NULL,
        reviewer TEXT NOT NULL,
        verdict TEXT NOT NULL,
        source_id TEXT NOT NULL,
        reasoning TEXT NOT NULL,
        submitted_at TEXT NOT NULL,
        PRIMARY KEY(action_id, reviewer)
    );

    CREATE TABLE IF NOT EXISTS pathway_adjudications (
        action_id TEXT PRIMARY KEY,
        adjudicator TEXT NOT NULL,
        verdict TEXT NOT NULL,
        reasoning TEXT NOT NULL,
        source_id TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS pathway_sessions (
        id TEXT PRIMARY KEY,
        reviewer TEXT NOT NULL,
        case_id TEXT NOT NULL,
        condition TEXT NOT NULL,
        started REAL NOT NULL,
        ended REAL,
        answer TEXT,
        confidence INTEGER,
        workload INTEGER
    );
    """)

    return cx


@st.cache_data(show_spinner=False)
def load():
    actions = pd.read_csv(
        DATA / "obligations.csv",
        dtype=str
    ).fillna("")

    documents = pd.read_csv(
        DATA / "documents.csv",
        dtype=str
    ).fillna("")

    required_actions = {
        "obligation_id",
        "claim_id",
        "obligation_name",
        "state"
    }

    required_documents = {
        "obligation_id",
        "document_id",
        "document_text"
    }

    if not required_actions.issubset(actions.columns):
        raise ValueError(
            "Missing required columns in obligations.csv"
        )

    if not required_documents.issubset(documents.columns):
        raise ValueError(
            "Missing required columns in documents.csv"
        )

    return actions, documents


def stage_events(records):
    """Extract candidate text mentions, not verified events."""

    rules = {
        "ORDERED":
            r"\b(order(?:ed)?|imaging requested|referral placed)\b",
        "AUTHORIZED":
            r"\b(approv(?:ed|al)|authoriz(?:ed|ation))\b",
        "SCHEDULED":
            r"\b(schedul(?:ed|ing)|appointment booked)\b",
        "COMPLETED":
            r"\b(complet(?:ed|ion)|performed|report finalized)\b",
        "CANCELLED":
            r"\b(cancel(?:led|ed|lation)|withdrawn)\b",
        "SUPERSEDED":
            r"\b(supersed(?:ed|es)|replaced by|revised order)\b"
    }

    uncertainty_terms = re.compile(
        r"\b(no|not|never|without|denied|pending|"
        r"awaiting|unable|rule out|if)\b",
        re.I
    )

    events = []

    for _, record in records.iterrows():
        document = str(record.get("document_text", ""))

        for stage, pattern in rules.items():
            matches = list(
                re.finditer(pattern, document, re.I)
            )[:3]

            for match in matches:
                start = max(0, match.start() - 65)
                end = min(
                    len(document),
                    match.end() + 65
                )

                context = document[start:end]

                uncertain = bool(
                    uncertainty_terms.search(context)
                )

                events.append({
                    "date": str(record.get("event_date", "")),
                    "source": str(record.get("document_id", "")),
                    "record_type": str(record.get("source_type", "")),
                    "candidate": stage,
                    "interpretation": (
                        "CHECK NEGATION / CONTEXT"
                        if uncertain
                        else "MENTION ONLY"
                    ),
                    "exact_quote": document[
                        match.start():match.end()
                    ],
                    "surrounding_text": context,
                    "offset": int(match.start())
                })

    return sorted(
        events,
        key=lambda item: (
            item["date"],
            item["source"],
            item["offset"]
        )
    )


def describe(action, linked, events):
    """Generate a conservative documentary review question."""

    recorded = str(action["state"]).upper()

    completion_mention = any(
        event["candidate"] == "COMPLETED"
        and event["interpretation"] == "MENTION ONLY"
        for event in events
    )

    changed_plan = any(
        event["candidate"] in ("CANCELLED", "SUPERSEDED")
        for event in events
    )

    source_types = linked.get(
        "source_type",
        pd.Series(dtype=str)
    ).tolist()

    report_present = any(
        str(source).lower() in (
            "radiology_report",
            "operative_report",
            "specialist_report",
            "discharge_summary"
        )
        for source in source_types
    )

    if changed_plan and completion_mention:
        return (
            "Potentially conflicting medical documentation",
            "Review event dates and the current plan. "
            "Do not automatically close the action."
        )

    if recorded == "CLOSED":
        return (
            "Recorded as closed — authority needs verification",
            "Verify that the completion evidence refers to "
            "the correct patient, procedure and date."
        )

    if recorded in ("CANCELLED", "SUPERSEDED"):
        return (
            "Care plan changed in the records",
            "Confirm the replacement plan or whether "
            "the action was appropriately discontinued."
        )

    if not report_present:
        return (
            "Completion documentation not located",
            "Confirm whether care occurred outside "
            "the available records before requesting a report. "
            "Do not infer that care was delayed."
        )

    return (
        "Care status requires human confirmation",
        "Review the source and its authority before "
        "making a coordination decision."
    )


def style():
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1390px !important;
            padding: 1.5rem clamp(.85rem,2.5vw,2.5rem)
                     5rem !important;
        }

        .block-container p {
            line-height: 1.65 !important;
        }

        [data-testid="stMetric"] {
            border: 1px solid rgba(160,206,135,.22);
            border-radius: 13px;
            padding: 1rem !important;
        }

        [data-baseweb="tab-list"] {
            flex-wrap: wrap !important;
            gap: .5rem;
            margin-bottom: 1rem;
        }

        .clx-hero {
            border-top: 1px solid #a9e575;
            border-bottom: 1px solid #294333;
            padding: 1.2rem 0 1.5rem;
            margin: 1rem 0 1.4rem;
        }

        .clx-eye {
            font: 700 11px monospace;
            color: #b2e978;
            letter-spacing: .14em;
        }

        .clx-title {
            font-size: clamp(1.7rem,3.2vw,2.9rem);
            line-height: 1.12;
            font-weight: 850;
            letter-spacing: -.05em;
            margin: .45rem 0;
        }

        .clx-sub {
            color: #aabeaf;
            line-height: 1.6;
            max-width: 850px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="clx-hero">'
        '<div class="clx-eye">'
        'CLAIMSLENS / 02 NURSE CASE WORKSPACE'
        '</div>'
        '<div class="clx-title">'
        'A care pathway. Every source. One next step.'
        '</div>'
        '<div class="clx-sub">'
        'Review what the records say, what remains uncertain, '
        'and the administrative follow-up a human should consider. '
        'Synthetic research data only.'
        '</div></div>',
        unsafe_allow_html=True
    )


def render():
    from claimslens_nav import sidebar_navigation

    sidebar_navigation()
    style()

    try:
        actions, docs = load()
    except Exception as error:
        st.error(
            "Unable to load synthetic medical records: "
            + str(error)
        )
        return

    cx = connect()

    try:
        overview = st.columns(4)

        overview[0].metric(
            "Claims",
            actions.claim_id.nunique()
        )

        overview[1].metric(
            "Care actions",
            len(actions)
        )

        overview[2].metric(
            "Open / unverifiable",
            int(
                actions.state.str.upper().isin(
                    ["OPEN", "UNVERIFIABLE"]
                ).sum()
            )
        )

        overview[3].metric(
            "Adjudicated references",
            cx.execute(
                "SELECT COUNT(*) FROM pathway_adjudications"
            ).fetchone()[0]
        )

        work, pathway, tasks, methods, evaluation = st.tabs([
            "01 · Worklist",
            "02 · Evidence pathway",
            "03 · Follow-ups",
            "04 · Independent study",
            "05 · Safety scorecard"
        ])

        # =================================================
        # WORKLIST
        # =================================================

        with work:
            st.subheader(
                "Find care questions worth reviewing"
            )

            st.caption(
                "Documentary screening only. "
                "Not a medical urgency ranking."
            )

            left, right = st.columns([1, 2])

            with left:
                states = st.multiselect(
                    "Recorded state",
                    sorted(actions.state.unique()),
                    default=["OPEN", "UNVERIFIABLE"]
                )

            with right:
                search = st.text_input(
                    "Find claim or care action",
                    placeholder="MRI, consultation, WC-1001"
                )

            frame = (
                actions[actions.state.isin(states)]
                if states
                else actions
            )

            if search:
                matching = (
                    frame.claim_id.str.contains(
                        search,
                        case=False,
                        regex=False
                    )
                    |
                    frame.obligation_name.str.contains(
                        search,
                        case=False,
                        regex=False
                    )
                )

                frame = frame[matching]

            st.dataframe(
                frame[
                    [
                        "claim_id",
                        "obligation_id",
                        "obligation_name",
                        "state"
                    ]
                ].head(250),
                hide_index=True,
                use_container_width=True
            )

            left_chart, right_chart = st.columns(2)

            with left_chart:
                st.markdown("**Documentary states**")
                st.bar_chart(
                    actions.state.value_counts(),
                    height=250
                )

            with right_chart:
                st.markdown("**Medical action categories**")
                st.bar_chart(
                    actions.obligation_name.value_counts().head(8),
                    height=250,
                    horizontal=True
                )

            st.caption(
                "These are synthetic portfolio counts, "
                "not verified patient outcomes."
            )

        # =================================================
        # LONGITUDINAL EVIDENCE PATHWAY
        # =================================================

        with pathway:
            claim = st.selectbox(
                "Claim",
                sorted(actions.claim_id.unique()),
                key="clx_claim"
            )

            subset = actions[
                actions.claim_id == claim
            ]

            action_id = st.selectbox(
                "Care action",
                subset.obligation_id.tolist(),
                format_func=lambda value: (
                    value
                    + " · "
                    + str(
                        subset.loc[
                            subset.obligation_id == value,
                            "obligation_name"
                        ].iloc[0]
                    )
                ),
                key="clx_action"
            )

            action = subset[
                subset.obligation_id == action_id
            ].iloc[0]

            linked = docs[
                docs.obligation_id == action_id
            ].copy()

            events = stage_events(linked)

            finding, next_action = describe(
                action,
                linked,
                events
            )

            st.warning(
                "**Finding:** " + finding
                + "\n\n"
                + "**Suggested administrative follow-up:** "
                + next_action
            )

            st.caption(
                "A mention is not a verified clinical event. "
                "No medical urgency score is calculated."
            )

            if events:
                events_frame = pd.DataFrame(events)

                st.markdown(
                    "#### Dated, source-linked event candidates"
                )

                st.dataframe(
                    events_frame[
                        [
                            "date",
                            "candidate",
                            "interpretation",
                            "source",
                            "exact_quote",
                            "surrounding_text"
                        ]
                    ],
                    hide_index=True,
                    use_container_width=True
                )

                st.bar_chart(
                    events_frame.candidate.value_counts(),
                    height=210
                )

            else:
                st.info(
                    "No candidate stage keywords were found. "
                    "This does not establish that no care occurred."
                )

            st.markdown(
                "#### Clinical dependency questions"
            )

            st.markdown(
                "**Order → authorization → scheduling → completion** "
                "is a pathway to investigate, not a set of "
                "automatically verified events. "
                "A cancellation may have a replacement order, "
                "and a missing report may belong to an outside provider."
            )

            if not linked.empty:
                visible = [
                    column
                    for column in (
                        "event_date",
                        "source_type",
                        "document_id",
                        "document_text"
                    )
                    if column in linked.columns
                ]

                st.markdown("#### Original source documents")

                st.dataframe(
                    linked[visible],
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info(
                    "No linked source records. "
                    "The actual care status remains unknown."
                )

        # =================================================
        # HUMAN APPROVED FOLLOW-UPS
        # =================================================

        with tasks:
            claim = st.selectbox(
                "Claim for follow-up",
                sorted(actions.claim_id.unique()),
                key="clx_tasks_claim"
            )

            subset = actions[
                actions.claim_id == claim
            ]

            action_id = st.selectbox(
                "Medical action",
                subset.obligation_id.tolist(),
                key="clx_tasks_action"
            )

            linked = docs[
                docs.obligation_id == action_id
            ]

            existing = cx.execute(
                """
                SELECT id, owner, type, reason, created_at
                FROM pathway_tasks
                WHERE action_id=? AND status='OPEN'
                """,
                (action_id,)
            ).fetchall()

            if existing:
                st.info(
                    "An open follow-up already exists "
                    "for this action. Another will not be created."
                )

            with st.form("clx_task_create"):
                owner = st.text_input(
                    "Assigned reviewer or nurse ID"
                )

                task_type = st.selectbox(
                    "Administrative follow-up",
                    [
                        "Confirm outside-provider status",
                        "Request missing medical record",
                        "Clarify cancellation or replacement",
                        "Verify appointment",
                        "Verify authorization",
                        "Other human review"
                    ]
                )

                source_id = st.selectbox(
                    "Supporting evidence",
                    ["NO SOURCE"]
                    + linked.document_id.tolist()
                )

                rationale = st.text_area(
                    "Specific question and reason for follow-up"
                )

                submitted = st.form_submit_button(
                    "Save human-approved follow-up",
                    disabled=bool(existing)
                )

            if submitted:
                if (
                    not owner.strip()
                    or len(rationale.strip()) < 15
                ):
                    st.error(
                        "Enter an owner and a specific rationale "
                        "of at least 15 characters."
                    )

                else:
                    try:
                        with cx:
                            cx.execute(
                                """
                                INSERT INTO pathway_tasks
                                (
                                    action_id, claim_id, source_id,
                                    owner, reason, type, created_at
                                )
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    action_id,
                                    claim,
                                    source_id,
                                    owner.strip(),
                                    rationale.strip(),
                                    task_type,
                                    now()
                                )
                            )

                        st.success(
                            "Task saved. Medical care status "
                            "was not changed."
                        )
                        st.rerun()

                    except sqlite3.IntegrityError:
                        st.warning(
                            "Another open task exists. "
                            "Duplicate rejected."
                        )

            history = cx.execute(
                """
                SELECT id, action_id, owner, type,
                       status, created_at
                FROM pathway_tasks
                WHERE claim_id=?
                ORDER BY id DESC
                """,
                (claim,)
            ).fetchall()

            if history:
                st.markdown("#### Follow-up history")

                st.dataframe(
                    pd.DataFrame(
                        history,
                        columns=[
                            "ID",
                            "Action",
                            "Owner",
                            "Task",
                            "Status",
                            "Created"
                        ]
                    ),
                    hide_index=True,
                    use_container_width=True
                )

                open_ids = [
                    item[0]
                    for item in history
                    if item[4] == "OPEN"
                ]

                if open_ids:
                    task_id = st.selectbox(
                        "Completed administrative task",
                        open_ids
                    )

                    if st.button(
                        "Close administrative task"
                    ):
                        with cx:
                            cx.execute(
                                """
                                UPDATE pathway_tasks
                                SET status='DONE', closed_at=?
                                WHERE id=? AND status='OPEN'
                                """,
                                (now(), task_id)
                            )

                        st.success(
                            "Follow-up closed. "
                            "Medical treatment completion "
                            "has NOT been asserted."
                        )

                        st.rerun()

        # =================================================
        # INDEPENDENT CLINICAL DOCUMENT REVIEW
        # =================================================

        with methods:
            st.subheader(
                "Independent reference reviews"
            )

            st.caption(
                "Reviewer clinical qualifications and identity "
                "must be verified outside the application. "
                "Two reviews alone do not establish ground truth."
            )

            claim = st.selectbox(
                "Claim for review",
                sorted(actions.claim_id.unique()),
                key="clx_label_claim"
            )

            subset = actions[
                actions.claim_id == claim
            ]

            action_id = st.selectbox(
                "Medical action for review",
                subset.obligation_id.tolist(),
                key="clx_label_action"
            )

            linked = docs[
                docs.obligation_id == action_id
            ]

            columns = [
                column
                for column in (
                    "document_id",
                    "event_date",
                    "source_type",
                    "document_text"
                )
                if column in linked
            ]

            st.dataframe(
                linked[columns],
                hide_index=True,
                use_container_width=True
            )

            with st.form("clx_independent_review"):
                reviewer = st.text_input(
                    "Independent reviewer ID"
                )

                verdict = st.selectbox(
                    "Documentary reference state",
                    REFERENCE_STATES
                )

                source_id = st.selectbox(
                    "Evidence ID",
                    ["NO SOURCE"]
                    + linked.document_id.tolist()
                )

                reasoning = st.text_area(
                    "Explain source authority, negation, "
                    "chronology and uncertainty"
                )

                save_review = st.form_submit_button(
                    "Lock independent assessment"
                )

            if save_review:
                if (
                    not reviewer.strip()
                    or len(reasoning.strip()) < 20
                ):
                    st.error(
                        "Reviewer ID and detailed reasoning required."
                    )

                else:
                    try:
                        with cx:
                            cx.execute(
                                """
                                INSERT INTO pathway_reviews
                                VALUES (?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    action_id,
                                    reviewer.strip(),
                                    verdict,
                                    source_id,
                                    reasoning.strip(),
                                    now()
                                )
                            )

                        st.success(
                            "Independent assessment locked."
                        )

                    except sqlite3.IntegrityError:
                        st.warning(
                            "This reviewer already submitted "
                            "a locked answer."
                        )

            reviews = cx.execute(
                """
                SELECT reviewer, verdict
                FROM pathway_reviews
                WHERE action_id=?
                """,
                (action_id,)
            ).fetchall()

            reviewers = {
                item[0]
                for item in reviews
            }

            st.caption(
                f"{len(reviews)} independent assessments "
                "recorded for this action."
            )

            if len(reviewers) >= 2:
                st.markdown(
                    "#### Independent adjudication"
                )

                with st.form("clx_adjudication"):
                    adjudicator = st.text_input(
                        "Third adjudicator ID"
                    )

                    final_state = st.selectbox(
                        "Final documentary state",
                        REFERENCE_STATES
                    )

                    final_source = st.selectbox(
                        "Adjudication source",
                        ["NO SOURCE"]
                        + linked.document_id.tolist()
                    )

                    final_reason = st.text_area(
                        "Resolve disagreement and cite evidence"
                    )

                    adjudicate = st.form_submit_button(
                        "Lock adjudication"
                    )

                if adjudicate:
                    if (
                        not adjudicator.strip()
                        or adjudicator.strip() in reviewers
                        or len(final_reason.strip()) < 20
                    ):
                        st.error(
                            "Use a distinct adjudicator "
                            "and provide detailed reasoning."
                        )

                    else:
                        try:
                            with cx:
                                cx.execute(
                                    """
                                    INSERT INTO pathway_adjudications
                                    VALUES (?, ?, ?, ?, ?, ?)
                                    """,
                                    (
                                        action_id,
                                        adjudicator.strip(),
                                        final_state,
                                        final_reason.strip(),
                                        final_source,
                                        now()
                                    )
                                )

                            st.success(
                                "Adjudicated documentary answer locked."
                            )

                        except sqlite3.IntegrityError:
                            st.warning(
                                "An adjudication is already locked."
                            )

            st.divider()

            # =============================================
            # SIMULATED REVIEW COMPARISON
            # =============================================

            st.markdown(
                "#### Timed assisted versus unassisted review"
            )

            participant = st.text_input(
                "Study participant ID",
                key="clx_participant"
            )

            if st.button(
                "Assign randomized review task"
            ):
                if not participant.strip():
                    st.error(
                        "Enter a participant ID."
                    )

                else:
                    session_id = secrets.token_hex(12)

                    condition = secrets.choice([
                        "assisted",
                        "unassisted"
                    ])

                    case_id = secrets.choice(
                        sorted(actions.claim_id.unique())
                    )

                    with cx:
                        cx.execute(
                            """
                            INSERT INTO pathway_sessions
                            (
                                id, reviewer, case_id,
                                condition, started
                            )
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                session_id,
                                participant.strip(),
                                case_id,
                                condition,
                                time.time()
                            )
                        )

                    st.session_state[
                        "clx_session"
                    ] = session_id

            active_session = st.session_state.get(
                "clx_session"
            )

            if active_session:
                session = cx.execute(
                    """
                    SELECT case_id, condition, ended
                    FROM pathway_sessions
                    WHERE id=?
                    """,
                    (active_session,)
                ).fetchone()

                if session:
                    case_id, condition, ended = session

                    st.markdown(
                        f"**Assigned condition:** {condition}"
                    )

                    st.markdown(
                        f"**Assigned case:** {case_id}"
                    )

                    case_actions = actions[
                        actions.claim_id == case_id
                    ]

                    case_documents = docs[
                        docs.obligation_id.isin(
                            case_actions.obligation_id
                        )
                    ]

                    if condition == "assisted":
                        st.dataframe(
                            case_actions[
                                [
                                    "obligation_id",
                                    "obligation_name",
                                    "state"
                                ]
                            ],
                            hide_index=True,
                            use_container_width=True
                        )

                        st.caption(
                            "Displayed states are screening "
                            "results, not reference answers."
                        )

                    available_columns = [
                        column
                        for column in (
                            "obligation_id",
                            "document_id",
                            "event_date",
                            "document_text"
                        )
                        if column in case_documents
                    ]

                    st.dataframe(
                        case_documents[available_columns],
                        hide_index=True,
                        use_container_width=True
                    )

                    if ended is None:
                        with st.form("clx_pilot_response"):
                            response = st.text_area(
                                "List unresolved actions, "
                                "source IDs and reasoning"
                            )

                            confidence = st.slider(
                                "Decision confidence",
                                1, 5, 3
                            )

                            workload = st.slider(
                                "Perceived workload",
                                1, 5, 3
                            )

                            completed = st.form_submit_button(
                                "Lock response and stop timer"
                            )

                        if completed:
                            if len(response.strip()) < 25:
                                st.error(
                                    "Provide a detailed answer "
                                    "with source references."
                                )

                            else:
                                with cx:
                                    cx.execute(
                                        """
                                        UPDATE pathway_sessions
                                        SET ended=?,
                                            answer=?,
                                            confidence=?,
                                            workload=?
                                        WHERE id=?
                                          AND ended IS NULL
                                        """,
                                        (
                                            time.time(),
                                            response.strip(),
                                            confidence,
                                            workload,
                                            active_session
                                        )
                                    )

                                st.success(
                                    "Response locked. Accuracy "
                                    "has not yet been independently scored."
                                )

                    else:
                        st.success(
                            "Review session already completed."
                        )

                    if st.button(
                        "Dismiss current session"
                    ):
                        st.session_state.pop(
                            "clx_session",
                            None
                        )

                        st.rerun()

        # =================================================
        # RESEARCH READINESS
        # =================================================

        with evaluation:
            st.subheader(
                "Scientific validation and release readiness"
            )

            st.markdown(
                "**Proposed research stretch targets:** "
                "100+ independently adjudicated challenging cases; "
                "unresolved-care sensitivity of at least 95%; "
                "false follow-ups at most 5%; "
                "source attribution correctness at least 98%; "
                "zero observed unsupported completion conclusions; "
                "at least 20% lower nurse review time; "
                "and at least a 10-percentage-point improvement "
                "in review decision accuracy."
            )

            st.caption(
                "These are planned targets. They are not achieved "
                "results or Yale admission criteria."
            )

            adjudicated = cx.execute(
                """
                SELECT COUNT(*)
                FROM pathway_adjudications
                """
            ).fetchone()[0]

            sessions = cx.execute(
                """
                SELECT condition,
                       COUNT(*),
                       AVG(ended-started),
                       AVG(workload)
                FROM pathway_sessions
                WHERE ended IS NOT NULL
                GROUP BY condition
                """
            ).fetchall()

            st.metric(
                "Locked adjudications in this workspace",
                adjudicated
            )

            if sessions:
                st.dataframe(
                    pd.DataFrame(
                        sessions,
                        columns=[
                            "Study arm",
                            "Completed sessions",
                            "Mean seconds",
                            "Mean workload"
                        ]
                    ),
                    hide_index=True,
                    use_container_width=True
                )

            gates = [
                (
                    "Unnecessary follow-ups",
                    "PARTIAL",
                    "Database blocks duplicate open tasks "
                    "inside this workspace. "
                    "Independent false-alert review is pending."
                ),
                (
                    "Missing records versus missing care",
                    "PARTIAL",
                    "Uncertainty is displayed. "
                    "Keyword mentions are not verified events."
                ),
                (
                    "Clinical prioritization",
                    "NOT VALIDATED",
                    "No approved clinical urgency model. "
                    "This application does not assign urgency."
                ),
                (
                    "External generalizability",
                    "NOT VALIDATED",
                    "Independent held-out clinical cases "
                    "and verified provenance are still required."
                ),
                (
                    "Independent accuracy",
                    "NOT VALIDATED",
                    f"{adjudicated} locked adjudications "
                    "in this workspace. Held-out accuracy "
                    "has not been established."
                ),
                (
                    "Unified workflow",
                    "IMPLEMENTED — USABILITY UNTESTED",
                    "Worklist, source pathway, follow-ups, "
                    "annotations and study tools are together."
                ),
                (
                    "Measured nurse benefit",
                    "NOT VALIDATED",
                    "A controlled, independently scored "
                    "reviewer study is still required."
                )
            ]

            st.dataframe(
                pd.DataFrame(
                    gates,
                    columns=[
                        "Research requirement",
                        "Current assessment",
                        "Evidence and limitations"
                    ]
                ),
                hide_index=True,
                use_container_width=True
            )

            st.warning(
                "Clinical deployment and benefit claims "
                "remain blocked pending qualified independent "
                "validation. Do not enter real patient "
                "identifiers into this synthetic demonstration."
            )

            report = {
                "generated_at": now(),
                "software_status": "Research prototype",
                "clinical_release_authorized": False,
                "independent_verification_required": True,
                "gates": gates
            }

            st.download_button(
                "Download research status JSON",
                json.dumps(report, indent=2),
                file_name="claimslens_research_status.json",
                mime="application/json"
            )

    finally:
        cx.close()
