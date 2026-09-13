import streamlit as st

from services.transcription import transcribe_audio
from services.note_generator import generate_notes

st.set_page_config(
    page_title="Lecture AI",
    page_icon="🎙️",
    layout="wide"
)

st.title("Lecture AI")
st.write("Record a lecture, transcribe it locally, and generate study notes.")


# Store results so they survive Streamlit reruns
if "transcript" not in st.session_state:
    st.session_state.transcript = None

if "notes" not in st.session_state:
    st.session_state.notes = None


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
            st.session_state.transcript = transcribe_audio(selected_audio)

        # Clear old notes whenever a new transcript is created
        st.session_state.notes = None


if st.session_state.transcript:

    st.subheader("Transcript")

    st.write(st.session_state.transcript)

    if st.button("Generate Notes"):

        with st.spinner("Generating study notes..."):
            st.session_state.notes = generate_notes(
                st.session_state.transcript
            )


if st.session_state.notes:

    st.subheader("Lecture Notes")

    st.markdown(st.session_state.notes)

