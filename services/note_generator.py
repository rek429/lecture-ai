from google import genai
from google.genai import errors
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
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
Create 5 questions that test understanding of the lecture.

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

LECTURE TRANSCRIPT:

{transcript}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text

    except errors.ServerError as error:
        if error.code == 503:
            raise RuntimeError(
                "Gemini is temporarily busy. Please try generating notes again in a moment."
            ) from error

        raise