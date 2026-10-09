import os
from io import BytesIO

from dotenv import load_dotenv
from groq import Groq
from services.audio_processor import (
    MAX_UPLOAD_SIZE,
    compress_audio_for_transcription,
    split_audio_for_transcription,
)

load_dotenv()


def transcribe_with_groq(
    audio_bytes,
    file_extension="mp3"
):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    client = Groq(api_key=api_key)

    # Compress large recordings for transcription only.
    if len(audio_bytes) > MAX_UPLOAD_SIZE:
        audio_bytes = compress_audio_for_transcription(
            audio_bytes,
            file_extension
        )
        file_extension = "mp3"

     # Split oversized audio into upload-safe chunks.
    if len(audio_bytes) > MAX_UPLOAD_SIZE:
        chunk_minutes = 45

        while True:
            chunks = split_audio_for_transcription(
                audio_bytes,
                chunk_minutes=chunk_minutes
            )

            if not chunks:
                raise RuntimeError(
                    "Audio splitting produced no chunks."
                )

            if all(
                len(chunk) <= MAX_UPLOAD_SIZE
                for chunk in chunks
            ):
                break

            # Reduce chunk duration and try again.
            chunk_minutes //= 2

            if chunk_minutes < 1:
                raise ValueError(
                    "Unable to split audio below the upload limit."
                )
    else:
        chunks = [audio_bytes]

    if not chunks:
        raise RuntimeError("No audio chunks were created.")

    transcripts = []

    for index, chunk in enumerate(chunks):
        if len(chunk) > MAX_UPLOAD_SIZE:
            raise ValueError(
                f"Audio chunk {index + 1} exceeds the upload limit."
            )

        audio_file = BytesIO(chunk)
        audio_file.name = f"lecture_{index + 1}.{file_extension}"

        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3-turbo",
            response_format="text",
        )

        if isinstance(transcription, str):
            text = transcription.strip()
        else:
            text = transcription.text.strip()

        if not text:
            raise RuntimeError(
                f"Groq returned an empty transcript for chunk {index + 1}."
            )

        transcripts.append(text)

    return "\n\n".join(transcripts)