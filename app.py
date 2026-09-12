import streamlit as st
from transcribe import transcribe_audio

st.set_page_config(
    page_title="Lecture AI",
    page_icon="🎙️",
    layout="wide"
)

st.title("Lecture AI")

st.write("Record a lecture or upload an existing recording.")

audio = st.audio_input("Record lecture")

uploaded_audio = st.file_uploader(
    "Or upload an audio file",
    type=["mp3", "wav", "m4a"]
)

selected_audio = None

if audio:
    st.audio(audio)
    selected_audio = audio

elif uploaded_audio:
    st.audio(uploaded_audio)
    selected_audio = uploaded_audio

if selected_audio:

    if st.button("Transcribe Lecture"):

        with st.spinner("Transcribing locally..."):

            transcript = transcribe_audio(selected_audio)

        st.subheader("Transcript")

        st.write(transcript)