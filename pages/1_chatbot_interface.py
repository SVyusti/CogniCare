import os
import streamlit as st
import requests
from langflow.load import run_flow_from_json
from typing import Optional
import warnings
import json
try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None

BASE_API_URL = "http://127.0.0.1:7861/api/v1/run"
FLOW_ID = "5fe2bbc3-074b-4de5-bf88-85d97a77c0b7"
ENDPOINT = ""

TWEAKS = {
  "ChatInput-PE0SD": {},
  "ChatOutput-NUHQm": {},
  "OpenAIModel-lYZkI": {},
  "Prompt-qfdY1": {},
  "AstraDB-OP03E": {},
  "MistalAIEmbeddings-M7atU": {},
  "ParseData-Hmbm6": {}
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



# Sidebar for API key input (optional) and links
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)]()"

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by a custom backend")

# Initialize session state for messages if not already done
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Display existing chat messages from session state
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user input and communication with backend
if prompt := st.chat_input():

    # Append user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

     # Append bot response to session state and display it

    response=run_flow(message=prompt,
        endpoint=ENDPOINT or FLOW_ID,
        output_type="chat",
        input_type="chat",
        api_key=None
    )
    try:
        msg=response["outputs"][0]["outputs"][0]["messages"][0]["message"]
    except Exception as e:
        msg="Sorry, but I'm unable to provide an answer"


    if msg:
        st.session_state.messages.append({"role":"assistant","content":msg})
        st.chat_message("assistant").write(msg)