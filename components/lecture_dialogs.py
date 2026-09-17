import streamlit as st

from services.supabase_service import delete_supabase_lecture


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
def confirm_delete_lecture(user_id, lecture):
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
                user_id,
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