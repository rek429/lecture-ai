import os
import tempfile

import av


MB = 1024 * 1024

# Stay below Groq's 25 MB free-tier upload limit.
MAX_UPLOAD_SIZE = 24 * MB


def get_audio_size(audio_file):
    if isinstance(audio_file, bytes):
        return len(audio_file)

    return len(audio_file.getvalue())


def needs_preprocessing(audio_file):
    return get_audio_size(audio_file) > MAX_UPLOAD_SIZE


def compress_audio_for_transcription(
    audio_file,
    file_extension
):
    if isinstance(audio_file, bytes):
        audio_bytes = audio_file
    else:
        audio_bytes = audio_file.getvalue()

    input_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=f".{file_extension}"
    )

    output_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    input_path = input_file.name
    output_path = output_file.name

    input_file.write(audio_bytes)
    input_file.close()
    output_file.close()

    try:
        with av.open(input_path) as input_container:
            audio_stream = next(
                stream
                for stream in input_container.streams
                if stream.type == "audio"
            )

            with av.open(
                output_path,
                mode="w",
                format="mp3"
            ) as output_container:
                output_stream = output_container.add_stream(
                    "libmp3lame",
                    rate=16000
                )

                output_stream.bit_rate = 32000
                output_stream.layout = "mono"

                resampler = av.AudioResampler(
                    format="s16p",
                    layout="mono",
                    rate=16000
                )

                for frame in input_container.decode(
                    audio_stream
                ):
                    resampled_frames = resampler.resample(
                        frame
                    )

                    for resampled_frame in resampled_frames:
                        for packet in output_stream.encode(
                            resampled_frame
                        ):
                            output_container.mux(packet)

                for resampled_frame in resampler.resample(None):
                    for packet in output_stream.encode(
                        resampled_frame
                    ):
                        output_container.mux(packet)

                for packet in output_stream.encode(None):
                    output_container.mux(packet)

        with open(output_path, "rb") as file:
            return file.read()

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

        if os.path.exists(output_path):
            os.remove(output_path)


def split_audio_for_transcription(
    audio_bytes,
    chunk_minutes=45
):
    input_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    input_path = input_file.name
    input_file.write(audio_bytes)
    input_file.close()

    chunk_paths = []
    chunks = []

    try:
        with av.open(input_path) as input_container:
            audio_stream = next(
                stream
                for stream in input_container.streams
                if stream.type == "audio"
            )

            chunk_duration = chunk_minutes * 60
            chunk_start = 0

            while True:
                chunk_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp3"
                )
                chunk_path = chunk_file.name
                chunk_file.close()

                chunk_paths.append(chunk_path)

                with av.open(
                    chunk_path,
                    mode="w",
                    format="mp3"
                ) as output_container:
                    output_stream = output_container.add_stream(
                        "libmp3lame",
                        rate=16000
                    )

                    output_stream.bit_rate = 32000
                    output_stream.layout = "mono"

                    resampler = av.AudioResampler(
                        format="s16p",
                        layout="mono",
                        rate=16000
                    )

                    input_container.seek(
                        int(
                            chunk_start
                            / float(audio_stream.time_base)
                        ),
                        stream=audio_stream
                    )

                    wrote_audio = False

                    for frame in input_container.decode(
                        audio_stream
                    ):
                        frame_time = frame.time
                        
                        if frame_time is not None and frame_time < chunk_start:
                            continue


                        if (
                            frame_time is not None
                            and frame_time
                            >= chunk_start + chunk_duration
                        ):
                            break

                        resampled_frames = resampler.resample(
                            frame
                        )

                        for resampled_frame in resampled_frames:
                            wrote_audio = True

                            for packet in output_stream.encode(
                                resampled_frame
                            ):
                                output_container.mux(packet)

                    for resampled_frame in resampler.resample(None):
                        wrote_audio = True

                        for packet in output_stream.encode(
                            resampled_frame
                        ):
                            output_container.mux(packet)

                    for packet in output_stream.encode(None):
                        output_container.mux(packet)

                if not wrote_audio:
                    os.remove(chunk_path)
                    chunk_paths.remove(chunk_path)
                    break

                with open(chunk_path, "rb") as file:
                    chunks.append(file.read())

                chunk_start += chunk_duration

        return chunks

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

        for chunk_path in chunk_paths:
            if os.path.exists(chunk_path):
                os.remove(chunk_path)