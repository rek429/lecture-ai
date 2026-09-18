from faster_whisper import WhisperModel
import tempfile
import os

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

def transcribe_audio(
    audio_file,
    file_extension="wav"
):
    if isinstance(audio_file, bytes):
        audio_bytes = audio_file
    else:
        audio_bytes = audio_file.getvalue()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=f".{file_extension}"
    ) as temp_file:
        temp_file.write(audio_bytes)
        temp_path = temp_file.name

    try:
        segments, info = model.transcribe(
            temp_path,
            beam_size=1,
            vad_filter=True
        )

        transcript = ""

        for segment in segments:
            transcript += segment.text + " "
    
        return transcript.strip()

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)