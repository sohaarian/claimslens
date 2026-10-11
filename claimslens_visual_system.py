from pathlib import Path
import html
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent

PAGES = {
    "portfolio": (
        "CLINICAL DEMO",
        "Evidence, not assumptions.",
        "Explore the original interactive heart, care labels, and source evidence.",
        "clinical"
    ),
    "00_Start_Here": (
        "OVERVIEW",
        "Care coordination, made clearer.",
        "Understand the problem, the workflow, and what ClaimsLens helps a reviewer investigate.",
        "overview"
    ),
    "01_Study_Design": (
        "STUDY DESIGN",
        "A question worth testing.",
        "Can nurse case managers find unresolved care more accurately with evidence-grounded AI?",
        "research"
    ),
    "2_Research_Validation": (
        "VALIDATION",
        "Evidence before claims.",
        "Understand what has been measured, what failed, and what is still unproven.",
        "research"
    ),
    "3_Research_Engineering": (
        "ENGINEERING",
        "Built for traceability.",
        "Follow the technical process from medical record to source-linked conclusion.",
        "sources"
    ),
    "04_Evidence_Graph": (
        "EVIDENCE GRAPH",
        "See the care story unfold.",
        "Connect dated clinical milestones to the documents supporting them.",
        "sources"
    ),
    "04_Care_Intelligence": (
        "CARE INTELLIGENCE",
        "Turn evidence gaps into action.",
        "Inspect the clinical records and decide which follow-up is necessary.",
        "workflow"
    ),
    "05_Clinical_Intelligence": (
        "CLINICAL INTELLIGENCE",
        "What needs attention?",
        "Review the medical evidence behind every open question.",
        "clinical"
    ),
    "06_Nurse_Workflow": (
        "NURSE WORKFLOW",
        "Close the care coordination loop.",
        "Find a gap, review the source, assign the work, and document what changed.",
        "workflow"
    ),
    "90_AssuranceNet_Research": (
        "SAFETY & ERRORS",
        "When should the system say unknown?",
        "Investigate conflicting evidence and unsupported completion conclusions.",
        "safety"
    ),
    "91_Clinical_Evidence_Study": (
        "REFERENCE LABELS",
        "Humans establish the reference.",
        "Independent clinical review is essential to evaluating model performance.",
        "research"
    ),
    "92_Evidence_Atlas": (
        "EVIDENCE ATLAS",
        "Explore the medical record collection.",
        "Visualize the types of care and clinical documentation ClaimsLens analyzes.",
        "sources"
    ),
    "93_Model_Study": (
        "MODEL STUDY",
        "Test the model, not the marketing.",
        "Compare methods using defensible evidence rather than unsupported accuracy claims.",
        "research"
    )
}


@st.cache_data(show_spinner=False)
def load_data():
    try:
        actions = pd.read_csv(
            ROOT / "prototype_data/obligations.csv"
        ).fillna("")

        documents = pd.read_csv(
            ROOT / "prototype_data/documents.csv"
        ).fillna("")

        return actions, documents

    except (
        OSError,
        ValueError,
        pd.errors.ParserError
    ):
        return pd.DataFrame(), pd.DataFrame()


def counts(frame, column, limit=10):
    if column not in frame.columns:
        return pd.DataFrame(
            columns=["name", "value"]
        )

    return (
        frame[column]
        .astype(str)
        .value_counts()
        .head(limit)
        .rename_axis("name")
        .reset_index(name="value")
    )


def draw_charts(kind, actions, documents):
    try:
        import plotly.graph_objects as go

    except ImportError:
        st.info(
            "Plotly is required for the visual analytics."
        )
        return

    states = counts(actions, "state")
    medical = counts(
        actions, "obligation_name", 8
    )
    sources = counts(
        documents, "source_type", 8
    )

    if states.empty:
        st.info(
            "No synthetic portfolio data available."
        )
        return

    palette = {
        "clinical": "#BBF36B",
        "overview": "#BBF36B",
        "workflow": "#61D7EB",
        "sources": "#89B7F7",
        "safety": "#FFAA83",
        "research": "#C8B6FE"
    }

    accent = palette.get(
        kind, "#BBF36B"
    )

    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#D9E4DF",
            size=11
        ),
        margin=dict(
            l=16,
            r=12,
            t=18,
            b=23
        ),
        height=290,
        showlegend=False
    )

    left, right = st.columns(
        [1.05, 1],
        gap="large"
    )

    with left:
        if kind in (
            "clinical",
            "overview",
            "safety"
        ):
            st.markdown(
                "**Medical action status**"
            )

            figure = go.Figure(
                go.Pie(
                    labels=states["name"],
                    values=states["value"],
                    hole=.7,
                    marker=dict(
                        colors=[
                            "#B7EF68",
                            "#53BEEA",
                            "#F5A46C",
                            "#BEA6FF",
                            "#EF719F",
                            "#70D9B5"
                        ]
                    ),
                    textinfo="percent",
                    textposition="outside"
                )
            )

            figure.add_annotation(
                text=(
                    str(
                        int(states["value"].sum())
                    )
                    + "<br>"
                    + '<span style="font-size:11px">'
                    + "care actions</span>"
                ),
                showarrow=False,
                font=dict(
                    size=22,
                    color="#FAFCF9"
                )
            )

        elif kind == "sources" and not sources.empty:
            st.markdown(
                "**Types of source documents**"
            )

            figure = go.Figure(
                go.Bar(
                    x=sources["value"][::-1],
                    y=sources["name"][::-1],
                    orientation="h",
                    marker_color=accent
                )
            )

        else:
            st.markdown(
                "**Documentary states**"
            )

            figure = go.Figure(
                go.Bar(
                    x=states["name"],
                    y=states["value"],
                    marker_color=accent
                )
            )

        figure.update_layout(**layout)

        figure.update_xaxes(
            showgrid=False,
            zeroline=False
        )

        figure.update_yaxes(
            showgrid=False,
            zeroline=False
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

    with right:
        if kind in (
            "clinical",
            "overview",
            "workflow"
        ) and not medical.empty:
            st.markdown(
                "**Most common medical actions**"
            )

            labels = medical

        elif kind == "research":
            st.markdown(
                "**Reference portfolio composition**"
            )

            labels = states

        elif not sources.empty:
            st.markdown(
                "**Medical source distribution**"
            )

            labels = sources

        else:
            st.markdown(
                "**Care action distribution**"
            )

            labels = states

        figure = go.Figure(
            go.Bar(
                x=labels["value"][::-1],
                y=labels["name"][::-1],
                orientation="h",
                marker_color=accent
            )
        )

        figure.update_layout(**layout)

        figure.update_xaxes(
            showgrid=False,
            zeroline=False
        )

        figure.update_yaxes(
            showgrid=False
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


def show_page(key):
    kicker, title, description, kind = PAGES.get(
        key,
        (
            key.replace("_", " ").upper(),
            "Understand the medical evidence.",
            "Explore the available evidence and its clinical meaning.",
            "clinical"
        )
    )

    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1440px !important;
            padding: 1rem clamp(.85rem,2.2vw,2rem) 4rem !important;
        }

        .block-container * {
            box-sizing: border-box;
            min-width: 0;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid #28332D;
        }

        [data-testid="stMetric"] {
            background: #111B17 !important;
            border: 1px solid #2D4033 !important;
            border-radius: 9px !important;
            padding: .85rem !important;
        }

        [data-testid="stMetricValue"] {
            font-size: clamp(1.1rem,1.9vw,1.85rem) !important;
        }

        [data-baseweb="tab-list"] {
            flex-wrap: wrap !important;
            gap: .5rem !important;
        }

        [data-testid="stDataFrame"],
        [data-testid="stPlotlyChart"] {
            max-width: 100% !important;
        }

        .cl-editorial {
            border-top: 1px solid #314236;
            border-bottom: 1px solid #314236;
            padding: 1.2rem 0;
            margin-bottom: 1.3rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1.5rem;
        }

        .cl-editorial-kicker {
            color: #BAEF70;
            font-size: 11px;
            font-weight: 750;
            letter-spacing: .16em;
            font-family: monospace;
        }

        .cl-editorial-title {
            color: #F6F9F4;
            font-size: clamp(1.65rem,3vw,2.65rem);
            line-height: 1.08;
            letter-spacing: -.065em;
            font-weight: 850;
            margin: .4rem 0;
        }

        .cl-editorial-description {
            color: #B6C6BB;
            font-size: .94rem;
            max-width: 750px;
            line-height: 1.55;
        }

        .cl-editorial-mark {
            color: transparent;
            -webkit-text-stroke: 1px #B7EF68;
            font-size: clamp(2.4rem,7vw,5.5rem);
            font-weight: 900;
            line-height: 1;
            opacity: .8;
        }

        /* Make old oversized banners compact,
           without hiding the original animated heart. */

        .cl-hero,
        .cl-header,
        .clg-top {
            height: auto !important;
            min-height: 0 !important;
            max-height: none !important;
            overflow: visible !important;
            padding: 1rem !important;
            margin: 0 0 1rem !important;
        }

        .cl-hero h1,
        .cl-header h1,
        .clg-title {
            font-size: clamp(1.25rem,2vw,1.8rem) !important;
            white-space: normal !important;
            overflow-wrap: anywhere !important;
            line-height: 1.2 !important;
        }

        /* Remove the previous generic banner
           if remnants of its CSS remain. */

        .clv-head,
        .clv-art,
        .clv-guide {
            display: none !important;
        }

        @media(max-width:760px) {
            .cl-editorial-mark {
                display: none;
            }

            .cl-editorial {
                padding: .8rem 0;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    number = {
        "overview": "00",
        "clinical": "01",
        "workflow": "02",
        "sources": "03",
        "research": "04",
        "safety": "05"
    }.get(kind, "06")

    st.markdown(
        '<div class="cl-editorial">'
        '<div>'
        '<div class="cl-editorial-kicker">'
        'CLAIMSLENS &nbsp;/&nbsp; '
        + html.escape(kicker)
        + '</div>'
        '<div class="cl-editorial-title">'
        + html.escape(title)
        + '</div>'
        '<div class="cl-editorial-description">'
        + html.escape(description)
        + '</div>'
        '</div>'
        '<div class="cl-editorial-mark">'
        + number
        + '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    actions, documents = load_data()

    st.caption(
        "VISUAL DATA EXPLORER  /  SYNTHETIC CLINICAL PORTFOLIO"
    )

    draw_charts(
        kind,
        actions,
        documents
    )

    st.caption(
        "Charts describe the synthetic dataset, "
        "not verified clinical outcomes."
    )

    st.divider()
