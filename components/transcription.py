import streamlit as st

from services.transcription import transcribe_audio
from services.supabase_service import (
    update_lecture_transcript,
    update_lecture_notes,
)


def render_transcription(user_id, selected_audio):
    if not selected_audio:
        return

    if st.button(
        "Transcribe Lecture",
        type="primary"
    ):
        if not st.session_state.course_name:
            st.warning(
                "Choose or create a course first."
            )
            return

        if not st.session_state.lecture_title:
            st.warning(
                "Enter a lecture title first."
            )
            return

        with st.spinner(
            "Transcribing..."
        ):
            new_transcript = transcribe_audio(
                selected_audio,
                st.session_state.audio_extension

            )

        # Save the new transcript.
        update_lecture_transcript(
            user_id,
            st.session_state.current_lecture_id,
            new_transcript
        )

        # Notes generated from the previous transcript
        # are no longer valid after re-transcription.
        update_lecture_notes(
            user_id,
            st.session_state.current_lecture_id,
            None
        )

        st.session_state.transcript = new_transcript
        st.session_state.notes = None
        st.session_state.lecture_saved = True

        st.rerun()