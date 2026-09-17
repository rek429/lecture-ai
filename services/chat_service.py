from groq import Groq
from dotenv import load_dotenv
import os


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
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
- Never introduce facts, examples, explanations, or context that are not
  supported by the transcript.
- If the student's question requires information outside the transcript,
  explicitly say that the lecture did not provide that information.

LECTURE TRANSCRIPT:

{transcript}

STUDENT QUESTION:

{question}
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )

        return response.choices[0].message.content

    except Exception as error:
        raise RuntimeError(
            "Lecture chat is temporarily unavailable. "
            "Please try again in a moment."
        ) from error