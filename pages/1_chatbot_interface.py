import streamlit as st
import requests

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

    # Send POST request to backend with user message

    response = requests.post('http://your-backend-api-url/chat', json={"message": prompt})

    if response.status_code == 200:
        bot_response = response.json().get('response')
        # Append bot response to session state and display it

        msg=bot_response


    else:
        msg="Error communicating with backend."


     # Append bot response to session state and display it



    if msg:

    #Append bot resposne to sesionstate

        st.seesion_state.messages.append({"role":"assistant","content":msg})

        st.chat_message("assistant").write(msg)