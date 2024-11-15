from pydantic import BaseModel

class RNDImageUploadRequest(BaseModel):
    image_base64: str
