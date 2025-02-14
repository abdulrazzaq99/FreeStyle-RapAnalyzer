import streamlit as st
from difflib import SequenceMatcher
from deepgram import DeepgramClient, LiveOptions, PrerecordedOptions
import asyncio
import tempfile
import json
import os
from dotenv import load_dotenv


def landing_page():
    st.title("🎵 Rap Analyzer & Music Comparison")
    st.markdown("""
    Welcome to the **Rapper’s Freestyle Analyzer**! This app allows you to:
    - Analyze your rap flow & rhyme patterns 🎤
    - Compare two songs to check for plagiarism 🎶
    - Connect with us for feedback 💬
    """)

    st.sidebar.success("Select a page above ☝️")

# Replace with your Deepgram API Key
load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Ensure API key is set
if not DEEPGRAM_API_KEY:
    st.error("Deepgram API key is missing! Please check your .env file.")

def transcribe_audio(audio_path):
    """ Transcribe an audio file using Deepgram's latest API """
    if not os.path.exists(audio_path):
        st.error("No file uploaded")
        return "No file uploaded"

    try:
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)

        

        with open(audio_path, "rb") as buffer_data:
            payload = { 'buffer': buffer_data }  # Read file as bytes
            
        options = PrerecordedOptions(
            smart_format=True, model="nova-2", language="en-US"
        )

        # Correct method for file transcription
        response = deepgram.listen.prerecorded.v('1').transcribe_file(payload, options)
        print(response)

        # Extract transcript
        transcript = response.results.channels[0].alternatives[0].transcript if response.results else "No transcript available"

        return transcript

    except Exception as err:
        st.error(f"Error transcribing: {err}")
        print(f"ERROR: {err}")  # Debugging error message
        return "Error transcribing"

def rap_analyzer():
    """ Streamlit UI for Rap Analyzer """
    st.title("🎤 Rap Analyzer")

    uploaded_file = st.file_uploader("Upload your rap audio (MP3, WAV)", type=["mp3", "wav"])

    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")

        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(uploaded_file.read())
            temp_audio_path = temp_audio.name

        if st.button("Analyze Rap"):
            transcript = transcribe_audio(temp_audio_path)
            if transcript:
                st.subheader("Transcribed Lyrics:")
                st.write(transcript)
            else:
                st.error("Failed to transcribe audio.")

        # Clean up temporary file
        os.remove(temp_audio_path)

def music_comparison():
    st.title("🎶 Music Comparison")
    song1 = st.text_area("Enter Lyrics of Song 1")
    song2 = st.text_area("Enter Lyrics of Song 2")
    
    if st.button("Compare Songs"):
        if song1 and song2:
            similarity = SequenceMatcher(None, song1.lower(), song2.lower()).ratio() * 100
            st.subheader(f"Similarity Score: {similarity:.2f}%")
            if similarity > 70:
                st.warning("⚠️ High similarity detected! Possible plagiarism.")
            else:
                st.success("✅ The songs are significantly different.")
        else:
            st.error("Please enter lyrics for both songs.")

def contact_page():
    st.title("📩 Contact Us")
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    message = st.text_area("Your Message")
    
    if st.button("Submit"):
        if name and email and message:
            st.success("✅ Thank you for reaching out! We'll get back to you soon.")
        else:
            st.error("⚠️ Please fill out all fields.")

# Page Routing
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Rap Analyzer", "Music Comparison", "Contact Us"])

if page == "Home":
    landing_page()
elif page == "Rap Analyzer":
    rap_analyzer()
elif page == "Music Comparison":
    music_comparison()
elif page == "Contact Us":
    contact_page()
