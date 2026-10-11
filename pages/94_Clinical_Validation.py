import streamlit as st
st.set_page_config(page_title='ClaimsLens | Clinical Validation', layout='wide')
from claimslens_release_gates import show_page
show_page()
