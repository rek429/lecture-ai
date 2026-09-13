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


# Authentication
if not st.user.is_logged_in:
    st.title("Lecture AI")
    st.write(
        "Sign in to save and access your lectures."
    )

    if st.button("Continue with Google"):
        st.login("google")

    st.stop()


CURRENT_USER_ID = st.user.sub


# One-time messages
if "save_message" in st.session_state:
    st.success(
        st.session_state.save_message
    )
    del st.session_state.save_message


if st.session_state.get("new_lecture_message"):
    st.success(
        "New lecture started."
    )
    del st.session_state.new_lecture_message


# Session state
if "transcript" not in st.session_state:
    st.session_state.transcript = None

if "notes" not in st.session_state:
    st.session_state.notes = None

if "course_name" not in st.session_state:
    st.session_state.course_name = ""

if "lecture_title" not in st.session_state:
    st.session_state.lecture_title = ""

if "lecture_saved" not in st.session_state:
    st.session_state.lecture_saved = False

if "input_version" not in st.session_state:
    st.session_state.input_version = 0


# Main heading
st.title("Lecture AI")

st.write(
    "Record a lecture, transcribe it locally, and generate study notes."
)


# Sidebar
st.sidebar.title("Lecture History")


# New lecture confirmation dialog
@st.dialog("Start a new lecture?")
def confirm_new_lecture():

    st.write(
        "Are you sure you want to start a new lecture?"
    )

    if (
        st.session_state.transcript
        and not st.session_state.lecture_saved
    ):
        st.warning(
            "Your current lecture has not been saved. "
            "Starting a new lecture will clear it."
        )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Cancel",
            use_container_width=True
        ):
            st.rerun()

    with col2:

        if st.button(
            "Start New Lecture",
            type="primary",
            use_container_width=True
        ):

            st.session_state.course_name = ""
            st.session_state.lecture_title = ""
            st.session_state.transcript = None
            st.session_state.notes = None
            st.session_state.lecture_saved = False

            # Forces fresh recording/upload widgets
            st.session_state.input_version += 1

            st.session_state.new_lecture_message = True

            st.rerun()


# New Lecture button
if st.sidebar.button(
    "New Lecture",
    use_container_width=True
):
    confirm_new_lecture()


# Load saved lectures
saved_lectures = load_lectures(
    CURRENT_USER_ID
)


if saved_lectures:

    lecture_options = {
        f"{lecture['course']} - {lecture['title']}": lecture
        for lecture in saved_lectures
    }

    selected_lecture_name = st.sidebar.selectbox(
        "Saved lectures",
        options=[
            "Select a lecture"
        ] + list(
            lecture_options.keys()
        )
    )

    if (
        selected_lecture_name
        != "Select a lecture"
    ):

        selected_lecture = lecture_options[
            selected_lecture_name
        ]

        if st.sidebar.button(
            "Open Lecture",
            use_container_width=True
        ):

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

            st.session_state.lecture_saved = True

            # Clear old recording/upload widgets
            st.session_state.input_version += 1

            st.rerun()

else:

    st.sidebar.write(
        "No saved lectures yet."
    )


# Lecture information
st.text_input(
    "Course",
    key="course_name",
    placeholder="e.g. CSE 109"
)

st.text_input(
    "Lecture title",
    key="lecture_title",
    placeholder="e.g. Pointers and Memory"
)


# Audio input
audio = st.audio_input(
    "Record lecture",
    key=(
        f"audio_input_"
        f"{st.session_state.input_version}"
    )
)


uploaded_audio = st.file_uploader(
    "Or upload an audio file",
    type=[
        "mp3",
        "wav",
        "m4a"
    ],
    key=(
        f"audio_upload_"
        f"{st.session_state.input_version}"
    )
)


selected_audio = None


if audio:

    st.audio(
        audio
    )

    selected_audio = audio


elif uploaded_audio:

    st.audio(
        uploaded_audio
    )

    selected_audio = uploaded_audio


# Transcription
if selected_audio:

    if st.button(
        "Transcribe Lecture"
    ):

        with st.spinner(
            "Transcribing locally..."
        ):

            st.session_state.transcript = (
                transcribe_audio(
                    selected_audio
                )
            )

        # New transcript means the lecture
        # has not been saved yet
        st.session_state.notes = None
        st.session_state.lecture_saved = False

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


    # Transcript tab
    with transcript_tab:

        st.write(
            st.session_state.transcript
        )


    # Notes tab
    with notes_tab:

        if st.session_state.notes:

            st.markdown(
                st.session_state.notes
            )

        else:

            st.info(
                "Generate notes to view them here."
            )


    # Chat tab
    with chat_tab:

        question = st.text_input(
            "Ask a question about this lecture"
        )

        if st.button(
            "Ask Lecture"
        ):

            if question.strip():

                with st.spinner(
                    "Thinking..."
                ):

                    answer = ask_lecture(
                        st.session_state.transcript,
                        question
                    )

                st.markdown(
                    answer
                )

            else:

                st.warning(
                    "Enter a question first."
                )


    # Generate notes
    if st.button(
        "Generate Notes"
    ):

        with st.spinner(
            "Generating study notes..."
        ):

            st.session_state.notes = (
                generate_notes(
                    st.session_state.transcript
                )
            )

        # Notes changed, so this version
        # needs to be saved again
        st.session_state.lecture_saved = False

        st.rerun()


    # Save lecture
    if (
        st.session_state.transcript
        and st.session_state.notes
    ):

        if st.button(
            "Save Lecture"
        ):

            save_lecture(
                CURRENT_USER_ID,
                st.session_state.course_name,
                st.session_state.lecture_title,
                st.session_state.transcript,
                st.session_state.notes
            )

            st.session_state.lecture_saved = True

            st.session_state.save_message = (
                "Lecture saved successfully."
            )

            st.rerun()