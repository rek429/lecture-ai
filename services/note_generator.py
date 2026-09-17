from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_notes(transcript):
    prompt = f"""
You are a lecture note-taking assistant.

Turn the following lecture transcript into clear, organized study notes.

Use this structure:

# Lecture Overview
Give a short summary of what the lecture was about.

# Key Concepts
List and explain the major concepts taught.

# Important Definitions
Include important terms and their meanings.

# Examples
Include examples the professor used.

# Important Details
Include details, explanations, formulas, code concepts, or facts that a
student should remember.

# Professor Emphasis
Mention anything that appears especially emphasized or repeated.

# Questions / Unclear Points
Identify ideas that may need further clarification.

# Review Questions
Create up to 5 questions that test understanding of the lecture.
Every question must be answerable using only information explicitly contained
in the transcript. If the transcript does not contain enough information for
5 meaningful questions, create fewer questions instead of introducing outside
knowledge.


IMPORTANT:
- Base the notes strictly on information contained in the transcript.
- Do not add background knowledge, assumptions, or inferred facts.
- If a section has no meaningful information, write "Not discussed."
- Do not force information into every section.
- Do not turn casual statements into technical definitions.
- Clean up filler words, repetition, and obvious speech-to-text errors.
- Preserve technical terminology and examples accurately.
- Distinguish between what the speaker explicitly said and what is uncertain.
- Make the notes concise enough to study from while preserving important detail.
- Never introduce a subject, context, example, or explanation that is not
  supported by the transcript, even if it seems obvious.
LECTURE TRANSCRIPT:

{transcript}
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
            "Note generation is temporarily unavailable. "
            "Please try again in a moment."
        ) from error