import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from streamlit_card import card


st.title("CogniCare")
st.caption("Your everyday companion")

add_logo("http://placekitten.com/120/120")

hasClicked = card(
        title="Activate",
        text="Click to start the CogniCare",
        image="http://placekitten.com/300/250",
    )