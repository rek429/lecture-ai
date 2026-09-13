import json
import os
from datetime import datetime


LECTURE_DIR = "data/lectures"


def save_lecture(course_name, lecture_title, transcript, notes):
    os.makedirs(LECTURE_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    safe_course = course_name.replace(" ", "_").lower()
    safe_title = lecture_title.replace(" ", "_").lower()

    filename = f"{safe_course}_{safe_title}_{timestamp}.json"

    lecture_data = {
        "course": course_name,
        "title": lecture_title,
        "transcript": transcript,
        "notes": notes,
        "created_at": datetime.now().isoformat()
    }

    file_path = os.path.join(
        LECTURE_DIR,
        filename
    )

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            lecture_data,
            file,
            indent=4
        )

    return file_path


def load_lectures():
    os.makedirs(LECTURE_DIR, exist_ok=True)

    lectures = []

    for filename in os.listdir(LECTURE_DIR):

        if not filename.endswith(".json"):
            continue

        file_path = os.path.join(
            LECTURE_DIR,
            filename
        )

        with open(file_path, "r", encoding="utf-8") as file:
            lecture_data = json.load(file)

        lecture_data["filename"] = filename

        lectures.append(lecture_data)

    lectures.sort(
        key=lambda lecture: lecture["created_at"],
        reverse=True
    )

    return lectures