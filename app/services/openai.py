import os
import tempfile
from typing import Optional
from openai import OpenAI
from fastapi import HTTPException, status
from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger("openai_service", "openai.log")
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def transcribe_audio(audio_bytes: bytes) -> Optional[str]:
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        try:
            with open(temp_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    response_format="verbose_json",
                    # timestamp_granularities=["word"],
                    file=audio_file
                )

            return response.text

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transcribe audio: {str(e)}"
        )

# def transcribe_audio(audio_file: str) -> Optional[str]:
#     try:
#         with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#             temp_file.write(audio_file)
#             temp_path = temp_file.name

#         if not os.path.exists(audio_file_path):
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Audio file not found"
#             )

#         with open(audio_file_path, "rb") as audio_file:
#             response = client.audio.transcriptions.create(
#                 model="whisper-1",
#                 response_format="verbose_json",
#                 # timestamp_granularities=["word"]
#                 file=audio_file
#             )

#         return response.text

#     except Exception as e:
#         logger.error(f"Error transcribing audio: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to transcribe audio: {str(e)}"
#         )

# system_prompt = """
# You are a helpful assistant for the company ZyntriQix. Your task is to correct
# any spelling discrepancies in the transcribed text. Make sure that the names of
# the following products are spelled correctly: ZyntriQix, Digique Plus,
# CynapseFive, VortiQore V8, EchoNix Array, OrbitalLink Seven, DigiFractal
# Matrix, PULSE, RAPT, B.R.I.C.K., Q.U.A.R.T.Z., F.L.I.N.T. Only add necessary
# punctuation such as periods, commas, and capitalization, and use only the
# context provided.
# """
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
                {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                {"role": "user", "content": f"Please summarize the following text:\n\n{text}"}
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
