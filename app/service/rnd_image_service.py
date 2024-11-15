import base64
import uuid
import boto3
from app.util.utils import upload_to_s3
from app.core.settings import settings


class RNDImageService:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket_name = settings.S3_BUCKET

    async def upload_image(self, image_base64: str) -> str:
        try:
            image_data = base64.b64decode(image_base64)
        except Exception:
            raise ValueError("Invalid base64 image data")

        image_uuid = str(uuid.uuid4())
        file_name = f"{image_uuid}.png" 

        content_type = "image/png" 

        url = await upload_to_s3(
            file_name=file_name,
            file_content=image_data,
            content_type=content_type,
            folder_name="rnd_images",
        )

        return url

    def list_images(self):
        try:
            prefix = "rnd_images/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
            )
            urls = []
            for obj in response.get("Contents", []):
                key = obj["Key"]
                url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
                urls.append(url)
            return urls
        except Exception as e:
            raise e
