import streamlit as st
from services.chat_service import ask_lecture
from services.transcription import transcribe_audio
from services.note_generator import generate_notes
from services.lecture_storage import save_lecture, load_lectures


st.set_page_config(
    page_title="Lecture AI",
    page_icon="🎙️",
    layout="wide"
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


st.title("Lecture AI")
st.write(
    "Record a lecture, transcribe it locally, and generate study notes."
)


# Lecture history
st.sidebar.title("Lecture History")

saved_lectures = load_lectures()

if saved_lectures:

    lecture_options = {
        f"{lecture['course']} - {lecture['title']}": lecture
        for lecture in saved_lectures
    }

    selected_lecture_name = st.sidebar.selectbox(
        "Saved lectures",
        options=[
            "Select a lecture"
        ] + list(lecture_options.keys())
    )

    if selected_lecture_name != "Select a lecture":

        selected_lecture = lecture_options[
            selected_lecture_name
        ]

        if st.sidebar.button("Open Lecture"):

            st.session_state.course_name = (
                selected_lecture["course"]
            )

            st.session_state.lecture_title = (
                selected_lecture["title"]
            )

            st.session_state.transcript = (
                selected_lecture["transcript"]
            )

            st.session_state.notes = (
                selected_lecture["notes"]
            )

            st.rerun()

else:
    st.sidebar.write("No saved lectures yet.")


# Lecture information
course_name = st.text_input(
    "Course",
    value=st.session_state.course_name,
    placeholder="e.g. CSE 109"
)

lecture_title = st.text_input(
    "Lecture title",
    value=st.session_state.lecture_title,
    placeholder="e.g. Pointers and Memory"
)


# Audio input
audio = st.audio_input(
    "Record lecture"
)

uploaded_audio = st.file_uploader(
    "Or upload an audio file",
    type=[
        "mp3",
        "wav",
        "m4a"
    ]
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

        with st.spinner(
            "Transcribing locally..."
        ):

            st.session_state.transcript = (
                transcribe_audio(
                    selected_audio
                )
            )

        # Clear old notes when a new transcript is created
        st.session_state.notes = None

        st.rerun()


# Lecture content
if st.session_state.transcript:

    st.divider()

    if st.session_state.course_name:
        st.write(
            f"**Course:** "
            f"{st.session_state.course_name}"
        )

    if st.session_state.lecture_title:
        st.write(
            f"**Lecture:** "
            f"{st.session_state.lecture_title}"
        )

    transcript_tab, notes_tab, chat_tab = st.tabs(
        [
            "Transcript",
            "Lecture Notes",
            "Chat"
        ]
    )


    with transcript_tab:

        st.write(
            st.session_state.transcript
        )


    with notes_tab:

        if st.session_state.notes:

            st.markdown(
                st.session_state.notes
            )

        else:

            st.info(
                "Generate notes to view them here."
            )
    with chat_tab:

        question = st.text_input(
            "Ask a question about this lecture"
        )

        if st.button("Ask Lecture"):

            if question.strip():

                with st.spinner("Thinking..."):
                    answer = ask_lecture(
                        st.session_state.transcript,
                        question
                    )

                st.markdown(answer)

            else:

                st.warning(
                    "Enter a question first."
                )


    # Generate notes
    if st.button("Generate Notes"):

        with st.spinner(
            "Generating study notes..."
        ):

            st.session_state.notes = (
                generate_notes(
                    st.session_state.transcript
                )
            )

        st.rerun()


    # Save lecture
    if (
        st.session_state.transcript
        and st.session_state.notes
    ):

        if st.button("Save Lecture"):

            file_path = save_lecture(
                st.session_state.course_name,
                st.session_state.lecture_title,
                st.session_state.transcript,
                st.session_state.notes
            )

            st.success(
                f"Lecture saved successfully: "
                f"{file_path}"
            )