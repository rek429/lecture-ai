from supabase import create_client
from dotenv import load_dotenv
import os
import time
from datetime import datetime

load_dotenv()


SUPABASE_URL = os.getenv(
    "SUPABASE_URL"
)

SUPABASE_SECRET_KEY = os.getenv(
    "SUPABASE_SECRET_KEY"
)


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY
)

def run_read_with_retry(action, attempts=3, delay=1):
    last_error = None

    for attempt in range(attempts):
        try:
            return action()

        except Exception as error:
            last_error = error

            if attempt < attempts - 1:
                time.sleep(delay)

    raise last_error

def get_or_create_user(
    google_sub,
    email
):
    response = run_read_with_retry(
        lambda: (
            supabase
            .table("users")
            .select("*")
            .eq("google_sub", google_sub)
            .execute()
        )
    )

    if response.data:
        return response.data[0]

    response = (
        supabase
        .table("users")
        .insert({
            "google_sub": google_sub,
            "email": email
        })
        .execute()
    )

    return response.data[0]

def get_courses(user_id):
    response = run_read_with_retry(
        lambda: (
            supabase
            .table("courses")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at")
            .execute()
        )
    )

    return response.data


def get_or_create_course(
    user_id,
    course_name
):
    response = run_read_with_retry(
        lambda: (
            supabase
            .table("courses")
            .select("*")
            .eq("user_id", user_id)
            .eq("name", course_name)
            .execute()
        )
    )

    if response.data:
        return response.data[0]

    response = (
        supabase
        .table("courses")
        .insert({
            "user_id": user_id,
            "name": course_name
        })
        .execute()
    )

    return response.data[0]

def create_lecture(
    user_id,
    course_id,
    title,
    transcript,
    notes
):
    response = (
        supabase
        .table("lectures")
        .insert({
            "user_id": user_id,
            "course_id": course_id,
            "title": title,
            "transcript": transcript,
            "notes": notes
        })
        .execute()
    )

    return response.data[0]

def get_lectures(user_id):
    response = run_read_with_retry(
        lambda: (
            supabase
            .table("lectures")
            .select(
                "*, courses(name)"
            )
            .eq(
                "user_id",
                user_id
            )
            .order(
                "created_at",
                desc=True
            )
            .execute()
        )
    )

    return response.data


def update_supabase_lecture(
    user_id,
    lecture_id,
    course_id,
    title,
    transcript,
    notes
):
    response = (
        supabase
        .table("lectures")
        .update({
            "course_id": course_id,
            "title": title,
            "transcript": transcript,
            "notes": notes,
            "updated_at": datetime.now().isoformat()
        })
        .eq(
            "id",
            lecture_id
        )
        .eq(
            "user_id",
            user_id
        )
        .execute()
    )

    return response.data[0]

def delete_supabase_lecture(
    user_id,
    lecture_id
):
    response = (
        supabase
        .table("lectures")
        .delete()
        .eq(
            "id",
            lecture_id
        )
        .eq(
            "user_id",
            user_id
        )
        .execute()
    )

    return response.data

def save_chat_message(
    user_id,
    lecture_id,
    role,
    content
):
    response = (
        supabase
        .table("chat_messages")
        .insert({
            "user_id": user_id,
            "lecture_id": lecture_id,
            "role": role,
            "content": content
        })
        .execute()
    )

    return response.data[0]


def get_chat_messages(
    user_id,
    lecture_id
):
    response = run_read_with_retry(
        lambda: (
            supabase
            .table("chat_messages")
            .select("*")
            .eq("user_id", user_id)
            .eq("lecture_id", lecture_id)
            .order("created_at")
            .execute()
        )
    )

    return response.data

def upload_lecture_audio(
    user_id,
    lecture_id,
    audio_bytes,
    file_extension="wav"
):
    audio_path = (
        f"{user_id}/"
        f"{lecture_id}/"
        f"lecture.{file_extension}"
    )

    # A lecture's original recording is permanent.
    # Never overwrite an existing recording.
    supabase.storage.from_(
        "lecture-audio"
    ).upload(
        path=audio_path,
        file=audio_bytes,
        file_options={
            "content-type": (
                f"audio/{file_extension}"
            ),
            "upsert": False,
        },
    )

    return audio_path


def download_lecture_audio(audio_path):
    return supabase.storage.from_("lecture-audio").download(audio_path)


def delete_lecture_audio(audio_path):
    if audio_path:
        supabase.storage.from_("lecture-audio").remove([audio_path])

def create_audio_lecture(user_id, course_id, title):
    response = (
        supabase.table("lectures")
        .insert({
            "user_id": user_id,
            "course_id": course_id,
            "title": title,
            "transcript": None,
            "notes": None,
            "audio_path": None,
        })
        .execute()
    )

    return response.data[0]


def update_lecture_audio_path(user_id, lecture_id, audio_path):
    response = (
        supabase.table("lectures")
        .update({
            "audio_path": audio_path,
        })
        .eq("id", lecture_id)
        .eq("user_id", user_id)
        .execute()
    )

    return response.data[0]


def update_lecture_transcript(user_id, lecture_id, transcript):
    response = (
        supabase.table("lectures")
        .update({
            "transcript": transcript,
            "updated_at": datetime.now().isoformat(),
        })
        .eq("id", lecture_id)
        .eq("user_id", user_id)
        .execute()
    )

    return response.data[0]


def update_lecture_notes(user_id, lecture_id, notes):
    response = (
        supabase.table("lectures")
        .update({
            "notes": notes,
            "updated_at": datetime.now().isoformat(),
        })
        .eq("id", lecture_id)
        .eq("user_id", user_id)
        .execute()
    )

    return response.data[0]