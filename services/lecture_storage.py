import json
import os
from datetime import datetime


DATA_DIR = "data/users"


def get_lecture_dir(user_id):
    return os.path.join(
        DATA_DIR,
        user_id,
        "lectures"
    )


def save_lecture(
    user_id,
    course_name,
    lecture_title,
    transcript,
    notes
):
    lecture_dir = get_lecture_dir(user_id)

    os.makedirs(
        lecture_dir,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    safe_course = course_name.replace(
        " ",
        "_"
    ).lower()

    safe_title = lecture_title.replace(
        " ",
        "_"
    ).lower()

    filename = (
        f"{safe_course}_"
        f"{safe_title}_"
        f"{timestamp}.json"
    )

    lecture_data = {
        "course": course_name,
        "title": lecture_title,
        "transcript": transcript,
        "notes": notes,
        "created_at": datetime.now().isoformat()
    }

    file_path = os.path.join(
        lecture_dir,
        filename
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            lecture_data,
            file,
            indent=4
        )

    return file_path


def load_lectures(user_id):
    lecture_dir = get_lecture_dir(user_id)

    os.makedirs(
        lecture_dir,
        exist_ok=True
    )

    lectures = []

    for filename in os.listdir(
        lecture_dir
    ):

        if not filename.endswith(".json"):
            continue

        file_path = os.path.join(
            lecture_dir,
            filename
        )

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            lecture_data = json.load(file)

        lecture_data["filename"] = filename

        lectures.append(
            lecture_data
        )

    lectures.sort(
        key=lambda lecture: lecture["created_at"],
        reverse=True
    )

    return lectures