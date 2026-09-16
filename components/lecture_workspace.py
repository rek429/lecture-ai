import streamlit as st

from services.chat_service import ask_lecture
from services.note_generator import generate_notes

from services.supabase_service import (
    get_chat_messages,
    save_chat_message,
    update_lecture_notes,
)


def render_lecture_workspace(user_id):
    if not st.session_state.transcript:
        return

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
            "Chat",
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
                user_id,
                st.session_state.current_lecture_id
            )

            for message in chat_messages:
                with st.chat_message(
                    message["role"]
                ):
                    st.markdown(
                        message["content"]
                    )

            if st.session_state.get(
                "clear_chat_question"
            ):
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
                        user_id,
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
                        user_id,
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

            update_lecture_notes(
                user_id,
                st.session_state.current_lecture_id,
                new_notes
            )

            st.session_state.notes = new_notes
            st.session_state.lecture_saved = True

            st.rerun()

        except RuntimeError:
            st.warning(
                "Gemini is temporarily busy. "
                "Your lecture and transcript are safe. "
                "Please try generating notes again in a moment."
            )