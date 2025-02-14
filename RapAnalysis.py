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
    """Transcribe an audio file using Deepgram's API and return the full response."""
    if not os.path.exists(audio_path):
        st.error("No file uploaded")
        return None

    try:
        # Initialize Deepgram client
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)

        # Set transcription options
        options = PrerecordedOptions(
            smart_format=True, model="nova-2", language="en-US"
        )

        # Open the audio file and read it as bytes
        with open(audio_path, "rb") as audio_file:
            payload = {'buffer': audio_file}

            # Transcribe the file using the correct method
            response = deepgram.listen.prerecorded.v('1').transcribe_file(payload, options, timeout=30)

            # Debugging: Print the response to check if it's working
            print(response.to_json(indent=4))

            # Return the full response object
            return response

    except Exception as err:
        st.error(f"Error transcribing: {err}")
        print(f"ERROR: {err}")  # Debugging error message
        return None

def find_rhyme_pairs(words):
    """Find pairs of words that rhyme."""
    # Simple rhyme detection: check if the last 2-3 letters match
    rhyme_pairs = []
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            if words[i][-3:].lower() == words[j][-3:].lower():
                rhyme_pairs.append((words[i], words[j]))
    return rhyme_pairs

def calculate_rap_speed(flow_data):
    """
    Calculate the rap speed rating based on word timings.
    """
    if not flow_data:
        return 0

    # Calculate the duration of each word
    word_durations = [end - start for _, start, end in flow_data]

    # Calculate the average time per word
    avg_time_per_word = sum(word_durations) / len(word_durations)

    # Normalize the rap speed rating (0 to 10)
    if avg_time_per_word < 0.2:
        return 10  # Extremely fast
    elif avg_time_per_word < 0.3:
        return 9
    elif avg_time_per_word < 0.4:
        return 8
    elif avg_time_per_word < 0.5:
        return 7
    elif avg_time_per_word < 0.6:
        return 6
    elif avg_time_per_word < 0.7:
        return 5
    elif avg_time_per_word < 0.8:
        return 4
    elif avg_time_per_word < 0.9:
        return 3
    elif avg_time_per_word < 1.0:
        return 2
    else:
        return 1  # Very slow

def calculate_rap_rating(response):
    """
    Calculate an overall rap rating based on all analysis measures.
    """
    if not response:
        return 0

    # Extract words and their metadata from the response
    words = (
        response.results.channels[0].alternatives[0].words
        if response.results.channels and response.results.channels[0].alternatives
        else []
    )

    if not words:
        return 0

    # 1. Rhyme Density Analysis
    rhyme_pairs = find_rhyme_pairs([word["word"] for word in words])
    rhyme_density = len(rhyme_pairs) / len(words) if words else 0

    # 2. Flow Analysis (Word Timing)
    flow_data = [(word["word"], word["start"], word["end"]) for word in words]
    rap_speed_rating = calculate_rap_speed(flow_data)

    # 3. Word Complexity Analysis
    unique_words = set(word["word"] for word in words)
    word_complexity = len(unique_words) / len(words) if words else 0

    # 4. Confidence Analysis
    low_confidence_words = [word for word in words if word["confidence"] < 0.8]
    confidence_rating = 1 - (len(low_confidence_words) / len(words)) if words else 0

    # 5. Emphasis Analysis (Repeated Words)
    word_counts = {}
    for word in words:
        word_counts[word["word"]] = word_counts.get(word["word"], 0) + 1
    repeated_words = {word: count for word, count in word_counts.items() if count > 1}
    emphasis_rating = len(repeated_words) / len(words) if words else 0

    # Calculate overall rap rating (weighted average)
    overall_rating = (
        (rhyme_density * 0.3) +  # Rhyme density contributes 30%
        (rap_speed_rating * 0.2) +  # Rap speed contributes 20%
        (word_complexity * 0.2) +  # Word complexity contributes 20%
        (confidence_rating * 0.2) +  # Confidence contributes 20%
        (emphasis_rating * 0.1)  # Emphasis contributes 10%
    )

    # Normalize the rating to a scale of 0 to 10
    overall_rating = min(max(overall_rating * 10, 0), 10)

    return overall_rating

def rap_analyzer():
    """Streamlit UI for Rap Analyzer with Advanced Analysis."""
    st.title("🎤 Rap Analyzer")

    uploaded_file = st.file_uploader("Upload your rap audio (MP3, WAV)", type=["mp3", "wav"])

    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")

        # Save file to a known location
        temp_dir = tempfile.mkdtemp()  # Create a temporary directory
        temp_audio_path = os.path.join(temp_dir, uploaded_file.name)

        with open(temp_audio_path, "wb") as temp_audio:
            temp_audio.write(uploaded_file.read())

        if st.button("Analyze Rap"):
            # Transcribe the audio file
            response = transcribe_audio(temp_audio_path)
            if response:
                # Extract the transcript text
                transcript = (
                    response.results.channels[0].alternatives[0].transcript
                    if response.results.channels and response.results.channels[0].alternatives
                    else "No transcript available"
                )

                # Calculate the overall rap rating
                rap_rating = calculate_rap_rating(response)

                # Store the transcript and rating in session state
                st.session_state.transcript = transcript
                st.session_state.rap_rating = rap_rating
                st.session_state.response = response

            else:
                st.error("Failed to transcribe audio.")

        # Clean up temporary directory and file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

        # Display the transcript and rating if available
        if "transcript" in st.session_state and "rap_rating" in st.session_state:
            st.subheader("Transcribed Lyrics:")
            st.write(st.session_state.transcript)

            st.subheader("🎤 Rap Rating")
            st.write(f"**Overall Rap Rating:** {st.session_state.rap_rating:.1f}/10")

            # Option to display detailed analysis
            if st.checkbox("Show Detailed Analysis"):
                st.subheader("📊 Detailed Analysis")
                analyze_rap(st.session_state.response)

def analyze_rap(response):
    """
    Perform advanced analysis on the Deepgram response.
    """
    # Extract words and their metadata from the response
    words = (
        response.results.channels[0].alternatives[0].words
        if response.results.channels and response.results.channels[0].alternatives
        else []
    )

    if not words:
        st.warning("No word-level data available for analysis.")
        return

    # 1. Rhyme Density Analysis
    st.markdown("### 🎵 Rhyme Density")
    rhyme_pairs = find_rhyme_pairs([word["word"] for word in words])
    st.write(f"**Total Rhyme Pairs:** {len(rhyme_pairs)}")
    if rhyme_pairs:
        st.write("**Rhyme Pairs:**")
        for pair in rhyme_pairs:
            st.write(f"- {pair[0]} & {pair[1]}")

    # 2. Flow Analysis (Word Timing)
    st.markdown("### 🎶 Flow Analysis")
    flow_data = [(word["word"], word["start"], word["end"]) for word in words]
    st.write("**Word Timings:**")
    st.write(flow_data)

    # 3. Word Complexity Analysis
    st.markdown("### 📚 Word Complexity")
    unique_words = set(word["word"] for word in words)
    st.write(f"**Unique Words Used:** {len(unique_words)}")
    st.write("**Top 10 Unique Words:**")
    st.write(list(unique_words)[:10])

    # 4. Confidence Analysis
    st.markdown("### 🔍 Confidence Analysis")
    low_confidence_words = [word for word in words if word["confidence"] < 0.8]
    st.write(f"**Low Confidence Words (Confidence < 0.8):** {len(low_confidence_words)}")
    if low_confidence_words:
        st.write("**Words with Low Confidence:**")
        for word in low_confidence_words:
            st.write(f"- {word['word']} (Confidence: {word['confidence']:.2f})")

    # 5. Emphasis Analysis (Repeated Words)
    st.markdown("### 🔄 Emphasis Analysis")
    word_counts = {}
    for word in words:
        word_counts[word["word"]] = word_counts.get(word["word"], 0) + 1
    repeated_words = {word: count for word, count in word_counts.items() if count > 1}
    st.write(f"**Repeated Words:** {len(repeated_words)}")
    if repeated_words:
        st.write("**Most Repeated Words:**")
        for word, count in sorted(repeated_words.items(), key=lambda x: x[1], reverse=True)[:10]:
            st.write(f"- {word} (Repeated {count} times)")


        
        
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
