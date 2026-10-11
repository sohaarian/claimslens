
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent

STEPS = [
    ('portfolio_app.py', '01 Clinical Demo'),
    ('pages/06_Nurse_Workflow.py', '02 Nurse Care Workflow'),
    ('pages/05_Clinical_Intelligence.py', '03 Clinical Intelligence'),
    ('pages/04_Evidence_Graph.py', '04 Clinical Evidence Graph'),
    ('pages/01_Study_Design.py', '05 Study Design'),
    ('pages/91_Clinical_Evidence_Study.py', '06 Reference Labels'),
    ('pages/93_Model_Study.py', '07 Evidence Lab'),
    ('pages/90_AssuranceNet_Research.py', '08 Safety & Errors'),
]

ARCHIVE = [
    ("pages/2_Research_Validation.py",
     "Earlier validation results"),
    ("pages/3_Research_Engineering.py",
     "Engineering notes"),
    ("pages/92_Evidence_Atlas.py",
     "Evidence Atlas"),
    ("pages/00_Start_Here.py",
     "Earlier introduction")
]


def sidebar_navigation():
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    .cl-nav-heading {
        color: #bceba0;
        font-size: .72rem;
        font-weight: 750;
        letter-spacing: .13em;
        margin: .4rem 0 .8rem;
    }
    .cl-nav-caption {
        color: #a6bca9;
        font-size: .78rem;
        line-height: 1.5;
        margin: .6rem 0 1rem;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink"] {
        border-radius: 11px;
        padding: .32rem .3rem;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(
            '<div class="cl-nav-heading">'
            'CLAIMSLENS STUDY</div>',
            unsafe_allow_html=True
        )

        st.caption(
            "Clinical evidence verification"
        )

        for filename, label in STEPS:
            if (ROOT / filename).is_file():
                st.page_link(
                    filename,
                    label=label
                )

        st.markdown(
            '<div class="cl-nav-caption">'
            'Start with the clinical demo. '
            'The next four steps explain how '
            'we test the system.'
            '</div>',
            unsafe_allow_html=True
        )

        with st.expander("Earlier work and reference pages"):
            for filename, label in ARCHIVE:
                if (ROOT / filename).is_file():
                    st.page_link(
                        filename,
                        label=label
                    )
