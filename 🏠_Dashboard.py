import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from streamlit_card import card
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech
import io
from docx import Document
import requests
from typing import Optional
import warnings
try:
    from langflow.load import upload_file
except ImportError:
    warnings.warn("Langflow provides a function to help you upload files to the flow. Please install langflow to use it.")
    upload_file = None
import base64


def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def build_markup_for_logo(
    png_file,
    background_position="45% 10%",
    margin_top="10%",
    image_width="50%",
    image_height="",
):
    binary_string = get_base64_of_bin_file(png_file)
    return """
            <style>
                [data-testid="stSidebarNav"] {
                    background-image: url("data:image/png;base64,%s");
                    background-repeat: no-repeat;
                    background-position: %s;
                    margin-top: %s;
                    background-size: %s %s;
                }
            </style>
            """ % (
        binary_string,
        background_position,
        margin_top,
        image_width,
        image_height,
    )

def add_logos(png_file):
    logo_markup = build_markup_for_logo(png_file)
    st.markdown(
        logo_markup,
        unsafe_allow_html=True,
    )
add_logo("http://placekitten.com/120/120")
add_logos("Cogni.png")

BASE_API_URL = "http://127.0.0.1:7861/api/v1/run"
FLOW_ID = "4944269f-96a2-41d2-a3cb-11191de533ba"
ENDPOINT = "" # You can set a specific endpoint name in the flow settings

# Load environment variables from .env file
load_dotenv()

openai_api_key = os.getenv("API_KEY")
openai_base_url = os.getenv("BASE_URL")
mistral_api_key = os.getenv("MISTRAL_API_KEY")
astra_db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
astra_db_api_key = os.getenv("ASTRA_DB_API_KEY")

# Ensure the environment variable is set
google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not google_application_credentials:
    raise Exception("GOOGLE_APPLICATION_CREDENTIALS environment variable not set or .env file is incorrect.")

# Function to convert MP3 to mono WAV
def convert_mp3_to_mono_wav(complex_wav_path, wav_path):
    audio = AudioSegment.from_wav(complex_wav_path)
    mono_audio = audio.set_channels(1)  # Convert to mono
    mono_audio.export(wav_path, format="wav")

# Function to transcribe audio
def transcribe_audio(file_path):
    client = speech.SpeechClient()

    with io.open(file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        #sample_rate_hertz=16000,  # Ensure this matches your audio file's sample rate
        language_code="en-US",
    )

    try:
        response = client.recognize(config=config, audio=audio)

        # Extract transcription
        for result in response.results:
            return result.alternatives[0].transcript
    except Exception as e:
        st.error(f"Error during transcription: {e}")
        return None

# Function to save transcription to a docx file
def save_to_docx(transcription, file_path):
    doc = Document()
    doc.add_paragraph(transcription)
    doc.save(file_path)


# You can tweak the flow by adding a tweaks dictionary
# e.g {"OpenAI-XXXXX": {"model_name": "gpt-4"}}
TWEAKS = {
  "RecursiveCharacterTextSplitter-BoGCK": {},
  "AstraDB-I8vdZ": {},
  "MistalAIEmbeddings-8JwAE": {},
  "File-qyM1S": {}
}

#langflow integration
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

#streamlit app
st.markdown("<h1 style='text-align: center;'>CogniCare</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Enhancing lives of Dementia patients with AI</p>", unsafe_allow_html=True)
hasClicked = card(
        title="Activate",
        text="Click to start the CogniCare",
        image="http://placekitten.com/300/250",
    )


audio_bytes=audio_recorder()
if audio_bytes:
    st.audio(audio_bytes,format='audio/wav')
    audio_location="audios/audio_file.wav"
    wav_path = "converted_audios/converted_audio.wav"
    os.makedirs(os.path.dirname(audio_location), exist_ok=True)
    os.makedirs(os.path.dirname(wav_path), exist_ok=True)
    with open(audio_location, "wb") as audio_file:
        audio_file.write(audio_bytes)
    convert_mp3_to_mono_wav(audio_location, wav_path)
    transcription=transcribe_audio(wav_path)
    if transcription:
        st.success("Transcription successful!")
        st.write(transcription)

        # Save transcription
        doc_path = "transcript/transcription.docx"
        os.makedirs(os.path.dirname(doc_path), exist_ok=True)
        save_to_docx(transcription, doc_path)

        # Provide download links
        with open(doc_path, "rb") as docx_file:
            st.download_button(
                label="Download Transcription as DOCX",
                data=docx_file,
                file_name="transcription.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
    else:
        st.error("Transcription failed.")

    response = run_flow(message="dummy text",endpoint=ENDPOINT or FLOW_ID,output_type="chat",input_type="chat",api_key=None)
    print(response)
