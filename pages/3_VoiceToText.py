import os
import streamlit as st
from dotenv import load_dotenv
from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech
import io
from docx import Document

# Load environment variables from .env file
load_dotenv()

# Ensure the environment variable is set
google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not google_application_credentials:
    raise Exception("GOOGLE_APPLICATION_CREDENTIALS environment variable not set or .env file is incorrect.")

# Function to convert MP3 to mono WAV
def convert_mp3_to_mono_wav(mp3_path, wav_path):
    audio = AudioSegment.from_mp3(mp3_path)
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

# Function to save transcription to a txt file
def save_to_txt(transcription, file_path):
    with open(file_path, "w") as text_file:
        text_file.write(transcription)

# Function to save transcription to a docx file
def save_to_docx(transcription, file_path):
    doc = Document()
    doc.add_paragraph(transcription)
    doc.save(file_path)

# Streamlit app
st.title("Audio Transcription App")

uploaded_file = st.file_uploader("Upload an MP3 file", type=["mp3"])

if uploaded_file is not None:
    # Save the uploaded file
    mp3_path = "uploaded_audio.mp3"
    with open(mp3_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    wav_path = "converted_audio.wav"
    convert_mp3_to_mono_wav(mp3_path, wav_path)

    st.audio(uploaded_file, format="audio/mp3")

    transcription = transcribe_audio(wav_path)
    if transcription:
        st.success("Transcription successful!")
        st.write(transcription)
        
        # Save transcription
        save_to_txt(transcription, "transcription.txt")
        save_to_docx(transcription, "transcription.docx")
        
        # Provide download links
        with open("transcription.txt", "rb") as text_file:
            st.download_button(
                label="Download Transcription as TXT",
                data=text_file,
                file_name="transcription.txt",
                mime="text/plain",
            )
        
        with open("transcription.docx", "rb") as docx_file:
            st.download_button(
                label="Download Transcription as DOCX",
                data=docx_file,
                file_name="transcription.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
    else:
        st.error("Transcription failed.")
