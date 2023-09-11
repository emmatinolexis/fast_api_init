from sqlalchemy import Column, Boolean, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .core import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())


class User(BaseModel):
    __tablename__ = "users"

    phone_number = Column(String(length=15), nullable=True, default="", index=True)
    email_address = Column(String(length=100), nullable=False, default="", index=True)
    password = Column(String(length=512), nullable=False)

    profile = relationship("Profile", uselist=False, back_populates="user")


class Profile(BaseModel):
    __tablename__ = "profiles"

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="profile")
    

class AssetType(BaseModel):
    __tablename__ = "asset_types"
    asset_type_name = Column(String(length=50), nullable=False, default="", index=True)
    status = Column(String(length=15), nullable=False, default="", index=True)

class Asset(BaseModel):
    __tablename__ = "assets"
    asset_name = Column(String(length=50),nullable=False,default="", index=True)
    asset_type_id = Column(String(length=10),nullable=False,default="", index=True)
    status = Column(String(length=15),nullable=False,default="", index=True)
    customer_id = Column(String(length=50),nullable=False,default="", index=True)

    
    

