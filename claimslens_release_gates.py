from pathlib import Path
import json
import io
import zipfile
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "research_outputs" / "release_evidence"

SPEC = {
    "external_cases": [
        "case_id", "provenance", "independent_source",
        "family", "held_out", "synthetic"
    ],
    "case_scores": [
        "case_id", "reviewer_id", "ground_truth_status",
        "predicted_status", "false_alert",
        "unsupported_closure", "source_correct"
    ],
    "nurse_study": [
        "session_id", "reviewer_id", "case_id", "arm",
        "seconds", "correct", "false_followup",
        "workload", "qualified_reviewer"
    ],
    "triage_signoff": [
        "reviewer_id", "credential_verified",
        "approved", "date", "protocol_version"
    ],
    "workflow_usability": [
        "reviewer_id", "qualified_reviewer",
        "completed", "steps", "navigation_errors", "seconds"
    ],
    "source_interpretation": [
        "case_id", "reference_status",
        "predicted_status", "missing_document",
        "incorrect_delayed_care"
    ],
    "followup_audit": [
        "action_id", "open_duplicate",
        "false_alert", "task_actionable"
    ]
}


def load_csv(name):
    file = EVIDENCE / (name + ".csv")

    if not file.exists():
        return None, "Missing " + file.name

    try:
        frame = pd.read_csv(
            file,
            dtype=str
        ).fillna("")
    except Exception as error:
        return None, "Unreadable file: " + str(error)

    missing = set(SPEC[name]) - set(frame.columns)

    if missing:
        return None, "Missing columns: " + ", ".join(sorted(missing))

    return frame, f"Loaded {len(frame)} records"


def positive(series):
    return series.astype(str).str.lower().isin(
        ["true", "1", "yes", "y"]
    )


def numeric(series):
    return pd.to_numeric(
        series,
        errors="coerce"
    )


def result(passed, evidence, requirement):
    return {
        "status": "PASS" if passed else "NOT PASSED",
        "evidence": evidence,
        "requirement": requirement
    }


def evaluate():
    frames = {}
    notes = {}

    for name in SPEC:
        frames[name], notes[name] = load_csv(name)

    checks = {}

    # 1. False alerts and unnecessary work
    frame = frames["followup_audit"]

    if frame is None or len(frame) < 60:
        checks["1. Unnecessary follow-ups"] = result(
            False,
            notes["followup_audit"],
            "At least 60 independently reviewed follow-up "
            "opportunities, with no duplicate open tasks."
        )
    else:
        duplicates = int(
            positive(frame.open_duplicate).sum()
        )

        false_alert_rate = positive(
            frame.false_alert
        ).mean()

        actionable_rate = positive(
            frame.task_actionable
        ).mean()

        passed = (
            duplicates == 0
            and false_alert_rate <= .10
            and actionable_rate >= .90
        )

        checks["1. Unnecessary follow-ups"] = result(
            passed,
            f"{len(frame)} reviews; "
            f"{duplicates} duplicates; "
            f"{false_alert_rate:.1%} false alerts; "
            f"{actionable_rate:.1%} actionable.",
            "Zero duplicate tasks, no more than 10% "
            "false alerts, at least 90% actionable."
        )

    # 2. Missing documents versus missing care
    frame = frames["source_interpretation"]

    if (
        frame is None
        or len(frame) < 60
        or not positive(frame.missing_document).any()
    ):
        checks["2. Evidence versus incomplete care"] = result(
            False,
            notes["source_interpretation"],
            "At least 60 independently reviewed cases "
            "including cases with missing medical records."
        )
    else:
        agreement = (
            frame.reference_status.str.upper()
            == frame.predicted_status.str.upper()
        ).mean()

        false_delays = int(
            positive(
                frame.incorrect_delayed_care
            ).sum()
        )

        checks["2. Evidence versus incomplete care"] = result(
            agreement >= .90 and false_delays == 0,
            f"Agreement: {agreement:.1%}; "
            f"unsupported delayed-care statements: {false_delays}.",
            "At least 90% documentary-state agreement "
            "and zero unsupported claims of delayed care."
        )

    # 3. Clinical prioritization governance
    frame = frames["triage_signoff"]

    passed = (
        frame is not None
        and len(frame) >= 2
        and frame.reviewer_id.nunique() >= 2
        and positive(frame.credential_verified).all()
        and positive(frame.approved).all()
        and frame.protocol_version.ne("").all()
    ) if frame is not None else False

    checks["3. Clinical prioritization"] = result(
        passed,
        notes["triage_signoff"],
        "Two distinct credential-verified reviewers "
        "must approve a versioned clinical prioritization policy. "
        "Submitted credentials require external verification."
    )

    # 4. Independent held-out data
    frame = frames["external_cases"]

    if frame is None:
        checks["4. Generalizability"] = result(
            False,
            notes["external_cases"],
            "At least 60 genuinely independent held-out "
            "non-synthetic cases from two source families."
        )
    else:
        independent = frame[
            ~positive(frame.synthetic)
            & positive(frame.held_out)
            & positive(frame.independent_source)
            & frame.provenance.ne("")
        ]

        passed = (
            len(independent) >= 60
            and independent.family.nunique() >= 2
            and independent.case_id.nunique()
            == len(independent)
        )

        checks["4. Generalizability"] = result(
            passed,
            f"{len(independent)} documented independent "
            f"held-out cases across "
            f"{independent.family.nunique()} source families.",
            "Independent data provenance, legal access, "
            "de-identification and source diversity "
            "must also be verified outside this software."
        )

    # 5. Accuracy against reference answers
    frame = frames["case_scores"]

    if frame is None or len(frame) < 60:
        checks["5. Independent accuracy"] = result(
            False,
            notes["case_scores"],
            "At least 60 independently adjudicated "
            "held-out cases with source-citation scoring."
        )
    else:
        accuracy = (
            frame.ground_truth_status.str.upper()
            == frame.predicted_status.str.upper()
        ).mean()

        unsupported = int(
            positive(frame.unsupported_closure).sum()
        )

        citation = positive(
            frame.source_correct
        ).mean()

        external = frames["external_cases"]

        held_out_ids = (
            set()
            if external is None
            else set(
                external.loc[
                    positive(external.held_out)
                    & positive(external.independent_source),
                    "case_id"
                ]
            )
        )

        passed = (
            frame.case_id.nunique() >= 60
            and len(frame) == frame.case_id.nunique()
            and set(frame.case_id).issubset(held_out_ids)
            and accuracy >= .90
            and citation >= .95
            and unsupported == 0
        )

        checks["5. Independent accuracy"] = result(
            passed,
            f"Status accuracy: {accuracy:.1%}; "
            f"citation correctness: {citation:.1%}; "
            f"unsupported closures: {unsupported}.",
            "At least 90% reference agreement, "
            "95% correct citations, zero unsupported "
            "closures, independent adjudication and "
            "verified held-out provenance."
        )

    # 6. Observed workflow usability
    frame = frames["workflow_usability"]

    if frame is None:
        checks["6. Workflow usability"] = result(
            False,
            notes["workflow_usability"],
            "At least six qualified reviewers and "
            "12 observed workflow trials."
        )
    else:
        qualified = frame[
            positive(frame.qualified_reviewer)
        ]

        completion = (
            positive(qualified.completed).mean()
            if len(qualified)
            else 0
        )

        navigation_errors = numeric(
            qualified.navigation_errors
        ).fillna(999).sum()

        passed = (
            qualified.reviewer_id.nunique() >= 6
            and len(qualified) >= 12
            and completion >= .90
            and navigation_errors == 0
        )

        checks["6. Workflow usability"] = result(
            passed,
            f"{qualified.reviewer_id.nunique()} reviewers; "
            f"{len(qualified)} trials; "
            f"{completion:.1%} completion; "
            f"{navigation_errors:g} navigation errors.",
            "At least 90% completed, no blocking "
            "navigation errors, independently observed."
        )

    # 7. Controlled nurse benefit
    frame = frames["nurse_study"]

    if frame is None:
        checks["7. Measured nurse benefit"] = result(
            False,
            notes["nurse_study"],
            "Controlled comparison with qualified reviewers "
            "and independently scored cases."
        )
    else:
        qualified = frame[
            positive(frame.qualified_reviewer)
        ].copy()

        assisted = qualified[
            qualified.arm == "assisted"
        ]

        unassisted = qualified[
            qualified.arm == "unassisted"
        ]

        a_accuracy = (
            positive(assisted.correct).mean()
            if len(assisted)
            else 0
        )

        b_accuracy = (
            positive(unassisted.correct).mean()
            if len(unassisted)
            else 0
        )

        a_false = (
            positive(assisted.false_followup).mean()
            if len(assisted)
            else 1
        )

        b_false = (
            positive(unassisted.false_followup).mean()
            if len(unassisted)
            else 0
        )

        a_time = (
            numeric(assisted.seconds).median()
            if len(assisted)
            else float("inf")
        )

        b_time = (
            numeric(unassisted.seconds).median()
            if len(unassisted)
            else 0
        )

        crossover_reviewers = (
            set(assisted.reviewer_id)
            & set(unassisted.reviewer_id)
        )

        passed = (
            len(assisted) >= 30
            and len(unassisted) >= 30
            and len(crossover_reviewers) >= 6
            and assisted.session_id.nunique() == len(assisted)
            and unassisted.session_id.nunique() == len(unassisted)
            and a_accuracy > b_accuracy
            and a_false <= b_false
            and a_time <= b_time
        )

        checks["7. Measured nurse benefit"] = result(
            passed,
            f"{len(assisted)} assisted and "
            f"{len(unassisted)} unassisted reviews; "
            f"accuracy {a_accuracy:.1%} versus {b_accuracy:.1%}; "
            f"false follow-ups {a_false:.1%} versus {b_false:.1%}; "
            f"median time {a_time:g} versus {b_time:g} seconds.",
            "At least 30 reviews per arm and six qualified "
            "crossover reviewers; higher accuracy with "
            "no increase in false follow-ups or review time. "
            "A prespecified statistical analysis is still required."
        )

    return checks


def show_page():
    st.title("Clinical Validation & Release Gates")

    st.caption(
        "ClaimsLens / independent evaluation / "
        "synthetic research prototype"
    )

    st.info(
        "This dashboard evaluates supplied evidence. "
        "It cannot independently verify reviewer credentials, "
        "patient consent, dataset provenance or clinical safety."
    )

    checks = evaluate()

    passed = sum(
        item["status"] == "PASS"
        for item in checks.values()
    )

    first, second, third = st.columns(3)

    first.metric("Passed", f"{passed}/7")
    second.metric("Open", 7 - passed)
    third.metric(
        "Clinical deployment",
        "BLOCKED" if passed < 7 else "REVIEW REQUIRED"
    )

    st.progress(passed / 7)

    for name, item in checks.items():
        st.markdown("### " + name)

        st.write("**Result:** " + item["status"])
        st.write(item["evidence"])

        st.caption(
            "Required: " + item["requirement"]
        )

        st.divider()

    if passed == 7:
        st.warning(
            "All seven local numerical gates passed. "
            "This does NOT constitute clinical validation "
            "or authorization to deploy. Independent auditing, "
            "governance and approvals remain necessary."
        )
    else:
        st.error(
            "Clinical release blocked. Unmet requirements "
            "must not be reported as validated results."
        )

    with st.expander("Evidence collection templates"):
        output = io.BytesIO()

        with zipfile.ZipFile(
            output, "w", zipfile.ZIP_DEFLATED
        ) as archive:
            for name, columns in SPEC.items():
                archive.writestr(
                    name + ".csv",
                    ",".join(columns) + "\n"
                )

        st.download_button(
            "Download seven data templates",
            output.getvalue(),
            file_name="claimslens_validation_templates.zip",
            mime="application/zip"
        )

        st.caption(
            "Place independently verified completed files in "
            "research_outputs/release_evidence/. Do not enter "
            "identifiable patient information into this prototype."
        )

    report = {
        "gates": checks,
        "passed": passed,
        "clinical_release_authorized": False,
        "independent_verification_required": True
    }

    st.download_button(
        "Export strict rubric report",
        json.dumps(report, indent=2),
        file_name="claimslens_strict_rubric.json",
        mime="application/json"
    )


if __name__ == "__main__":
    findings = evaluate()

    for name, item in findings.items():
        print(name, item["status"])
        print(" ", item["evidence"])

    print(
        "Passed",
        sum(x["status"] == "PASS" for x in findings.values()),
        "of 7"
    )

    print("Clinical authorization: NO")
