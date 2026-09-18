import streamlit as st

from services.supabase_service import download_lecture_audio


def restore_lecture_from_url(saved_lectures):
    lecture_id_from_url = st.query_params.get("lecture")

    if (
        not lecture_id_from_url
        or st.session_state.current_lecture_id == lecture_id_from_url
    ):
        return

    lecture_from_url = next(
        (
            lecture
            for lecture in saved_lectures
            if lecture["id"] == lecture_id_from_url
        ),
        None
    )

    if not lecture_from_url:
        # Invalid or deleted lecture IDs should
        # not remain in the URL.
        st.query_params.clear()
        return

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
            audio_path = lecture_from_url["audio_path"]

            st.session_state.recorded_audio = (
                download_lecture_audio(
                    audio_path
                )
            )

            st.session_state.audio_extension = (
                audio_path
                .rsplit(".", 1)[-1]
                .lower()
            )

            st.session_state.audio_saved = True

        except Exception:
            st.session_state.recorded_audio = None
            st.session_state.audio_saved = False

    else:
        st.session_state.recorded_audio = None
        st.session_state.audio_saved = False