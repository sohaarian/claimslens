import streamlit as st


from claimslens_ui import install_ui, brand_hero, first_time_guide, page_purpose
st.set_page_config(
    page_title="ClaimsLens Research & Validation",
    page_icon="◎",
    layout="wide",
)

install_ui()

brand_hero(
    "Research / Validation",
    "PROVE",
    "IT",
    "This page answers a different question from the Claims workspace: "
    "how well did the frozen ClaimsLens research system perform, how was it "
    "evaluated, and where did it fail?",
    "FROZEN V1 / LOCKED BENCHMARK / FAILURE ANALYSIS",
)

page_purpose(
    "What this page is for",
    "Use Research Validation to evaluate the scientific evidence behind "
    "ClaimsLens. The locked V1 benchmark remains separate from later "
    "AssuranceNet development experiments."
)

first_time_guide("validation")


st.markdown('\n<style>\n.stApp {\n    background:\n        radial-gradient(circle at 85% -10%,\n        rgba(190,255,55,.055), transparent 30%),\n        #080a08;\n    color: #f2f4ef;\n}\n\n.block-container {\n    max-width: 1220px;\n    padding-top: 2.8rem;\n    padding-bottom: 5rem;\n}\n\nhtml, body, [class*="css"] {\n    font-family:\n        Inter,\n        -apple-system,\n        BlinkMacSystemFont,\n        "Segoe UI",\n        sans-serif;\n}\n\nh1, h2, h3 {\n    color: #f3f5f0 !important;\n    letter-spacing: -.03em;\n}\n\nh1 {\n    font-weight: 650 !important;\n}\n\nh2 {\n    margin-top: 2.6rem !important;\n}\n\np, li, label {\n    color: #a6aea5;\n}\n\nsection[data-testid="stSidebar"] {\n    background: #090b09 !important;\n    border-right: 1px solid rgba(255,255,255,.08);\n}\n\ndiv[data-baseweb="select"] > div,\ndiv[data-baseweb="input"] > div,\ndiv[data-testid="stTextInput"] input {\n    background: #0d100d !important;\n    border: 1px solid rgba(255,255,255,.10) !important;\n    border-radius: 3px !important;\n    color: white !important;\n}\n\ndiv[data-testid="stMetric"] {\n    border-top: 1px solid rgba(255,255,255,.10);\n    padding-top: 1rem;\n}\n\ndiv[data-testid="stMetricLabel"] {\n    color: #7d877d !important;\n    text-transform: uppercase;\n    letter-spacing: .08em;\n    font-size: .68rem;\n}\n\ndiv[data-testid="stMetricValue"] {\n    color: #f4f6f1 !important;\n}\n\ndiv[data-testid="stExpander"] {\n    border: 1px solid rgba(255,255,255,.09) !important;\n    border-radius: 3px !important;\n    background: #0b0e0b !important;\n}\n\ndiv[data-testid="stDataFrame"] {\n    border: 1px solid rgba(255,255,255,.09);\n    border-radius: 3px;\n    overflow: hidden;\n}\n\nhr {\n    border-color: rgba(255,255,255,.08) !important;\n}\n\n#MainMenu {\n    visibility: hidden;\n}\n\nfooter {\n    visibility: hidden;\n}\n</style>\n', unsafe_allow_html=True)



st.markdown(
    """
    <style>
    .stApp {
        background: #080b10;
        color: #f5f7fb;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .eyebrow {
        font-size: 0.78rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #8f9bad;
        margin-bottom: 0.4rem;
    }

    .hero {
        font-size: 3.4rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 0.7rem;
    }

    .subtitle {
        color: #9ba7b8;
        font-size: 1.02rem;
        max-width: 950px;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: #0f141c;
        border: 1px solid #1e2938;
        border-radius: 16px;
        padding: 1.25rem 1.35rem;
        min-height: 125px;
    }

    .metric-number {
        font-size: 2rem;
        font-weight: 800;
    }

    .metric-label {
        color: #9aa7b8;
        font-size: 0.88rem;
    }

    .flow {
        background: #0f141c;
        border: 1px solid #1e2938;
        border-radius: 16px;
        padding: 1.25rem;
        text-align: center;
        min-height: 120px;
    }

    .flow-title {
        font-weight: 800;
        font-size: 1rem;
        margin-bottom: 0.35rem;
    }

    .flow-text {
        color: #9ba7b8;
        font-size: 0.86rem;
    }

    .safety-box {
        background: #11170f;
        border-left: 4px solid #dfff54;
        border-radius: 12px;
        padding: 1rem 1.15rem;
        margin-bottom: 1rem;
    }

    .limitation-box {
        background: #17100f;
        border-left: 4px solid #ff9d76;
        border-radius: 12px;
        padding: 1rem 1.15rem;
        margin-bottom: 0.8rem;
    }

    .research-box {
        background: #0d1720;
        border-left: 4px solid #73e3ff;
        border-radius: 12px;
        padding: 1rem 1.15rem;
        margin-bottom: 0.8rem;
    }

    .small-note {
        color: #8f9bad;
        font-size: 0.82rem;
    }

    .protocol-box {
        background: #0f141c;
        border-left: 4px solid #73e3ff;
        border-radius: 12px;
        padding: 1rem 1.15rem;
        margin-bottom: 1rem;
    }

    .provenance-box {
        background: #0f141c;
        border: 1px solid #1e2938;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.7rem;
    }

    .provenance-arrow {
        color: #8f9bad;
        text-align: center;
        font-size: 1.2rem;
        margin: 0.2rem 0;
    }

    @media (max-width: 1100px) {
        .hero {
            font-size: 2.6rem;
        }

        .flow {
            min-height: 0;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="eyebrow">Research & Validation</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero">Research Validation</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    ClaimsLens investigates whether evidence-constrained longitudinal
    reconstruction can determine what a workers' compensation record
    actually supports while avoiding unsupported closure.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Research question
# ---------------------------------------------------------


st.info(
    "This page reports the frozen V1 research evaluation. "
    "These results are separate from later AssuranceNet development experiments."
)


st.markdown("## Research question")

st.markdown(
    """
    <div class="research-box">
    <strong>
    Can AI reconstruct the documentary state of consequential obligations
    across a longitudinal workers' compensation record while respecting
    evidence authority, timing, prerequisites, and uncertainty?
    </strong>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Architecture
# ---------------------------------------------------------

st.markdown("## System architecture")

architecture = [
    (
        "1. Longitudinal records",
        "Multi-source claim documents with event dates, received dates, source types, and authors.",
    ),
    (
        "2. Evidence extraction",
        "A local language model extracts evidence without deciding the final documentary state.",
    ),
    (
        "3. Provenance & authority",
        "Evidence is evaluated by source, assertion status, timing, and documentary authority.",
    ),
    (
        "4. State reconstruction",
        "Deterministic rules reconstruct OPEN, CLOSED, CANCELLED, SUPERSEDED, or UNVERIFIABLE.",
    ),
    (
        "5. Human review",
        "ClaimsLens exposes the evidence, missing proof, blockers, and uncertainty for verification.",
    ),
]

for start in range(0, len(architecture), 2):
    row_items = architecture[start:start + 2]
    columns = st.columns(2)

    for column, (title, description) in zip(columns, row_items):
        with column:
            st.markdown(
                f"""
                <div class="flow">
                    <div class="flow-title">{title}</div>
                    <div class="flow-text">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------
# Locked benchmark
# ---------------------------------------------------------

st.markdown("## Locked benchmark evaluation")

st.write(
    "The final study used a researcher-adjudicated synthetic benchmark. "
    "The first development cases were kept out of the locked-test headline "
    "results, and the model architecture was frozen before final evaluation."
)

metrics = [
    ("120", "Synthetic benchmark episodes"),
    ("72", "Locked-test episodes"),
    ("80.6%", "ClaimsLens exact accuracy"),
    ("0.824", "ClaimsLens macro-F1"),
]

for start in range(0, len(metrics), 2):
    columns = st.columns(2)

    for column, (value, label) in zip(
        columns,
        metrics[start:start + 2],
    ):
        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-number">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("<br>", unsafe_allow_html=True)

secondary = [
    ("0", "Unsupported closure predictions"),
    ("1.000", "CLOSED precision"),
    ("0.909", "UNVERIFIABLE recall"),
]

for start in range(0, len(secondary), 2):
    columns = st.columns(2)

    for column, (value, label) in zip(
        columns,
        secondary[start:start + 2],
    ):
        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-number">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )



st.markdown("### Evaluation protocol transparency")

st.markdown(
    """
    <div class="protocol-box">
    The ClaimsLens V1 architecture, extraction logic, benchmark, and
    experiment runners were frozen before the final locked evaluation.
    Before any locked-test scores were inspected, the evaluation script
    was corrected to point to the finalized benchmark file and to score
    only the 72 episodes labeled <strong>LOCKED_TEST</strong>.
    This correction changed evaluation scope only; it did not change
    model predictions, prompts, extraction logic, state rules, or the
    locked benchmark cases.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Architecture comparison")

st.dataframe(
    {
        "Method": [
            "Direct LLM",
            "Structured Prompt",
            "ClaimsLens",
        ],
        "Exact Accuracy": [
            "37.5%",
            "26.4%",
            "80.6%",
        ],
        "Macro-F1": [
            "0.388",
            "0.311",
            "0.824",
        ],
        "Unsupported Closures": [
            "1",
            "9",
            "0",
        ],
    },
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Why UNVERIFIABLE matters
# ---------------------------------------------------------

st.markdown("## Why abstention matters")

st.markdown(
    """
    <div class="safety-box">
    <strong>ClaimsLens does not force a conclusion when the available
    record cannot support one.</strong><br><br>

    A claimant saying that an MRI occurred is evidence that completion
    was reported. It is not automatically equivalent to an imaging
    facility record or radiology report establishing that the study
    occurred. ClaimsLens can therefore return
    <strong>UNVERIFIABLE</strong> rather than converting plausible
    information into documentary fact.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Documentary states
# ---------------------------------------------------------


st.markdown("## Provenance reasoning example")

st.write(
    "The example below illustrates the distinction between a plausible "
    "real-world event and what the available record can actually establish."
)

st.markdown(
    """
    <div class="provenance-box">
        <strong>1. NCM note</strong><br>
        Source: nurse case manager<br>
        Assertion: AFFIRMED report<br>
        Evidence: “Worker reports MRI was completed yesterday.”
    </div>

    <div class="provenance-arrow">↓</div>

    <div class="provenance-box">
        <strong>2. Authority assessment</strong><br>
        The NCM note documents that completion was reported,
        but it is not authoritative evidence that the imaging study
        itself occurred.
    </div>

    <div class="provenance-arrow">↓</div>

    <div class="provenance-box">
        <strong>3. Missing authoritative proof</strong><br>
        No imaging-facility completion record and no radiology report
        are present as of the evaluation date.
    </div>

    <div class="provenance-arrow">↓</div>

    <div class="provenance-box">
        <strong>4. ClaimsLens output</strong><br>
        Documentary state:
        <strong>UNVERIFIABLE</strong><br>
        Reason:
        <strong>NON_AUTHORITATIVE_EVIDENCE_ONLY</strong>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## Documentary state model")

st.dataframe(
    {
        "State": [
            "OPEN",
            "CLOSED",
            "CANCELLED",
            "SUPERSEDED",
            "UNVERIFIABLE",
        ],
        "Meaning": [
            "The obligation remains active.",
            "Required closure evidence is present.",
            "The obligation was explicitly cancelled.",
            "The obligation was replaced by a later obligation.",
            "The available record cannot support a definitive documentary state.",
        ],
    },
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Known failure modes
# ---------------------------------------------------------

st.markdown("## Known failure modes")

st.write(
    "ClaimsLens is not presented as a perfect system. "
    "The locked evaluation exposed specific weaknesses that remain targets "
    "for future research."
)

failures = [
    (
        "OPEN-state sensitivity",
        "OPEN recall on the locked test was 0.429. "
        "The system can be overly conservative and move unresolved cases "
        "into UNVERIFIABLE.",
    ),
    (
        "UNVERIFIABLE reason classification",
        "Reason accuracy was 0.500, indicating that recognizing uncertainty "
        "was easier than consistently identifying the correct uncertainty subtype.",
    ),
    (
        "Blocker extraction",
        "The current blocker metric was weak in the locked evaluation. "
        "This requires better extraction and evaluation before deployment.",
    ),
    (
        "Synthetic evaluation",
        "The benchmark uses controlled synthetic workers' compensation records. "
        "Performance has not yet been established on real-world claim files.",
    ),
]

for title, text in failures:
    st.markdown(
        f"""
        <div class="limitation-box">
            <strong>{title}</strong><br>
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Human oversight
# ---------------------------------------------------------

st.markdown("## Human oversight")

st.markdown(
    """
    <div class="safety-box">
    <strong>ClaimsLens is decision support, not autonomous decision-making.</strong>
    <br><br>
    The system does not diagnose patients, determine treatment,
    adjudicate compensability, determine return-to-work status,
    or autonomously close claims. A human reviewer verifies source
    evidence before taking action.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Scope
# ---------------------------------------------------------

st.markdown("## Scope and limitations")

st.write(
    "ClaimsLens currently evaluates three obligation classes: "
    "diagnostic imaging, specialist consultations, and authorization requests."
)

st.write(
    "The current research does not establish clinical effectiveness, "
    "cost savings, return-to-work improvement, litigation outcomes, "
    "or product-market validation."
)

st.write(
    "Workers' compensation is the current evaluation domain. "
    "The broader methodological question is evidence-constrained reasoning "
    "over incomplete, longitudinal, multi-source healthcare records."
)


# ---------------------------------------------------------
# Future research
# ---------------------------------------------------------

st.markdown("## Next research phase")

st.markdown(
    """
    - Evaluate the architecture on appropriately governed real-world or de-identified records.
    - Improve blocker and prerequisite extraction.
    - Expand proposition-specific evidence-authority rules.
    - Measure run-to-run model stability.
    - Evaluate human-AI review workflows.
    - Add additional longitudinal obligation classes.
    - Study whether evidence assurance identifies consequential documentation gaps earlier than existing workflows.
    """
)


st.divider()

st.markdown(
    """
    <div class="small-note">
    Research prototype · Synthetic benchmark and portfolio data ·
    Results describe controlled documentary-state reconstruction performance
    and should not be interpreted as clinical validation.
    </div>
    """,
    unsafe_allow_html=True,
)
