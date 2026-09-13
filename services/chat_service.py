from google import genai
from dotenv import load_dotenv
import os


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def ask_lecture(transcript, question):
    prompt = f"""
You are a lecture assistant.

Answer the student's question using only the lecture transcript below.

Rules:
- Base your answer only on the transcript.
- Do not add outside knowledge.
- If the transcript does not contain enough information to answer, say that clearly.
- Keep the answer clear and concise.
- Preserve technical terminology from the lecture.

LECTURE TRANSCRIPT:

{transcript}

STUDENT QUESTION:

{question}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text