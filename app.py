import streamlit as st
from utils.session_state import initialize_session_state
from services.transcription import transcribe_audio
from components.sidebar import render_sidebar
from components.lecture_form import render_lecture_form
from components.lecture_workspace import render_lecture_workspace

from services.supabase_service import (
    get_or_create_user,
    get_courses,
    get_or_create_course,
    get_lectures,
    delete_supabase_lecture,
    create_audio_lecture,
    upload_lecture_audio,
    update_lecture_audio_path,
    download_lecture_audio,
    delete_lecture_audio,
    update_lecture_transcript,
)



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

    if st.button(
        "Continue with Google"
    ):
        st.login("google")

    st.stop()


current_user = get_or_create_user(
    st.user.sub,
    st.user.email
)

CURRENT_USER_ID = current_user["id"]


 # Session state

initialize_session_state()

 # One-time messages
 


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


 # Dialogs
 
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
            st.session_state.current_course_id = None
            st.session_state.current_lecture_id = None
            st.session_state.recorded_audio = None
            st.session_state.audio_saved = False
            st.session_state.audio_fingerprint = None


            st.session_state.input_version += 1
            st.session_state.course_version += 1


            st.session_state.new_lecture_message = (
                "New lecture started."
            )
            st.query_params.clear()


            st.rerun()


@st.dialog("Delete lecture?")
def confirm_delete_lecture(lecture):

    st.warning(
        f"Are you sure you want to delete "
        f"{lecture['courses']['name']} - "
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

            deleted = delete_supabase_lecture(
                CURRENT_USER_ID,
                lecture["id"]
            )

            if deleted:

                st.session_state.course_name = ""
                st.session_state.lecture_title = ""
                st.session_state.transcript = None
                st.session_state.notes = None
                st.session_state.lecture_saved = False
                st.session_state.current_lecture_id = None
                st.session_state.current_course_id = None
                st.session_state.recorded_audio = None
                st.session_state.audio_saved = False
                st.session_state.audio_fingerprint = None

                
                st.session_state.input_version += 1

                st.session_state.delete_message = (
                    "Lecture deleted."
                )

            else:

                st.session_state.delete_message = (
                    "Lecture could not be found."
                )

            st.rerun()


 # Load lectures
 
saved_lectures = get_lectures(
    CURRENT_USER_ID
)
# Restore the lecture from the URL after a browser refresh.
lecture_id_from_url = st.query_params.get("lecture")

if (
    lecture_id_from_url
    and st.session_state.current_lecture_id != lecture_id_from_url
):
    lecture_from_url = next(
        (
            lecture
            for lecture in saved_lectures
            if lecture["id"] == lecture_id_from_url
        ),
        None
    )

    if lecture_from_url:
        st.session_state.course_name = (
            lecture_from_url["courses"]["name"]
        )

        st.session_state.lecture_title = (
            lecture_from_url["title"]
        )

        st.session_state.transcript = (
            lecture_from_url["transcript"]
        )

        st.session_state.notes = (
            lecture_from_url["notes"]
        )

        st.session_state.current_lecture_id = (
            lecture_from_url["id"]
        )

        st.session_state.current_course_id = (
            lecture_from_url["course_id"]
        )

        st.session_state.lecture_saved = True
        st.session_state.course_version += 1


        if lecture_from_url.get("audio_path"):
            try:
                st.session_state.recorded_audio = (
                    download_lecture_audio(
                        lecture_from_url["audio_path"]
                    )
                )

                st.session_state.audio_saved = True

            except Exception:
                st.session_state.recorded_audio = None
                st.session_state.audio_saved = False

        else:
            st.session_state.recorded_audio = None
            st.session_state.audio_saved = False

    else:
        # Invalid/deleted lecture ID should not remain in the URL.
        st.query_params.clear()


 # Sidebar

render_sidebar(
    saved_lectures,
    confirm_new_lecture,
    confirm_delete_lecture,
)

 # Main page
 
st.title(
    "Lecture AI"
)

st.write(
    "Record a lecture, transcribe it locally, "
    "and generate study notes."
)
 # Account menu
 
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

selected_audio = render_lecture_form(
    CURRENT_USER_ID
)

 # Transcription
 
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

                new_transcript = transcribe_audio(
                    selected_audio
                )

            # Save the transcript to Supabase before
            # updating the interface.
            update_lecture_transcript(
                CURRENT_USER_ID,
                st.session_state.current_lecture_id,
                new_transcript
            )

            st.session_state.transcript = new_transcript
            st.session_state.notes = None
            st.session_state.lecture_saved = True

            st.rerun()

 # Lecture workspace

render_lecture_workspace(
    CURRENT_USER_ID
)
