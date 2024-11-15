from pydantic import BaseModel

class RNDImageUploadRequest(BaseModel):
    image_base64: str

class RNDImageChunkUploadRequest(BaseModel):
    id: str  
    index: int 
    chunk: str 

