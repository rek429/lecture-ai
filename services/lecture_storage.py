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