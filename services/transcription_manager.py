import time

from groq import RateLimitError

from services.groq_transcription import transcribe_with_groq
from services.transcription import transcribe_audio


GROQ_COOLDOWN_SECONDS = 300
groq_cooldown_until = 0


def transcribe_lecture(
    audio_file,
    file_extension="wav"
):
    global groq_cooldown_until

    if isinstance(audio_file, bytes):
        audio_bytes = audio_file
    else:
        audio_bytes = audio_file.getvalue()

    # Skip Groq temporarily after a rate-limit error.
    if time.time() < groq_cooldown_until:
        remaining = int(groq_cooldown_until - time.time())

        print(
            f"Groq rate-limit cooldown active "
            f"({remaining} seconds remaining)."
        )

    else:
        try:
            print("Attempting Groq transcription...")

            transcript = transcribe_with_groq(
                audio_bytes,
                file_extension
            )

            print("Groq transcription successful.")
            return transcript

        except RateLimitError as error:
            groq_cooldown_until = (
                time.time() + GROQ_COOLDOWN_SECONDS
            )

            print(f"Groq rate limit reached: {error}")
            print("Starting 5-minute Groq cooldown.")

        except Exception as error:
            print(f"Groq transcription failed: {error}")

    print("Falling back to local Faster-Whisper...")

    transcript = transcribe_audio(
        audio_bytes,
        file_extension
    )

    print("Local transcription successful.")
    return transcript