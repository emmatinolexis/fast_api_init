from sqlalchemy import Column, String, Integer, LargeBinary, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from app.model.base_model import BaseModel

class RNDImage(BaseModel):
    __tablename__ = 'rnd_images'
    image_id = Column(String, primary_key=True) 
    chunk_index = Column(Integer, primary_key=True) 
    chunk_data = Column(LargeBinary, nullable=False) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

