from faster_whisper import WhisperModel
import tempfile
import os

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

def transcribe_audio(audio_file):
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as temp_file:
        temp_file.write(audio_file.getvalue())
        temp_path = temp_file.name

    try:
        segments, info = model.transcribe(
            temp_path,
            beam_size=5
        )

        transcript = ""

        for segment in segments:
            transcript += segment.text + " "

        return transcript.strip()

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)