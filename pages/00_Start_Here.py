
import streamlit as st
import pandas as pd
from pathlib import Path

from claimslens_product import style, intro

st.set_page_config(
    page_title="ClaimsLens | Start Here",
    page_icon="◎",
    layout="wide"
)

from claimslens_visual_system import show_page
show_page('00_Start_Here')



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


st.title("ClaimsLens")
intro()

st.markdown("### See the clinical problem in 30 seconds")

with st.container(border=True):
    st.markdown("**Example · A patient needs an MRI**")

    a, b, c = st.columns(3)

    with a:
        st.success("ORDERED")
        st.caption("A doctor requested the MRI.")

    with b:
        st.info("AUTHORIZED")
        st.caption("An approval was documented.")

    with c:
        st.warning("NOT YET VERIFIED")
        st.caption("The file may lack a completion report.")

    st.write(
        "**Why this matters:** An AI or reviewer who "
        "treats approval as completion could overlook "
        "unfinished care. ClaimsLens makes the "
        "evidence gap visible."
    )

st.markdown("### Explore an actual synthetic case")

root = Path(__file__).resolve().parent.parent

try:
    obs = pd.read_csv(
        root / "prototype_data" / "obligations.csv"
    ).fillna("")

    if obs.empty:
        raise ValueError("No synthetic obligations found")

    view = obs[
        [
            "claim_id",
            "obligation_id",
            "obligation_name",
            "state"
        ]
    ].copy()

    view["claim_id"] = view["claim_id"].astype(str)

    choices = view["claim_id"].drop_duplicates().tolist()

    chosen = st.selectbox(
        "Choose a synthetic claim",
        choices
    )

    subset = view[
        view["claim_id"] == chosen
    ]

    st.dataframe(
        subset[
            ["obligation_name", "state"]
        ],
        hide_index=True,
        use_container_width=True
    )

    if st.button(
        "Open this claim in ClaimsLens",
        type="primary"
    ):
        st.session_state["pending_claim"] = chosen
        st.switch_page("portfolio_app.py")

except Exception as exc:
    st.warning(
        "Case preview unavailable: " + str(exc)
    )

st.divider()

st.markdown("### Two ways to explore")

c1, c2 = st.columns(2, gap="large")

with c1:
    with st.container(border=True):
        st.markdown("#### Clinical product")

        st.write(
            "Review queue, care coordination, "
            "claim quality, and clinical change tracking."
        )

        st.page_link(
            "portfolio_app.py",
            label="Open Clinical Workspace"
        )

with c2:
    with st.container(border=True):
        st.markdown("#### Research evidence")

        st.write(
            "Trace predictions, challenge the system, "
            "and independently evaluate its errors."
        )

        st.page_link(
            "pages/90_AssuranceNet_Research.py",
            label="Open AssuranceNet Research"
        )

st.caption(
    "Product promise: transparent care coordination. "
    "Research claim: not yet independently validated."
)
