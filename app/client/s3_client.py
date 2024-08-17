import boto3
from smart_open import open


class S3Client:
    def __init__(self, aws_access_key: str, aws_secret_key: str, bucket_name: str):
        self.session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )
        self.client = self.session.client("s3")
        self.bucket_name = bucket_name

    async def upload_file(
        self,
        file_name: str,
        file_content: bytes,
        content_type: str,
        folder_name: str = None,
    ) -> str:
        # Set up the S3 URL
        if folder_name:
            s3_path = f"{folder_name}/{file_name}"
        else:
            s3_path = file_name

        url = f"s3://{self.bucket_name}/{s3_path}"

        # Attempt to upload the file content
        try:
            with open(
                url,
                "wb",
                transport_params={
                    "session": self.session,
                },
            ) as f:
                f.write(file_content)

            # Set the content type for the file, ensure the key is correct
            self.client.copy_object(
                Bucket=self.bucket_name,
                Key=s3_path,  # Correct Key with folder_name if applicable
                CopySource={
                    "Bucket": self.bucket_name,
                    "Key": s3_path,
                },  # Correct CopySource
                MetadataDirective="REPLACE",
                ContentType=content_type,
            )

            # Return a URL for the file
            return f"https://{self.bucket_name}.s3.amazonaws.com/{s3_path}"

        except Exception as e:
            # Catch any errors during upload or metadata setting
            print(f"Error uploading file: {e}")
            raise e
