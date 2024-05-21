from pydantic import BaseModel, Field
from app.util.enums import FileFormat


class FileUploadPayload(BaseModel):
    file_format: FileFormat
    encoded_file: str = Field(..., title="Base64 encoded file")
