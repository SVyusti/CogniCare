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


st.title("CogniCare")
st.caption("Your everyday companion")
add_logo("http://placekitten.com/120/120")

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
    with open(audio_location, "wb") as audio_file:
        audio_file.write(audio_bytes)
    convert_mp3_to_mono_wav(audio_location, wav_path)
    transcription=transcribe_audio(wav_path)
    if transcription:
        st.success("Transcription successful!")
        st.write(transcription)

        # Save transcription
        save_to_docx(transcription, "transcription.docx")

        # Provide download links
        with open("transcript/transcription.docx", "rb") as docx_file:
            st.download_button(
                label="Download Transcription as DOCX",
                data=docx_file,
                file_name="transcription.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
    else:
        st.error("Transcription failed.")