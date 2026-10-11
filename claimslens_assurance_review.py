"""ClaimsLens human-supervised review and validation extension.
Synthetic research use only. Not for clinical deployment.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import secrets
import sqlite3
import time

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DB = ROOT / "research_outputs" / "evidence_validation_v1.sqlite3"

STATUSES = [
    "OPEN", "CLOSED", "CANCELLED",
    "SUPERSEDED", "UNVERIFIABLE"
]

TASK_TYPES = [
    "Request missing medical record",
    "Confirm appointment status",
    "Verify authorization",
    "Confirm care completion with provider",
    "Escalate for nurse review",
    "Request clarification of conflicting notes",
]


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def db():
    DB.parent.mkdir(parents=True, exist_ok=True)

    cx = sqlite3.connect(str(DB), timeout=15)
    cx.execute("PRAGMA busy_timeout=15000")
    cx.execute("PRAGMA journal_mode=WAL")

    cx.executescript("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        claim_id TEXT NOT NULL,
        action_id TEXT NOT NULL,
        owner TEXT NOT NULL,
        task_type TEXT NOT NULL,
        rationale TEXT NOT NULL,
        evidence_id TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'OPEN',
        created TEXT NOT NULL,
        completed TEXT
    );

    CREATE TABLE IF NOT EXISTS independent_reviews (
        id INTEGER PRIMARY KEY,
        claim_id TEXT NOT NULL,
        action_id TEXT NOT NULL,
        reviewer TEXT NOT NULL,
        state TEXT NOT NULL,
        evidence_id TEXT NOT NULL,
        rationale TEXT NOT NULL,
        created TEXT NOT NULL,
        UNIQUE(action_id, reviewer)
    );

    CREATE TABLE IF NOT EXISTS adjudications (
        action_id TEXT PRIMARY KEY,
        adjudicator TEXT NOT NULL,
        state TEXT NOT NULL,
        evidence_id TEXT NOT NULL,
        rationale TEXT NOT NULL,
        created TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS pilot_sessions (
        id TEXT PRIMARY KEY,
        reviewer TEXT NOT NULL,
        claim_id TEXT NOT NULL,
        condition TEXT NOT NULL,
        started REAL NOT NULL,
        finished REAL,
        finding_count INTEGER,
        confidence INTEGER,
        workload INTEGER,
        answer TEXT
    );
    """)

    return cx


@st.cache_data(show_spinner=False)
def load_data():
    actions = pd.read_csv(
        ROOT / "prototype_data" / "obligations.csv",
        dtype=str
    ).fillna("")

    records = pd.read_csv(
        ROOT / "prototype_data" / "documents.csv",
        dtype=str
    ).fillna("")

    required_actions = {
        "claim_id", "obligation_id",
        "obligation_name", "state"
    }

    required_records = {
        "obligation_id", "document_id", "document_text"
    }

    if not required_actions.issubset(actions.columns):
        raise ValueError("Action dataset missing required columns.")

    if not required_records.issubset(records.columns):
        raise ValueError("Document dataset missing required columns.")

    return actions, records


def evidence_table(records):
    columns = [
        c for c in [
            "document_id",
            "event_date",
            "source_type",
            "document_text"
        ]
        if c in records.columns
    ]

    return records[columns].copy()


def interpretation(state):
    value = str(state).upper().strip()

    interpretations = {
        "OPEN":
            "Recorded as open. Confirm the current care status.",
        "UNVERIFIABLE":
            "Available documentation cannot establish the status.",
        "CLOSED":
            "Recorded as closed. Check whether authoritative "
            "completion evidence supports that statement.",
        "CANCELLED":
            "Recorded as cancelled. Check for a replacement plan.",
        "SUPERSEDED":
            "Recorded as superseded. Inspect the newer plan.",
    }

    return interpretations.get(
        value,
        "Unrecognized documentary state. Human review required."
    )


def show_workspace():
    st.divider()

    st.markdown(
        "## Integrated Evidence Assurance"
    )

    st.caption(
        "Human-supervised synthetic research workspace. "
        "A missing record is not proof of delayed or incomplete care."
    )

    try:
        actions, records = load_data()
    except Exception as error:
        st.error("Unable to load synthetic data: " + str(error))
        return

    cx = db()

    claims = sorted(
        actions["claim_id"].unique().tolist()
    )

    if not claims:
        st.warning("No synthetic claims available.")
        cx.close()
        return

    review_tab, labels_tab, pilot_tab, audit_tab = st.tabs([
        "One-case review",
        "Independent reference labels",
        "Timed nurse study",
        "Strict safety audit"
    ])

    # =====================================================
    # 1. ONE-CASE REVIEW
    # =====================================================

    with review_tab:
        st.markdown(
            "### Review the case, evidence and follow-up together"
        )

        claim = st.selectbox(
            "Select claim",
            claims,
            key="assurance_claim"
        )

        case_actions = actions[
            actions["claim_id"] == claim
        ].copy()

        case_actions["review_question"] = (
            case_actions["state"].map(interpretation)
        )

        st.dataframe(
            case_actions[
                [
                    "obligation_id",
                    "obligation_name",
                    "state",
                    "review_question"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        action_id = st.selectbox(
            "Select medical action",
            case_actions["obligation_id"].tolist(),
            key="assurance_action"
        )

        current = case_actions[
            case_actions["obligation_id"] == action_id
        ].iloc[0]

        linked = records[
            records["obligation_id"] == action_id
        ]

        st.info(
            interpretation(current["state"])
            + "\n\nThis is a documentary screening finding, "
            "not a clinical urgency score."
        )

        st.markdown("#### Source-linked medical records")

        if linked.empty:
            st.warning(
                "No linked document is available. "
                "Do not infer that care failed to occur."
            )
        else:
            st.dataframe(
                evidence_table(linked),
                use_container_width=True,
                hide_index=True
            )

        current_tasks = cx.execute(
            """
            SELECT id, owner, task_type, status
            FROM tasks
            WHERE action_id = ? AND status = 'OPEN'
            ORDER BY id DESC
            """,
            (action_id,)
        ).fetchall()

        if current_tasks:
            st.warning(
                f"{len(current_tasks)} open follow-up(s) "
                "already exist for this action."
            )

            st.dataframe(
                pd.DataFrame(
                    current_tasks,
                    columns=[
                        "ID", "Owner", "Task", "Status"
                    ]
                ),
                use_container_width=True,
                hide_index=True
            )

        st.markdown("#### Record a human-approved follow-up")

        with st.form("assurance_task_form"):
            owner = st.text_input(
                "Responsible nurse, reviewer or team"
            )

            task_type = st.selectbox(
                "Follow-up action",
                TASK_TYPES
            )

            source_id = st.selectbox(
                "Supporting source document",
                ["MISSING"] +
                linked["document_id"].astype(str).tolist()
            )

            rationale = st.text_area(
                "Why is this needed? "
                "What evidence or uncertainty prompted it?"
            )

            create_task = st.form_submit_button(
                "Save follow-up"
            )

        if create_task:
            if not owner.strip() or len(rationale.strip()) < 12:
                st.error(
                    "Specify an owner and a meaningful rationale."
                )

            elif current_tasks:
                st.error(
                    "An open follow-up already exists. "
                    "Review or resolve it before creating another."
                )

            else:
                with cx:
                    cx.execute(
                        """
                        INSERT INTO tasks
                        (
                            claim_id, action_id, owner,
                            task_type, rationale,
                            evidence_id, created
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            claim,
                            action_id,
                            owner.strip(),
                            task_type,
                            rationale.strip(),
                            source_id,
                            utc_now()
                        )
                    )

                st.success(
                    "Follow-up saved. "
                    "Medical care status was not changed."
                )

        st.markdown("#### Task history")

        history = cx.execute(
            """
            SELECT id, task_type, owner, status, rationale
            FROM tasks WHERE claim_id = ?
            ORDER BY id DESC LIMIT 50
            """,
            (claim,)
        ).fetchall()

        if history:
            st.dataframe(
                pd.DataFrame(
                    history,
                    columns=[
                        "ID", "Task", "Owner",
                        "Status", "Reason"
                    ]
                ),
                use_container_width=True,
                hide_index=True
            )

            pending_ids = [
                item[0] for item in history
                if item[3] == "OPEN"
            ]

            if pending_ids:
                to_close = st.selectbox(
                    "Follow-up task to close",
                    pending_ids
                )

                if st.button(
                    "Mark administrative follow-up complete"
                ):
                    with cx:
                        cx.execute(
                            """
                            UPDATE tasks
                            SET status = 'DONE', completed = ?
                            WHERE id = ? AND status = 'OPEN'
                            """,
                            (utc_now(), to_close)
                        )

                    st.success(
                        "Administrative task closed. "
                        "This does NOT confirm medical care completion."
                    )

    # =====================================================
    # 2. INDEPENDENT REFERENCE LABELING
    # =====================================================

    with labels_tab:
        st.markdown(
            "### Independently establish the documentary answer"
        )

        st.caption(
            "Two independent reviews, followed by adjudication "
            "by a different reviewer. Reviewer identities and "
            "clinical qualifications must be verified outside "
            "this prototype."
        )

        claim = st.selectbox(
            "Case for labeling",
            claims,
            key="reference_case"
        )

        case_actions = actions[
            actions["claim_id"] == claim
        ]

        action_id = st.selectbox(
            "Medical action for labeling",
            case_actions["obligation_id"].tolist(),
            key="reference_action"
        )

        linked = records[
            records["obligation_id"] == action_id
        ]

        st.dataframe(
            evidence_table(linked),
            use_container_width=True,
            hide_index=True
        )

        source_ids = (
            linked["document_id"].astype(str).tolist()
        )

        with st.form("independent_review"):
            reviewer = st.text_input(
                "Independent reviewer ID"
            )

            state = st.selectbox(
                "Reference documentary state",
                STATUSES
            )

            source_id = st.selectbox(
                "Source supporting this decision",
                ["MISSING"] + source_ids
            )

            reason = st.text_area(
                "Explain chronology, contradictions, "
                "negation and uncertainty."
            )

            submit = st.form_submit_button(
                "Lock independent review"
            )

        if submit:
            if not reviewer.strip() or len(reason.strip()) < 15:
                st.error(
                    "Reviewer ID and detailed reasoning required."
                )
            else:
                try:
                    with cx:
                        cx.execute(
                            """
                            INSERT INTO independent_reviews
                            (
                                claim_id, action_id,
                                reviewer, state,
                                evidence_id, rationale, created
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                claim,
                                action_id,
                                reviewer.strip(),
                                state,
                                source_id,
                                reason.strip(),
                                utc_now()
                            )
                        )

                    st.success(
                        "Independent review locked. "
                        "Not yet an adjudicated ground truth."
                    )

                except sqlite3.IntegrityError:
                    st.error(
                        "This reviewer already submitted "
                        "for this medical action."
                    )

        reviews = cx.execute(
            """
            SELECT reviewer, state, evidence_id
            FROM independent_reviews
            WHERE action_id = ?
            """,
            (action_id,)
        ).fetchall()

        st.caption(
            f"Independent reviews submitted: {len(reviews)}"
        )

        distinct_reviewers = {
            item[0] for item in reviews
        }

        if len(distinct_reviewers) >= 2:
            st.markdown("#### Third-reviewer adjudication")

            with st.form("reference_adjudication"):
                adjudicator = st.text_input(
                    "Adjudicator ID"
                )

                final_state = st.selectbox(
                    "Final documentary reference state",
                    STATUSES
                )

                final_source = st.selectbox(
                    "Supporting source",
                    ["MISSING"] + source_ids
                )

                final_reason = st.text_area(
                    "Explain the final decision and "
                    "resolve disagreements."
                )

                adjudicate = st.form_submit_button(
                    "Lock adjudicated answer"
                )

            if adjudicate:
                if (
                    not adjudicator.strip()
                    or adjudicator.strip() in distinct_reviewers
                ):
                    st.error(
                        "A separate third reviewer is required."
                    )

                elif len(final_reason.strip()) < 15:
                    st.error(
                        "Adjudication reasoning is required."
                    )

                else:
                    try:
                        with cx:
                            cx.execute(
                                """
                                INSERT INTO adjudications
                                (
                                    action_id, adjudicator,
                                    state, evidence_id,
                                    rationale, created
                                )
                                VALUES (?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    action_id,
                                    adjudicator.strip(),
                                    final_state,
                                    final_source,
                                    final_reason.strip(),
                                    utc_now()
                                )
                            )

                        st.success(
                            "Adjudicated reference saved and locked."
                        )

                    except sqlite3.IntegrityError:
                        st.error(
                            "An adjudication already exists "
                            "for this action."
                        )

    # =====================================================
    # 3. RANDOMIZED SIMULATED NURSE STUDY
    # =====================================================

    with pilot_tab:
        st.markdown(
            "### Test the question that actually matters"
        )

        st.write(
            "Do reviewers identify documentary care gaps "
            "more accurately, faster and with fewer false "
            "follow-ups when using ClaimsLens?"
        )

        st.caption(
            "This is a simulated feasibility study. "
            "Randomization alone does not establish "
            "comparability, blinding or clinical effectiveness."
        )

        participant = st.text_input(
            "Participant ID",
            key="pilot_participant"
        )

        if st.button(
            "Start randomized review session"
        ):
            if not participant.strip():
                st.error(
                    "Enter a participant ID."
                )
            else:
                session_id = secrets.token_hex(12)
                chosen_claim = secrets.choice(claims)
                condition = secrets.choice([
                    "Unassisted records",
                    "ClaimsLens assisted"
                ])

                with cx:
                    cx.execute(
                        """
                        INSERT INTO pilot_sessions
                        (
                            id, reviewer, claim_id,
                            condition, started
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            session_id,
                            participant.strip(),
                            chosen_claim,
                            condition,
                            time.time()
                        )
                    )

                st.session_state[
                    "assurance_session"
                ] = session_id

        session_id = st.session_state.get(
            "assurance_session"
        )

        if session_id:
            session = cx.execute(
                """
                SELECT claim_id, condition, finished
                FROM pilot_sessions WHERE id = ?
                """,
                (session_id,)
            ).fetchone()

            if session:
                claim, condition, finished = session

                st.markdown(
                    f"**Assigned condition:** {condition}"
                )

                st.markdown(
                    f"**Assigned case:** {claim}"
                )

                case_actions = actions[
                    actions["claim_id"] == claim
                ]

                linked = records[
                    records["obligation_id"].isin(
                        case_actions["obligation_id"]
                    )
                ]

                if condition == "ClaimsLens assisted":
                    st.dataframe(
                        case_actions[
                            [
                                "obligation_id",
                                "obligation_name",
                                "state"
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True
                    )

                    st.caption(
                        "Displayed states are system screening "
                        "results, not verified answers."
                    )

                st.markdown("#### Case records")

                st.dataframe(
                    evidence_table(linked),
                    use_container_width=True,
                    hide_index=True
                )

                if finished is None:
                    with st.form("complete_pilot_session"):
                        finding_count = st.number_input(
                            "Number of unresolved or "
                            "uncertain actions identified",
                            min_value=0,
                            max_value=50,
                            value=0
                        )

                        confidence = st.slider(
                            "Reviewer confidence (1–5)",
                            1, 5, 3
                        )

                        workload = st.slider(
                            "Perceived workload (1–5)",
                            1, 5, 3
                        )

                        answer = st.text_area(
                            "List action IDs, evidence IDs, "
                            "follow-up decisions and reasons."
                        )

                        finish = st.form_submit_button(
                            "Lock response and stop timer"
                        )

                    if finish:
                        if len(answer.strip()) < 20:
                            st.error(
                                "Include specific action IDs "
                                "and reasoning."
                            )
                        else:
                            with cx:
                                cx.execute(
                                    """
                                    UPDATE pilot_sessions
                                    SET finished = ?,
                                        finding_count = ?,
                                        confidence = ?,
                                        workload = ?,
                                        answer = ?
                                    WHERE id = ?
                                      AND finished IS NULL
                                    """,
                                    (
                                        time.time(),
                                        int(finding_count),
                                        int(confidence),
                                        int(workload),
                                        answer.strip(),
                                        session_id
                                    )
                                )

                            st.success(
                                "Study response locked. "
                                "Accuracy has not yet been "
                                "independently assessed."
                            )
                else:
                    st.success(
                        "Review session completed."
                    )

                if st.button(
                    "Clear active session from screen"
                ):
                    st.session_state.pop(
                        "assurance_session", None
                    )

    # =====================================================
    # 4. STRICT RESEARCH AND SAFETY AUDIT
    # =====================================================

    with audit_tab:
        st.markdown("### Research readiness")

        adjudicated = cx.execute(
            "SELECT COUNT(*) FROM adjudications"
        ).fetchone()[0]

        completed_reviews = cx.execute(
            """
            SELECT COUNT(*) FROM pilot_sessions
            WHERE finished IS NOT NULL
            """
        ).fetchone()[0]

        open_tasks = cx.execute(
            """
            SELECT COUNT(*) FROM tasks
            WHERE status = 'OPEN'
            """
        ).fetchone()[0]

        metrics = st.columns(4)

        metrics[0].metric(
            "Synthetic claims",
            len(claims)
        )

        metrics[1].metric(
            "Care actions",
            len(actions)
        )

        metrics[2].metric(
            "Adjudicated references",
            adjudicated
        )

        metrics[3].metric(
            "Completed pilot sessions",
            completed_reviews
        )

        st.caption(
            f"Open follow-up tasks in this module: {open_tasks}"
        )

        st.markdown("#### Recorded documentary states")

        st.bar_chart(
            actions["state"].value_counts()
        )

        results = cx.execute(
            """
            SELECT condition,
                   COUNT(*),
                   AVG(finished - started),
                   AVG(workload)
            FROM pilot_sessions
            WHERE finished IS NOT NULL
              AND finished >= started
            GROUP BY condition
            """
        ).fetchall()

        if results:
            st.markdown(
                "#### Exploratory timing and workload"
            )

            st.dataframe(
                pd.DataFrame(
                    results,
                    columns=[
                        "Study condition",
                        "Completed sessions",
                        "Mean review seconds",
                        "Mean reported workload"
                    ]
                ),
                use_container_width=True,
                hide_index=True
            )

            st.caption(
                "These summaries are descriptive only. "
                "They do not prove a difference in speed, "
                "accuracy, safety or clinical outcomes."
            )

        checks = [
            (
                "Unnecessary follow-ups",
                "PARTIAL",
                "Duplicate open tasks are blocked within "
                "this module. False alert rates remain unknown."
            ),
            (
                "Missing evidence versus delayed care",
                "PARTIAL",
                "Screening labels are distinguished from "
                "verified treatment outcomes."
            ),
            (
                "Clinical risk prioritization",
                "PARTIAL",
                "This module does not assign clinical urgency. "
                "A clinically reviewed triage policy is missing."
            ),
            (
                "Synthetic data generalization",
                "NOT RESOLVED",
                "Independent, externally sourced held-out "
                "test cases are still required."
            ),
            (
                "Independent accuracy",
                "NOT YET PROVEN",
                "Locked labels and adjudication are supported. "
                "Qualified human review and sufficient "
                "reference cases are still needed."
            ),
            (
                "Fragmented nurse workflow",
                "PARTIAL",
                "Case review, source evidence and follow-ups "
                "can be handled in one section, while "
                "existing research pages remain separate."
            ),
            (
                "Measured nurse benefit",
                "NOT YET PROVEN",
                "Timed randomized sessions are supported, "
                "but controlled, independently scored "
                "results are not yet available."
            )
        ]

        st.markdown("#### Strict weakness audit")

        st.dataframe(
            pd.DataFrame(
                checks,
                columns=[
                    "Weakness",
                    "Status",
                    "Evidence and limitation"
                ]
            ),
            use_container_width=True,
            hide_index=True
        )

        st.warning(
            "Do not claim validated clinical accuracy, "
            "improved care completion, fewer missed events, "
            "or nurse time savings until independent "
            "evaluation supports those claims."
        )

        protocol = {
            "name": "ClaimsLens simulated clinical review study",
            "status": "Pilot infrastructure only",
            "population": "Qualified nurse case managers to be recruited",
            "conditions": [
                "Unassisted records",
                "ClaimsLens assisted"
            ],
            "primary_outcome": (
                "Correct detection of unresolved care actions "
                "against independently adjudicated labels"
            ),
            "secondary_outcomes": [
                "False follow-up requests",
                "Unsupported closure decisions",
                "Time per review",
                "Perceived workload",
                "Source citation accuracy"
            ],
            "limits": [
                "Synthetic records",
                "No deployment claim",
                "No current proof of clinical benefit"
            ]
        }

        st.download_button(
            "Export study protocol",
            json.dumps(protocol, indent=2),
            file_name="claimslens_study_protocol.json",
            mime="application/json"
        )

    cx.close()
