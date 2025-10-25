import pandas as pd
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
import logistic_supabase as Logistic

st.markdown(
    """
    <h1 style='text-align: center; color: #2E86C1;'>
        Welcome
    </h1>
    """,
    unsafe_allow_html=True
)
# Feature
col1, col2, col3 = st.columns(3)
with col1:
    st.image("warehouse.png", width=100)
    if st.button("Logistic"):
        st.session_state.page = "Logistic"
with col2:
    if st.button("PPC"):
        st.session_state.page = "PPC"
with col3:
    if st.button("Produksi"):
        st.session_state.page = "Produksi"

if "page" not in st.session_state:
    st.session_state.page = "home"
if st.session_state.page == "Logistic":
    Logistic.show_page()












