# import os
# import tempfile
# from typing import Optional, List
# from openai import OpenAI
# from fastapi import HTTPException, status
# from app.core.config import settings
# from app.utils.logger import setup_logger
# import ffmpeg
# import os
# import shutil
# import math

# logger = setup_logger("openai_service", "openai.log")
# client = OpenAI(api_key=settings.OPENAI_API_KEY)

# def split_audio(input_path: str, chunk_length: int = 600):
#     output_dir = os.path.dirname(input_path)
#     base_name = os.path.splitext(os.path.basename(input_path))[0]
#     output_template = os.path.join(output_dir, f"{base_name}_%03d.mp3")

#     ffmpeg.input(input_path).output(
#         output_template,
#         f='segment',
#         segment_time=chunk_length,
#         c='copy'
#     ).run(quiet=True, overwrite_output=True)

#     return sorted([
#         os.path.join(output_dir, f) for f in os.listdir(output_dir)
#         if f.startswith(base_name + "_")
#     ])

# def transcribe_audio_chunk(file_path: str, offset: float):
#     with open(file_path, "rb") as audio_file:
#         response = client.audio.transcriptions.create(
#             model="whisper-1",
#             response_format="verbose_json",
#             timestamp_granularities=["word"],
#             file=audio_file
#         )

#     # Adjust timestamps with the offset
#     adjusted_words = []
#     for word in response.words:
#         word_data = word.dict()
#         word_data["start"] = word.start + offset
#         word_data["end"] = word.end + offset
#         adjusted_words.append(word_data)

#     return adjusted_words

# def transcribe_long_audio(audio_bytes: bytes):
#     try:
#         if shutil.which("ffmpeg") is None:
#             raise RuntimeError("ffmpeg is not installed or not found in system PATH")

#         with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
#             temp_file.write(audio_bytes)
#             temp_path = temp_file.name

#         chunks = split_audio(temp_path, chunk_length=600)  # 10 min
#         full_transcript = []

#         for index, chunk_path in enumerate(chunks):
#             offset = index * 600  # adjust timestamps by chunk start
#             words = transcribe_audio_chunk(chunk_path, offset=offset)
#             full_transcript.extend(words)

#         # Cleanup
#         for path in [temp_path] + chunks:
#             if os.path.exists(path):
#                 os.unlink(path)

#         transcript_text = stringify_with_timestamps(full_transcript, interval=10)
#         print(transcript_text, 'transcript_text')

#         return transcript_text

#     except Exception as e:
#         logger.error(f"Error transcribing long audio: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to transcribe audio: {str(e)}"
#         )

# def transcribe_audio(audio_bytes: bytes):
#     try:
#         with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
#             temp_file.write(audio_bytes)
#             temp_path = temp_file.name

#         try:
#             with open(temp_path, "rb") as audio_file:
#                 response = client.audio.transcriptions.create(
#                     model="whisper-1",
#                     response_format="verbose_json",
#                     timestamp_granularities=["word"],
#                     file=audio_file
#                 )

#             return response.words

#         finally:
#             if os.path.exists(temp_path):
#                 os.unlink(temp_path)

#     except Exception as e:
#         logger.error(f"Error transcribing audio: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to transcribe audio: {str(e)}"
#         )

# def format_seconds(seconds: float) -> str:
#     minutes = int(seconds) // 60
#     seconds = int(seconds) % 60
#     return f"{minutes:02d}:{seconds:02d}"

# def stringify_with_timestamps(words: List[dict], interval: int = 10) -> str:
#     if not words:
#         return ""

#     output = []
#     current_time_marker = 0
#     current_line = []

#     for word in words:
#         start_time = word.get("start", 0)

#         if start_time >= current_time_marker:
#             if current_line:
#                 output.append(f"[{format_seconds(current_time_marker)}] " + " ".join(current_line))
#             current_line = []
#             current_time_marker = math.floor(start_time / interval) * interval

#         current_line.append(word.get("word", ""))

#     if current_line:
#         output.append(f"[{format_seconds(current_time_marker)}] " + " ".join(current_line))

#     return "\n".join(output)


import os
import tempfile
from typing import Optional, List
from openai import OpenAI
from fastapi import HTTPException, status
from app.core.config import settings
from app.utils.logger import setup_logger
import ffmpeg
import shutil
import math

logger = setup_logger("openai_service", "openai.log")
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def split_audio(input_path: str, chunk_length: int = 600):
    output_dir = os.path.dirname(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_template = os.path.join(output_dir, f"{base_name}_%03d.mp3")

    ffmpeg.input(input_path).output(
        output_template,
        f='segment',
        segment_time=chunk_length,
        c='copy'
    ).run(quiet=True, overwrite_output=True)

    return sorted([
        os.path.join(output_dir, f) for f in os.listdir(output_dir)
        if f.startswith(base_name + "_")
    ])

def transcribe_audio_chunk(file_path: str, offset: float):
    with open(file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["word"],
            file=audio_file
        )

    # Adjust timestamps with the offset
    adjusted_words = []
    for word in response.words:
        word_data = word.dict()
        word_data["start"] = word.start + offset
        word_data["end"] = word.end + offset
        adjusted_words.append(word_data)

    return adjusted_words

def transcribe_long_audio(audio_bytes: bytes):
    try:
        if shutil.which("ffmpeg") is None:
            raise RuntimeError("ffmpeg is not installed or not found in system PATH")

        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        chunks = split_audio(temp_path, chunk_length=600)  # 10 min
        full_transcript = []

        for index, chunk_path in enumerate(chunks):
            offset = index * 600  # adjust timestamps by chunk start
            words = transcribe_audio_chunk(chunk_path, offset=offset)
            full_transcript.extend(words)

        # Cleanup
        for path in [temp_path] + chunks:
            if os.path.exists(path):
                os.unlink(path)

        transcript_text = stringify_with_timestamps(full_transcript, interval=10)

        return transcript_text

    except Exception as e:
        logger.error(f"Error transcribing long audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transcribe audio: {str(e)}"
        )

def transcribe_audio(audio_bytes: bytes):
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        try:
            with open(temp_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    response_format="verbose_json",
                    timestamp_granularities=["word"],
                    file=audio_file
                )

            return response.words

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transcribe audio: {str(e)}"
        )

def format_seconds(seconds: float) -> str:
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes:02d}:{seconds:02d}"

def stringify_with_timestamps(words: List[dict], interval: int = 10) -> str:
    if not words:
        return ""

    output = []
    current_time_marker = 0
    current_line = []

    for word in words:
        start_time = word.get("start", 0)

        if start_time >= current_time_marker + interval:
            if current_line:
                output.append(f"[{format_seconds(current_time_marker)}] " + " ".join(current_line))
            current_line = []
            while start_time >= current_time_marker + interval:
                current_time_marker += interval

        current_line.append(word.get("word", ""))

    if current_line:
        output.append(f"[{format_seconds(current_time_marker)}] " + " ".join(current_line))

    return "\n".join(output)

def summarize_text(text: str) -> Optional[str]:
    try:
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text provided for summarization"
            )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                { "role": "system", "content": "You are a dental assistant AI that summarizes text using the SOAP framework. The SOAP format consists of:\n\n- **Subjective (S):** Patient's reported symptoms, concerns, and dental history.\n- **Objective (O):** Clinical findings, test results, and observations from the dental examination.\n- **Assessment (A):** Diagnosis or professional evaluation of the patient's dental condition.\n- **Plan (P):** Recommended treatment, procedures, follow-up care, and next steps.\n\nEnsure that each section is concise, clear, and professionally formatted."},
                { "role": "user",  "content": f"Please summarize - as a report - this text using the SOAP framework:\n\n{text}"}
            ],
            max_tokens=300,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to summarize text: {str(e)}"
        )

def summarize_text(text: str) -> Optional[str]:
    try:
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text provided for summarization"
            )

        # If text is too long, just cut it down
        max_length = 16000  # about 4000 tokens, adjust if needed
        if len(text) > max_length:
            text = text[:max_length]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a dental assistant AI that summarizes text using the SOAP framework. The SOAP format consists of:\n\n"
                               "- **Subjective (S):** Patient's reported symptoms, concerns, and dental history.\n"
                               "- **Objective (O):** Clinical findings, test results, and observations from the dental examination.\n"
                               "- **Assessment (A):** Diagnosis or professional evaluation of the patient's dental condition.\n"
                               "- **Plan (P):** Recommended treatment, procedures, follow-up care, and next steps.\n\n"
                               "Ensure that each section is concise, clear, and professionally formatted."
                },
                {
                    "role": "user",
                    "content": f"Please summarize - as a report - this text using the SOAP framework:\n\n{text}"
                }
            ],
            max_tokens=500,  # you can adjust if needed
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to summarize text: {str(e)}"
        )