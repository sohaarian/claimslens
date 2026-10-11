
"""Consistent page identity for the eight ClaimsLens pages."""
import html
import streamlit as st

PAGES = {
    "portfolio": ("01", "Clinical Demo"),
    "06_Nurse_Workflow": ("02", "Nurse Care Workflow"),
    "05_Clinical_Intelligence": ("03", "Clinical Intelligence"),
    "04_Evidence_Graph": ("04", "Clinical Evidence Graph"),
    "01_Study_Design": ("05", "Study Design"),
    "91_Clinical_Evidence_Study": ("06", "Reference Labels"),
    "93_Model_Study": ("07", "Evidence Lab"),
    "90_AssuranceNet_Research": ("08", "Safety & Errors"),
}

def render_number(key):
    number, title = PAGES[key]

    st.markdown("""
    <style>
    /* Hide only the old, competing shared-page headings.
       Do not hide the animated ClaimsLens hero. */
    .cl-editorial,
    .cl-editorial-mark,
    .cl-fixed-intro,
    .cl-clean-section,
    .clv-head,
    .clv-art {
        display: none !important;
    }

    .block-container {
        max-width: 1360px !important;
        padding-left: clamp(.85rem,2.5vw,2.4rem) !important;
        padding-right: clamp(.85rem,2.5vw,2.4rem) !important;
        padding-bottom: 4rem !important;
    }

    .block-container * {
        box-sizing: border-box;
        min-width: 0;
    }

    .block-container h1,
    .block-container h2,
    .block-container h3 {
        overflow-wrap: anywhere !important;
        line-height: 1.3 !important;
    }

    .block-container h2 {
        margin-top: 1.5rem !important;
        margin-bottom: .9rem !important;
    }

    .block-container h3 {
        margin-top: 1.2rem !important;
        margin-bottom: .75rem !important;
    }

    .block-container p {
        line-height: 1.65 !important;
    }

    [data-testid="stMetric"] {
        border-radius: 12px !important;
        padding: 1rem !important;
        min-height: 105px;
    }

    [data-testid="stMetricLabel"] {
        line-height: 1.4 !important;
    }

    [data-testid="stMetricValue"] {
        font-size: clamp(1rem,1.6vw,1.65rem) !important;
        line-height: 1.25 !important;
        overflow-wrap: anywhere !important;
        font-variant-numeric: tabular-nums;
    }

    [data-baseweb="tab-list"] {
        flex-wrap: wrap !important;
        gap: .65rem !important;
        margin-bottom: 1rem !important;
    }

    [data-testid="stPlotlyChart"],
    [data-testid="stDataFrame"] {
        max-width: 100% !important;
    }

    .cl-page-id {
        display: flex;
        align-items: center;
        gap: 15px;
        margin: 1rem 0 1.2rem;
        padding: .85rem 0;
        border-top: 1px solid rgba(177,220,153,.3);
        border-bottom: 1px solid rgba(177,220,153,.16);
    }

    .cl-page-id-number {
        font-family: monospace;
        color: #BAEF70;
        font-weight: 800;
        font-size: 1.5rem;
        letter-spacing: -.04em;
        line-height: 1;
        min-width: 42px;
        font-variant-numeric: tabular-nums;
    }

    .cl-page-id-label {
        color: inherit;
        font-size: .94rem;
        font-weight: 750;
        line-height: 1.45;
    }

    .cl-page-id-sub {
        font-size: .76rem;
        color: #95BBA0;
        letter-spacing: .05em;
    }

    @media(max-width:760px) {
        .block-container {
            padding-left: .8rem !important;
            padding-right: .8rem !important;
        }

        .cl-page-id-number {
            font-size: 1.2rem;
            min-width: 30px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="cl-page-id">'
        '<div class="cl-page-id-number">'
        + html.escape(number)
        + '</div>'
        '<div>'
        '<div class="cl-page-id-sub">'
        'CLAIMSLENS / PAGE '
        + html.escape(number)
        + '</div>'
        '<div class="cl-page-id-label">'
        + html.escape(title)
        + '</div></div></div>',
        unsafe_allow_html=True
    )
