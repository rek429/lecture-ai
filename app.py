import streamlit as st

from services.chat_service import ask_lecture
from services.transcription import transcribe_audio
from services.note_generator import generate_notes
from services.lecture_storage import (
    save_lecture,
    update_lecture,
    load_lectures,
    delete_lecture
)


st.set_page_config(
    page_title="Lecture AI",
    page_icon="🎙️",
    layout="wide"
)


# --------------------------------------------------
# Authentication
# --------------------------------------------------

if not st.user.is_logged_in:

    st.title("Lecture AI")

    st.write(
        "Sign in to save and access your lectures."
    )

    if st.button(
        "Continue with Google"
    ):
        st.login("google")

    st.stop()


CURRENT_USER_ID = st.user.sub


# --------------------------------------------------
# Session state
# --------------------------------------------------

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

if "current_lecture_filename" not in st.session_state:
    st.session_state.current_lecture_filename = None

if "input_version" not in st.session_state:
    st.session_state.input_version = 0

if "just_saved_message" not in st.session_state:
    st.session_state.just_saved_message = None


# --------------------------------------------------
# One-time messages
# --------------------------------------------------



if "new_lecture_message" in st.session_state:

    st.success(
        st.session_state.new_lecture_message
    )

    del st.session_state.new_lecture_message


if "delete_message" in st.session_state:

    st.success(
        st.session_state.delete_message
    )

    del st.session_state.delete_message


# --------------------------------------------------
# Dialogs
# --------------------------------------------------

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
            st.session_state.current_lecture_filename = None

            st.session_state.input_version += 1

            st.session_state.new_lecture_message = (
                "New lecture started."
            )

            st.rerun()


@st.dialog("Delete lecture?")
def confirm_delete_lecture(lecture):

    st.warning(
        f"Are you sure you want to delete "
        f"{lecture['course']} - "
        f"{lecture['title']}?"
    )

    st.write(
        "This action cannot be undone."
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
            "Delete Lecture",
            type="primary",
            use_container_width=True
        ):

            deleted = delete_lecture(
                CURRENT_USER_ID,
                lecture["filename"]
            )

            if deleted:

                st.session_state.course_name = ""
                st.session_state.lecture_title = ""
                st.session_state.transcript = None
                st.session_state.notes = None
                st.session_state.lecture_saved = False

                st.session_state.input_version += 1

                st.session_state.delete_message = (
                    "Lecture deleted."
                )

            else:

                st.session_state.delete_message = (
                    "Lecture could not be found."
                )

            st.rerun()


# --------------------------------------------------
# Load lectures
# --------------------------------------------------

saved_lectures = load_lectures(
    CURRENT_USER_ID
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title(
    "Lecture Library"
)
st.sidebar.markdown("### Account")

user_email = getattr(
    st.user,
    "email",
    "Signed in"
)

st.sidebar.write(
    user_email
)

if st.sidebar.button(
    "Switch Account",
    use_container_width=True
):
    st.logout()

if st.sidebar.button(
    "Log Out",
    use_container_width=True
):
    st.logout()

st.sidebar.divider()


if st.sidebar.button(
    "＋ New Lecture",
    use_container_width=True
):
    confirm_new_lecture()


# Group lectures by course
courses = {}

for lecture in saved_lectures:

    course = lecture["course"].strip()

    if not course:
        course = "Uncategorized"

    if course not in courses:
        courses[course] = []

    courses[course].append(
        lecture
    )


# Display folders
if courses:

    for course, lectures in courses.items():

        with st.sidebar.expander(
            f"📁 {course}"
        ):

            for lecture in lectures:

                st.markdown(
                    f"**{lecture['title']}**"
                )

                col1, col2 = st.columns(
                    [3, 1]
                )

                with col1:

                    if st.button(
                        "Open",
                        key=(
                            f"open_"
                            f"{lecture['filename']}"
                        ),
                        use_container_width=True
                    ):

                        st.session_state.course_name = (
                            lecture["course"]
                        )

                        st.session_state.lecture_title = (
                            lecture["title"]
                        )

                        st.session_state.transcript = (
                            lecture["transcript"]
                        )

                        st.session_state.notes = (
                            lecture["notes"]
                        )

                        st.session_state.lecture_saved = True

                        st.session_state.current_lecture_filename = lecture["filename"]

                        st.session_state.input_version += 1

                        st.rerun()

                with col2:

                    if st.button(
                        "🗑️",
                        key=(
                            f"delete_"
                            f"{lecture['filename']}"
                        ),
                        help="Delete lecture",
                        use_container_width=True
                    ):

                        confirm_delete_lecture(
                            lecture
                        )

else:

    st.sidebar.write(
        "No saved lectures yet."
    )


# --------------------------------------------------
# Main page
# --------------------------------------------------

st.title(
    "Lecture AI"
)

st.write(
    "Record a lecture, transcribe it locally, "
    "and generate study notes."
)
# --------------------------------------------------
# Account menu
# --------------------------------------------------

header_left, header_right = st.columns(
    [12, 1]
)

with header_right:

    with st.popover(
        "👤",
        use_container_width=True
    ):

        user_email = getattr(
            st.user,
            "email",
            "Signed in"
        )

        st.caption(
            "Signed in as"
        )

        st.write(
            user_email
        )

        st.divider()

        if st.button(
            "Switch Account",
            use_container_width=True
        ):
            st.logout()

        if st.button(
            "Log Out",
            use_container_width=True
        ):
            st.logout()

st.divider()

st.subheader(
    "New Lecture"
)


# --------------------------------------------------
# Course selection
# --------------------------------------------------

existing_courses = sorted(
    {
        lecture["course"].strip()
        for lecture in saved_lectures
        if lecture["course"].strip()
    }
)


course_options = (
    existing_courses
    + ["+ Create new course"]
)


# Figure out which option should appear selected
if (
    st.session_state.course_name
    in existing_courses
):

    default_course_index = (
        existing_courses.index(
            st.session_state.course_name
        )
    )

else:

    default_course_index = (
        len(course_options) - 1
    )


selected_course = st.selectbox(
    "Course",
    options=course_options,
    index=default_course_index,
    key=(
        f"course_selector_"
        f"{st.session_state.input_version}"
    ),
    filter_mode=None
)


if selected_course == "+ Create new course":

    new_course_name = st.text_input(
        "New course name",
        value=(
            st.session_state.course_name
            if (
                st.session_state.course_name
                not in existing_courses
            )
            else ""
        ),
        placeholder="e.g. CSE 109"
    )

    st.session_state.course_name = (
        new_course_name.strip()
    )

else:

    st.session_state.course_name = (
        selected_course
    )


# --------------------------------------------------
# Lecture title
# --------------------------------------------------
previous_title = st.session_state.lecture_title

lecture_title = st.text_input(
    "Lecture title",
    value=st.session_state.lecture_title,
    placeholder="e.g. Pointers and Memory"
)

if lecture_title != previous_title:
    st.session_state.lecture_title = lecture_title

    if st.session_state.transcript:
        st.session_state.lecture_saved = False

st.session_state.lecture_title = (
    lecture_title
)


# --------------------------------------------------
# Audio
# --------------------------------------------------

st.subheader(
    "Audio"
)


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


# --------------------------------------------------
# Transcription
# --------------------------------------------------

if selected_audio:

    if st.button(
        "Transcribe Lecture",
        type="primary"
    ):

        if not st.session_state.course_name:

            st.warning(
                "Choose or create a course first."
            )

        elif not st.session_state.lecture_title:

            st.warning(
                "Enter a lecture title first."
            )

        else:

            with st.spinner(
                "Transcribing locally..."
            ):

                st.session_state.transcript = (
                    transcribe_audio(
                        selected_audio
                    )
                )

            st.session_state.notes = None
            st.session_state.lecture_saved = False

            st.rerun()


# --------------------------------------------------
# Lecture workspace
# --------------------------------------------------

if st.session_state.transcript:

    st.divider()

    st.subheader(
        st.session_state.lecture_title
    )

    st.caption(
        st.session_state.course_name
    )


    transcript_tab, notes_tab, chat_tab = st.tabs(
        [
            "Transcript",
            "Lecture Notes",
            "Chat"
        ]
    )


    # ----------------------------------------------
    # Transcript tab
    # ----------------------------------------------

    with transcript_tab:

        st.write(
            st.session_state.transcript
        )


    # ----------------------------------------------
    # Notes tab
    # ----------------------------------------------

    with notes_tab:

        if st.session_state.notes:

            st.markdown(
                st.session_state.notes
            )

        else:

            st.info(
                "Generate notes to view them here."
            )


    # ----------------------------------------------
    # Chat tab
    # ----------------------------------------------

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


    # ----------------------------------------------
    # Generate notes
    # ----------------------------------------------

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

        st.session_state.lecture_saved = False

        st.rerun()


    # ----------------------------------------------
    # Save lecture
    # ----------------------------------------------
if (
    st.session_state.transcript
    and st.session_state.notes
):

    if not st.session_state.lecture_saved:

        if st.session_state.current_lecture_filename:
            button_text = "Save Changes"
        else:
            button_text = "Save Lecture"

        if st.button(
            button_text,
            type="primary"
        ):
            if not st.session_state.course_name:
                st.warning(
                    "Choose or create a course first."
                )

            elif not st.session_state.lecture_title:
                st.warning(
                    "Enter a lecture title first."
                )

            else:

                if st.session_state.current_lecture_filename:
                    update_lecture(
                        CURRENT_USER_ID,
                        st.session_state.current_lecture_filename,
                        st.session_state.course_name,
                        st.session_state.lecture_title,
                        st.session_state.transcript,
                        st.session_state.notes
                    )

                    st.session_state.just_saved_message = (
                        "Changes saved successfully."
                    )

                else:
                    filename = save_lecture(
                        CURRENT_USER_ID,
                        st.session_state.course_name,
                        st.session_state.lecture_title,
                        st.session_state.transcript,
                        st.session_state.notes
                    )

                    st.session_state.current_lecture_filename = filename

                    st.session_state.just_saved_message = (
                        "Lecture saved successfully."
                    )

                st.session_state.lecture_saved = True
                st.rerun()

    elif st.session_state.get(
        "just_saved_message"
    ):
        st.success(
            st.session_state.just_saved_message
        )

        st.session_state.just_saved_message = None

elif (
    st.session_state.transcript
    and st.session_state.notes
    and st.session_state.lecture_saved
):
    st.success(
        "Lecture is already saved."
    )