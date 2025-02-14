import streamlit as st
from difflib import SequenceMatcher
from deepgram import Deepgram
import asyncio
import tempfile
import json
import os

def landing_page():
    st.title("🎵 Rap Analyzer & Music Comparison")
    st.markdown("""
    Welcome to the **Rapper’s Freestyle Analyzer**! This app allows you to:
    - Analyze your rap flow & rhyme patterns 🎤
    - Compare two songs to check for plagiarism 🎶
    - Connect with us for feedback 💬
    """)

    st.sidebar.success("Select a page above ☝️")

DEEPGRAM_API_KEY = "your_deepgram_api_key"

async def transcribe_audio(audio_path):
    """ Transcribes audio using Deepgram API """
    try:
        dg_client = Deepgram(DEEPGRAM_API_KEY)
        with open(audio_path, "rb") as audio:
            source = {"buffer": audio, "mimetype": "audio/wav"}  
            response = await dg_client.transcription.prerecorded(source, {"punctuate": True})
            return response["results"]["channels"][0]["alternatives"][0]["transcript"]
    except Exception as e:
        st.error(f"Error in transcription: {e}")
        return None

def rap_analyzer():
    st.title("🎤 Rap Analyzer")
    
    uploaded_file = st.file_uploader("Upload your rap audio (MP3, WAV)", type=["mp3", "wav"])
    
    if uploaded_file:
        st.success("File uploaded successfully!")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(uploaded_file.read())
            temp_audio_path = temp_audio.name

        if st.button("Analyze Rap"):
            transcript = asyncio.run(transcribe_audio(temp_audio_path))
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
