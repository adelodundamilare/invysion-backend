from app.core.config import settings
from datetime import datetime
from app.services.aws import get_client
import uuid
import io
# import cloudinary
# import cloudinary.uploader

# cloudinary.config(
#     cloud_name=settings.CLOUDINARY_CLOUD_NAME,
#     api_key=settings.CLOUDINARY_API_KEY,
#     api_secret=settings.CLOUDINARY_API_SECRET,
# )
s3_client = get_client("s3")

class UploadService:
    def upload_file(self, file: bytes, folder: str):
        # data = {"resource_type": "auto"}
        # result = cloudinary.uploader.upload(file, **data)
        # return result["secure_url"]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}"

        s3_key = f"{folder}/{filename}"
        bucket_name = settings.AWS_BUCKET

        # s3_client.Bucket(bucket_name).put_object(
        #     Key=s3_key,
        #     Body=io.BytesIO(file),
        #     ContentType="audio/mpeg"
        # )
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=io.BytesIO(file),
            ContentType="audio/mpeg"
        )

        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': s3_key
            },
            ExpiresIn=604800  # 7 days in seconds
        )

        return presigned_url




