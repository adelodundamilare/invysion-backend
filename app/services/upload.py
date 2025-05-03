# from app.core.config import settings
# from datetime import datetime
# from app.services.aws import get_client
# import uuid
# import io

# s3_client = get_client("s3")

# class UploadService:
#     def upload_file(self, file: bytes, folder: str):
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         unique_id = str(uuid.uuid4())[:8]
#         filename = f"{timestamp}_{unique_id}"

#         s3_key = f"{folder}/{filename}"
#         bucket_name = settings.AWS_BUCKET

#         s3_client.put_object(
#             Bucket=bucket_name,
#             Key=s3_key,
#             Body=io.BytesIO(file),
#             ContentType="audio/mpeg"
#         )

#         presigned_url = s3_client.generate_presigned_url(
#             'get_object',
#             Params={
#                 'Bucket': bucket_name,
#                 'Key': s3_key
#             },
#             ExpiresIn=604800  # 7 days in seconds
#         )

#         return presigned_url

from app.core.config import settings
from datetime import datetime
from app.services.aws import get_client
import uuid
import io

s3_client = get_client("s3")

class UploadService:
    def upload_file(self, file: bytes, folder: str, content_type: str = "application/octet-stream", generate_presigned: bool = False):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}"

        s3_key = f"{folder}/{filename}"
        bucket_name = settings.AWS_BUCKET

        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=io.BytesIO(file),
            ContentType=content_type
        )

        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': s3_key
            },
            ExpiresIn=31536000
        )

        return presigned_url

    def upload_audio(self, file: bytes, folder: str = "audio"):
        return self.upload_file(file, folder, content_type="audio/mpeg")

    def upload_profile_picture(self, file: bytes):
        folder = "profile_pictures"
        content_type = self._detect_image_type(file) or "image/jpeg"
        return self.upload_file(file, folder, content_type=content_type)

    def _detect_image_type(self, file_bytes: bytes) -> str:
        if file_bytes.startswith(b'\xff\xd8\xff'):
            return "image/jpeg"
        elif file_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            return "image/png"
        elif file_bytes.startswith(b'GIF87a') or file_bytes.startswith(b'GIF89a'):
            return "image/gif"
        elif file_bytes.startswith(b'RIFF') and file_bytes[8:12] == b'WEBP':
            return "image/webp"

        return None