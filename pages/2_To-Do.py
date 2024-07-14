import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from streamlit_card import card
from streamlit_extras.stodo import to_do
import requests
from typing import Optional
import warnings
try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

BASE_API_URL = "http://127.0.0.1:7861/api/v1/run"
FLOW_ID = "93f52439-7377-4c88-8f3d-90f337a5b3f3"
ENDPOINT = "" # You can set a specific endpoint name in the flow settings

# You can tweak the flow by adding a tweaks dictionary
# e.g {"OpenAI-XXXXX": {"model_name": "gpt-4"}}
TWEAKS = {
  "File-TgxsV": {},
  "RecursiveCharacterTextSplitter-lKzw4": {},
  "OpenAIModel-B3EB9": {},
  "CustomComponent-QR8ED": {},
  "Prompt-0Oan3": {},
  "ChatOutput-JlUtf": {}
}

def run_flow(message: str,
  endpoint: str,
  output_type: str = "chat",
  input_type: str = "chat",
  tweaks: Optional[dict] = None,
  api_key: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if api_key:
        headers = {"x-api-key": api_key}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

st.title("To Do for the day based on the Voice Recorded")

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

response = run_flow(message="dummy text",endpoint=ENDPOINT or FLOW_ID,output_type="chat",input_type="chat",api_key=None)
try:
    todo_list=response['outputs'][0]['outputs'][0]['outputs']['message']['message']['text']
    if todo_list=="no tasks for today":
        print("no tasks for today")
        todo_list=""

except KeyError:
    print("no tasks today")
# Input for new to-do items
if todo_list:
    todo_list=todo_list.split("\n")
    print(todo_list)
for todo in todo_list:
    to_do(
        [(st.write, todo)],
        todo,
    )

new_item = st.text_input("Enter a new task", key="new_task")

# Button for adding a new task; calls add_to_do when clicked.
if st.button('Add Task'):
    add_to_do(new_item)

# Button for clearing all tasks; calls clear_to_dos when clicked.
if st.button('Clear Tasks'):
    clear_to_dos()
