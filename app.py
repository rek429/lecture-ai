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


# Lecture information
course_name = st.text_input(
    "Course",
    placeholder="e.g. CSE 109"
)

lecture_title = st.text_input(
    "Lecture title",
    placeholder="e.g. Pointers and Memory"
)


# Store results so they survive Streamlit reruns
if "transcript" not in st.session_state:
    st.session_state.transcript = None

if "notes" not in st.session_state:
    st.session_state.notes = None

if "course_name" not in st.session_state:
    st.session_state.course_name = ""

if "lecture_title" not in st.session_state:
    st.session_state.lecture_title = ""


# Audio input
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


# Transcription
if selected_audio:

    if st.button("Transcribe Lecture"):

        st.session_state.course_name = course_name
        st.session_state.lecture_title = lecture_title

        with st.spinner("Transcribing locally..."):
            st.session_state.transcript = transcribe_audio(
                selected_audio
            )

        # Clear old notes when a new transcript is created
        st.session_state.notes = None


# Lecture content
if st.session_state.transcript:

    st.divider()

    if st.session_state.course_name:
        st.write(
            f"**Course:** {st.session_state.course_name}"
        )

    if st.session_state.lecture_title:
        st.write(
            f"**Lecture:** {st.session_state.lecture_title}"
        )

    transcript_tab, notes_tab = st.tabs(
        [
            "Transcript",
            "Lecture Notes"
        ]
    )

    with transcript_tab:
        st.write(st.session_state.transcript)

    with notes_tab:

        if st.session_state.notes:
            st.markdown(st.session_state.notes)

        else:
            st.info(
                "Generate notes to view them here."
            )


    # Generate notes
    if st.button("Generate Notes"):

        with st.spinner("Generating study notes..."):
            st.session_state.notes = generate_notes(
                st.session_state.transcript
            )

        st.rerun()
