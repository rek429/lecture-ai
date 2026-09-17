import streamlit as st
from utils.session_state import initialize_session_state
from components.sidebar import render_sidebar
from components.lecture_form import render_lecture_form
from components.lecture_workspace import render_lecture_workspace
from components.transcription import render_transcription
from utils.lecture_state import restore_lecture_from_url
from components.lecture_dialogs import (
    confirm_new_lecture,
    confirm_delete_lecture,
)
from services.supabase_service import (
    get_or_create_user,
    get_lectures,
    delete_lecture_audio,
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
 

 # Load lectures
 
saved_lectures = get_lectures(
    CURRENT_USER_ID
)
# Restore the lecture from the URL after a browser refresh.
restore_lecture_from_url(
    saved_lectures
)


 # Sidebar

render_sidebar(
    saved_lectures,
    confirm_new_lecture,
    lambda lecture: confirm_delete_lecture(
        CURRENT_USER_ID,
        lecture
    ),
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
#lecture form
selected_audio = render_lecture_form(
    CURRENT_USER_ID
)
#Transcription
render_transcription(
    CURRENT_USER_ID,
    selected_audio
)
 # Lecture workspace

render_lecture_workspace(
    CURRENT_USER_ID
)
