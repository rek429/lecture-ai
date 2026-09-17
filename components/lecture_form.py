import hashlib
import streamlit as st
from services.supabase_service import (
    get_courses,
    get_or_create_course,
    create_audio_lecture,
    upload_lecture_audio,
    update_lecture_audio_path,
)


def render_lecture_form(user_id):
    if not st.session_state.current_lecture_id:
        st.subheader(
            "New Lecture"
        )

    # ----------------------------------------------
    # Course selection
    # ----------------------------------------------

    supabase_courses = get_courses(
        user_id
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

    # Figure out which option should appear selected.
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
                    user_id,
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

    # ----------------------------------------------
    # Lecture title
    # ----------------------------------------------

    previous_title = (
        st.session_state.lecture_title
    )

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

    # ----------------------------------------------
    # Audio
    # ----------------------------------------------

    st.subheader(
        "Audio"
    )
    # Existing lecture: show its saved recording.
    if (
        st.session_state.current_lecture_id
        and st.session_state.audio_saved
        and st.session_state.recorded_audio
    ):
        st.audio(
            st.session_state.recorded_audio
        )

        selected_audio = (
            st.session_state.recorded_audio
        )

        return selected_audio

    # New lecture: allow recording or uploading.
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
        audio_bytes = audio.getvalue()

        new_fingerprint = hashlib.sha256(
            audio_bytes
        ).hexdigest()

        if (
            new_fingerprint
            != st.session_state.audio_fingerprint
        ):
            # A genuinely new recording was made.
            st.session_state.recorded_audio = audio
            st.session_state.audio_fingerprint = new_fingerprint
            st.session_state.audio_saved = False

        selected_audio = (
            st.session_state.recorded_audio
        )

        st.audio(
            selected_audio
        )

    elif uploaded_audio:
        audio_bytes = uploaded_audio.getvalue()

        new_fingerprint = hashlib.sha256(
            audio_bytes
        ).hexdigest()

        if (
            new_fingerprint
            != st.session_state.audio_fingerprint
        ):
            # A genuinely new file was uploaded.
            st.session_state.recorded_audio = uploaded_audio
            st.session_state.audio_fingerprint = new_fingerprint
            st.session_state.audio_saved = False

        selected_audio = (
            st.session_state.recorded_audio
        )

        st.audio(
            selected_audio
        )

    elif st.session_state.recorded_audio:
        selected_audio = (
            st.session_state.recorded_audio
        )

        st.audio(
            selected_audio
        )
    # ----------------------------------------------
    # Automatic audio save
    # ----------------------------------------------

    if (
        selected_audio
        and not st.session_state.audio_saved
    ):
        if (
            st.session_state.course_name
            and st.session_state.lecture_title
        ):
            try:
                course = get_or_create_course(
                    user_id,
                    st.session_state.course_name
                )

                lecture = create_audio_lecture(
                    user_id,
                    course["id"],
                    st.session_state.lecture_title
                )

                lecture_id = lecture["id"]

                audio_path = upload_lecture_audio(
                    user_id,
                    lecture_id,
                    selected_audio.getvalue(),
                    "wav"
                )

                update_lecture_audio_path(
                    user_id,
                    lecture_id,
                    audio_path
                )

                st.session_state.current_lecture_id = (
                    lecture_id
                )

                st.session_state.current_course_id = (
                    course["id"]
                )

                st.session_state.audio_saved = True
                st.session_state.lecture_saved = True

                st.success(
                    "Recording saved automatically."
                )

            except Exception:
                st.error(
                    "The recording could not be saved. "
                    "Keep this page open and try again."
                )

    return selected_audio