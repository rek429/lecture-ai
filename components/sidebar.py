import streamlit as st

from services.supabase_service import (
    download_lecture_audio,
)


def render_sidebar(
    saved_lectures,
    confirm_new_lecture,
    confirm_delete_lecture,
):
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

    # Display course folders
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
                            key=f"open_{lecture['id']}",
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
                                    audio_path = lecture["audio_path"]

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

                            st.session_state.input_version += 1
                            st.session_state.course_version += 1

                            st.query_params["lecture"] = lecture["id"]

                            st.rerun()

                    with col2:
                        if st.button(
                            "🗑️",
                            key=f"delete_{lecture['id']}",
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