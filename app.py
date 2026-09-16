import streamlit as st
from services.chat_service import ask_lecture
from services.transcription import transcribe_audio
from services.note_generator import generate_notes

from services.supabase_service import (
    get_or_create_user,
    get_courses,
    get_or_create_course,
    create_lecture,
    get_lectures,
    update_supabase_lecture,
    delete_supabase_lecture,
    save_chat_message,
    get_chat_messages,
    create_audio_lecture,
    upload_lecture_audio,
    update_lecture_audio_path,
    download_lecture_audio,
    delete_lecture_audio,
    update_lecture_transcript,
    update_lecture_notes,
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

if "course_version" not in st.session_state:
    st.session_state.course_version = 0

if "just_saved_message" not in st.session_state:
    st.session_state.just_saved_message = None

if "current_course_id" not in st.session_state:
    st.session_state.current_course_id = None

if "current_lecture_id" not in st.session_state:
    st.session_state.current_lecture_id = None

if "recorded_audio" not in st.session_state:
    st.session_state.recorded_audio = None

if "audio_saved" not in st.session_state:
    st.session_state.audio_saved = False


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

    course = lecture["courses"]["name"].strip()

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
                            f"{lecture['id']}"
                        ),
                        use_container_width=True
                    ):

                        st.session_state.course_name = (
                            lecture["courses"]["name"]
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

                        st.session_state.current_lecture_id = (
                            lecture["id"]
                        )

                        st.session_state.current_course_id = (
                            lecture["course_id"]
                        )

                        # Restore the permanently saved recording.
                        if lecture.get("audio_path"):
                            try:
                                st.session_state.recorded_audio = (
                                    download_lecture_audio(
                                        lecture["audio_path"]
                                    )
                                )
                                st.session_state.audio_saved = True

                            except Exception:
                                st.session_state.recorded_audio = None
                                st.session_state.audio_saved = False

                        else:
                            st.session_state.recorded_audio = None
                            st.session_state.audio_saved = False

                        st.session_state.input_version += 1
                        st.session_state.course_version += 1

                        st.query_params["lecture"] = lecture["id"]
                        st.rerun()


                with col2:

                    if st.button(
                        "🗑️",
                        key=(
                            f"delete_"
                            f"{lecture['id']}"
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

st.subheader(
    "New Lecture"
)


 # Course selection

supabase_courses = get_courses(
    CURRENT_USER_ID
)

existing_courses = sorted(
    [
        course["name"]
        for course in supabase_courses
    ]
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
        f"{st.session_state.course_version}"
    ),
    filter_mode=None
)


if selected_course == "+ Create new course":

    new_course_name = st.text_input(
        "New course name",
        value=(
            st.session_state.course_name
            if st.session_state.course_name not in existing_courses
            else ""
        ),
        placeholder="e.g. CSE 109"
    )

    new_course_name = new_course_name.strip()

    if new_course_name:

        if st.button("Create Course"):

            course = get_or_create_course(
                CURRENT_USER_ID,
                new_course_name
            )

            st.session_state.course_name = (
                course["name"]
            )
            st.session_state.current_course_id = (
                course["id"]
            )
            

            st.session_state.course_version += 1

            st.rerun()

else:

    st.session_state.course_name = (
        selected_course
    )

    selected_course_data = next(
        course
        for course in supabase_courses
        if course["name"] == selected_course
    )

    st.session_state.current_course_id = (
        selected_course_data["id"]
    )


# Lecture title

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


 # Audio
 
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
    # Only treat it as new audio if it is different from
    # the recording currently stored in session state.
    if (
        st.session_state.recorded_audio is None
        or audio.name != st.session_state.recorded_audio.name
    ):
        st.session_state.recorded_audio = audio
        st.session_state.audio_saved = False

    st.audio(st.session_state.recorded_audio)
    selected_audio = st.session_state.recorded_audio

elif uploaded_audio:

    st.session_state.recorded_audio = uploaded_audio

    st.audio(
        st.session_state.recorded_audio
    )

    selected_audio = (
        st.session_state.recorded_audio
    )

elif st.session_state.recorded_audio:

    st.audio(
        st.session_state.recorded_audio
    )

    selected_audio = (
        st.session_state.recorded_audio
    )

# Automatically save a new recording once it exists.
if selected_audio and not st.session_state.audio_saved:
    if st.session_state.course_name and st.session_state.lecture_title:
        try:
            # Make sure the course exists and get its database ID.
            course = get_or_create_course(
                CURRENT_USER_ID,
                st.session_state.course_name
            )

            # Create the lecture immediately, even though it has
            # not been transcribed or summarized yet.
            lecture = create_audio_lecture(
                CURRENT_USER_ID,
                course["id"],
                st.session_state.lecture_title
            )

            lecture_id = lecture["id"]

            # Preserve the original recording in Supabase Storage.
            audio_path = upload_lecture_audio(
                CURRENT_USER_ID,
                lecture_id,
                selected_audio.getvalue(),
                "wav"
            )

            # Connect the stored recording to the lecture row.
            update_lecture_audio_path(
                CURRENT_USER_ID,
                lecture_id,
                audio_path
            )

            st.session_state.current_lecture_id = lecture_id
            st.session_state.current_course_id = course["id"]
            st.session_state.audio_saved = True
            st.session_state.lecture_saved = True

            st.success("Recording saved automatically.")

        except Exception as error:
            st.error(
                "The recording could not be saved. "
                "Keep this page open and try again."
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

        if not st.session_state.current_lecture_id:

            st.info(
                "Save this lecture before using persistent chat."
            )

        else:

            chat_messages = get_chat_messages(
                CURRENT_USER_ID,
                st.session_state.current_lecture_id
            )

            for message in chat_messages:

                with st.chat_message(
                    message["role"]
                ):
                    st.markdown(
                        message["content"]
                    )
            if st.session_state.get("clear_chat_question"):
                st.session_state.chat_question = ""
                st.session_state.clear_chat_question = False
                

            question = st.text_input(
                "Ask a question about this lecture",
                key="chat_question"
            )

            if st.button(
                "Ask Lecture"
            ):

                if question.strip():

                    save_chat_message(
                        CURRENT_USER_ID,
                        st.session_state.current_lecture_id,
                        "user",
                        question
                    )

                    with st.spinner(
                        "Thinking..."
                    ):

                        answer = ask_lecture(
                            st.session_state.transcript,
                            question
                        )

                    save_chat_message(
                        CURRENT_USER_ID,
                        st.session_state.current_lecture_id,
                        "assistant",
                        answer
                    )

                    st.session_state.clear_chat_question = True

                    st.rerun()

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

    try:
        with st.spinner(
            "Generating study notes..."
        ):

            new_notes = generate_notes(
                st.session_state.transcript
            )

        # Save the generated notes before updating
        # the interface.
        update_lecture_notes(
            CURRENT_USER_ID,
            st.session_state.current_lecture_id,
            new_notes
        )

        st.session_state.notes = new_notes
        st.session_state.lecture_saved = True

        st.rerun()

    except RuntimeError as error:
        st.warning(
            "Gemini is temporarily busy. "
            "Your lecture and transcript are safe. "
            "Please try generating notes again in a moment."
        )


    # ----------------------------------------------
    # Save lecture
    # ----------------------------------------------
if (
    st.session_state.transcript
    and st.session_state.notes
):

    if not st.session_state.lecture_saved:

        if st.session_state.current_lecture_id:
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

                if st.session_state.current_lecture_id:
                    update_supabase_lecture(
                        CURRENT_USER_ID,
                        st.session_state.current_lecture_id,
                        st.session_state.current_course_id,
                        st.session_state.lecture_title,
                        st.session_state.transcript,
                        st.session_state.notes
                    )

                    st.session_state.just_saved_message = (
                        "Changes saved successfully."
                    )

                else:
                    lecture = create_lecture(
                        CURRENT_USER_ID,
                        st.session_state.current_course_id,
                        st.session_state.lecture_title,
                        st.session_state.transcript,
                        st.session_state.notes
                    )

                    st.session_state.current_lecture_id = (
                        lecture["id"]
                    )

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