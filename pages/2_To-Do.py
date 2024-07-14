import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from streamlit_card import card
from streamlit_extras.stodo import to_do

st.title("To-Do for the day")

to_do(
        [(st.write, "☕ Take my coffee")],
        "coffee",
    )
# to_do(
#         [(st.write, "🥞 Have a nice breakfast")],
#         "pancakes",
#     )
# to_do(
#         [(st.write, ":train: Go to work!")],
#         "work",
#     )

# Initialize the session state for the to-do list if it is not already initialized
if 'to_do_list' not in st.session_state:
    st.session_state.to_do_list = []

def add_to_do(item):
    if item:  # Ensure the item is not empty
        st.session_state.to_do_list.append(item)
        new_item = ''  # Clear input box after adding

# Function to clear all items from the to-do list
def clear_to_dos():
    st.session_state.to_do_list = []

# Display existing to-dos
if st.session_state.to_do_list:
    for item in st.session_state.to_do_list:
        st.write(f"☕ {item}")

# Input for new to-do items
new_item = st.text_input("Enter a new task", key="new_task")

# Button for adding a new task; calls add_to_do when clicked.
if st.button('Add Task'):
    add_to_do(new_item)

# Button for clearing all tasks; calls clear_to_dos when clicked.
if st.button('Clear Tasks'):
    clear_to_dos()
