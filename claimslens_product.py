
import html
import streamlit as st


def escape(value):
    return html.escape(str(value))


def style():
    st.markdown("""
    <style>
    .block-container {
        width: 100% !important;
        max-width: 1160px !important;
        padding: 1.4rem 1.6rem 3rem !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    .block-container * {
        box-sizing: border-box;
        min-width: 0;
    }

    .block-container p {
        line-height: 1.55;
        overflow-wrap: break-word;
    }

    .cl-intro {
        position: relative;
        display: flex;
        align-items: center;
        gap: 1.5rem;
        margin: 0 0 1.25rem;
        padding: 1.4rem 1.5rem;
        background: linear-gradient(
            115deg, #101e16, #1b3221
        );
        border: 1px solid rgba(171,221,147,.23);
        border-radius: 18px;
    }

    .cl-orbit {
        flex: 0 0 95px;
        width: 95px;
        height: 95px;
    }

    .cl-eyebrow {
        color: #addd8e;
        font-size: .71rem;
        font-weight: 700;
        letter-spacing: .13em;
        margin-bottom: .4rem;
    }

    .cl-heading {
        color: #f2f8ef;
        font-size: clamp(1.45rem,2.3vw,2rem);
        line-height: 1.18;
        font-weight: 750;
        letter-spacing: -.035em;
        margin-bottom: .4rem;
    }

    .cl-description {
        color: #c9ddcd;
        font-size: .93rem;
        line-height: 1.55;
        max-width: 770px;
    }

    .cl-section {
        margin: 1.1rem 0 1rem;
        padding: 0 0 1rem;
        border-bottom: 1px solid rgba(165,205,157,.17);
    }

    .cl-section-title {
        font-size: 1.3rem;
        font-weight: 730;
        letter-spacing: -.02em;
        color: #edf6e9;
        line-height: 1.3;
        margin-bottom: .4rem;
    }

    .cl-section-sub {
        color: #b8cdbb;
        font-size: .88rem;
        line-height: 1.55;
        max-width: 800px;
    }

    .cl-section-label {
        font-size: .67rem;
        font-weight: 720;
        color: #a8d987;
        letter-spacing: .12em;
        margin-bottom: .35rem;
    }

    [data-testid="stMetric"] {
        padding: .85rem !important;
        border: 1px solid rgba(164,204,151,.2);
        border-radius: 12px;
    }

    [data-baseweb="tab-list"] {
        display: flex !important;
        gap: .4rem !important;
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        padding: .4rem 0 .8rem !important;
        scrollbar-width: thin;
    }

    [data-baseweb="tab"] {
        white-space: nowrap !important;
        flex-shrink: 0 !important;
        height: auto !important;
        padding: .65rem .85rem !important;
        border-radius: 9px !important;
    }

    div[data-testid="stDataFrame"] {
        max-width: 100%;
    }

    @media (max-width: 700px) {
        .block-container {
            padding: .8rem .75rem 3rem !important;
        }

        .cl-intro {
            gap: .8rem;
            padding: 1rem;
        }

        .cl-orbit {
            width: 56px;
            height: 56px;
            flex-basis: 56px;
        }

        .cl-description {
            font-size: .83rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def orbit():
    return """
    <svg class="cl-orbit" viewBox="0 0 120 120"
         xmlns="http://www.w3.org/2000/svg"
         aria-label="ClaimsLens brand symbol">
      <defs>
        <radialGradient id="orbGradient">
          <stop stop-color="#d9ff9f"/>
          <stop offset=".45" stop-color="#a6e94f"/>
          <stop offset="1" stop-color="#39651d"/>
        </radialGradient>
      </defs>
      <circle cx="60" cy="60" r="19"
              fill="url(#orbGradient)"/>
      <circle cx="60" cy="60" r="31"
              stroke="#b9ed6b" stroke-width="1.5"
              fill="none" opacity=".8"/>
      <ellipse cx="60" cy="60" rx="50" ry="18"
               stroke="#87c84d" fill="none"
               opacity=".65"
               transform="rotate(-30 60 60)"/>
      <ellipse cx="60" cy="60" rx="20" ry="50"
               stroke="#87c84d" fill="none"
               opacity=".45"
               transform="rotate(-30 60 60)"/>
      <circle cx="100" cy="38" r="3"
              fill="#c5f587"/>
    </svg>
    """


PAGES = {
    "queue": (
        "CASE REVIEW",
        "Find the claims that need attention.",
        "Sort the portfolio, review the evidence gaps "
        "and open a claim."
    ),
    "coordination": (
        "CARE COORDINATION",
        "See what happened to the patient.",
        "Follow a medical action from the source "
        "documents to the next review step."
    ),
    "quality": (
        "QUALITY REVIEW",
        "Find missing or conflicting proof.",
        "Check the supporting records before "
        "accepting a finding."
    ),
    "lab": (
        "SAFETY TESTING",
        "Test the limits of automated review.",
        "Explore document changes and misleading "
        "instructions."
    ),
    "changes": (
        "CLINICAL TIMELINE",
        "See how the medical record changed.",
        "Compare dated notes and investigate "
        "possible care-status changes."
    ),
    "events": (
        "EVENT EXTRACTION",
        "Trace the evidence back to the note.",
        "Examine the actual wording that triggered "
        "each event."
    ),
    "decisions": (
        "EVIDENCE VERIFICATION",
        "Find out what the documents support.",
        "Compare decisions with and without "
        "verification safeguards."
    ),
    "benchmark": (
        "RESEARCH EVALUATION",
        "Measure performance against real labels.",
        "Use independently adjudicated cases "
        "before claiming accuracy."
    ),
    "safety": (
        "ROBUSTNESS TESTING",
        "Find the failure points.",
        "Examine contradictory and misleading "
        "documentation."
    ),
    "study": (
        "REVIEWER EVALUATION",
        "Measure whether ClaimsLens helps.",
        "Compare manual and assisted review "
        "with collected participant data."
    )
}


def intro(research=False):
    if research:
        heading = "AssuranceNet Research"
        description = (
            "Testing whether clinical event detection, "
            "document verification and uncertainty checks "
            "produce more dependable conclusions."
        )
        eyebrow = "CLAIMSLENS RESEARCH"
    else:
        heading = "ClaimsLens"
        description = (
            "Review medical records, check what happened "
            "and identify care that still needs follow-up."
        )
        eyebrow = "CLINICAL EVIDENCE INTELLIGENCE"

    st.markdown(
        '<div class="cl-intro">'
        + orbit()
        + '<div>'
        + '<div class="cl-eyebrow">'
        + escape(eyebrow)
        + '</div>'
        + '<div class="cl-heading">'
        + escape(heading)
        + '</div>'
        + '<div class="cl-description">'
        + escape(description)
        + '</div>'
        + '</div></div>',
        unsafe_allow_html=True
    )


def header(key):
    label, title, description = PAGES[key]

    st.markdown(
        '<div class="cl-section">'
        + '<div class="cl-section-label">'
        + escape(label)
        + '</div>'
        + '<div class="cl-section-title">'
        + escape(title)
        + '</div>'
        + '<div class="cl-section-sub">'
        + escape(description)
        + '</div></div>',
        unsafe_allow_html=True
    )


# CLAIMSLENS SIMPLIFIED NAVIGATION V7


# Native Streamlit navigation is enabled again.
def product_navigation():
    return None
