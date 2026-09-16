import streamlit as st


def initialize_session_state():
    defaults = {
        "transcript": None,
        "notes": None,
        "course_name": "",
        "lecture_title": "",
        "lecture_saved": False,
        "input_version": 0,
        "course_version": 0,
        "just_saved_message": None,
        "current_course_id": None,
        "current_lecture_id": None,
        "recorded_audio": None,
        "audio_saved": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value