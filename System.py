import pandas as pd
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
import Logistic as Logistic
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# scope biar bisa akses Google Sheet
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/drive']

# load credential
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# buka Google Sheet pakai nama file
sheet = client.open("DataBase").sheet1

# contoh tambah data
data = ["2025-10-21", "Barang Masuk", "PO123", "100 pcs"]
sheet.append_row(data)



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












