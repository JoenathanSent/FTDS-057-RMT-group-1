import streamlit as st
from main_page import run_page
from predict_price import run_predict_price
from streamlit_option_menu import option_menu

# 1. as sidebar menu
with st.sidebar:
    selected = option_menu(
        "Menu",
        [
            "EDA",
            "Inference",
        ],
        icons=[
            "",
            "magic",
        ],
        menu_icon="cast",
        default_index=0
    )

if selected == "EDA":
    run_page()
elif selected == "Inference":
    run_predict_price()