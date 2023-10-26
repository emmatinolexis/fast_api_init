from sqlalchemy import Column, Boolean, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

import datetime
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

    # username = Column(String(length=30),nullable=True,default="",index=True)
    first_name = Column(String(length=30),nullable=False,default="",index=True)
    last_name = Column(String(length=30),nullable=False,default="",index=True)
    phone_number = Column(String(length=20), nullable=True, default="", index=True)
    email_address = Column(String(length=100), nullable=False, default="", index=True)
    password = Column(String(length=200), nullable=False)
    # verification_token = Column(String(length=100), nullable=False, default="", index=True)
    # google_auth = Column(String(length=100), nullable=False, default="", index=True)
    verifiedAt = Column(String(length=100), nullable=True, default=None, index=True)
    location = Column(String(length=30),nullable=True,default="",index=True)
    address = Column(String(length=50),nullable=True,default="",index=True)
    profile = relationship("Profile", uselist=False, back_populates="user")
    user_verification = relationship("EmailVerification", uselist=False, back_populates="user")
    

    

class Profile(BaseModel):
    __tablename__ = "profiles"

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="profile")
    
class AssetType(BaseModel):
    __tablename__ = "asset_types"
    asset_type_name = Column(String(length=50), nullable=False, default="", index=True)

class Asset(BaseModel):
    __tablename__ = "assets"
    asset_name = Column(String(length=50),nullable=False,default="", index=True)
    asset_id = Column(String(length=10),nullable=False,default="", index=True)
    asset_status = Column(String(length=15),nullable=False,default="", index=True)
    user_id = Column(String(length=50),nullable=False,default="", index=True)

class TokenTable(Base):
    __tablename__ = "token"
    user_id = Column(Integer)
    access_toke = Column(String(450), primary_key=True)
    refresh_toke = Column(String(450),nullable=False)
    status = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now)
    

class EmailVerification(Base):
    __tablename__ = "email_verifications"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    verification_token = Column(String(450))
    expiry_date = Column(String(450),nullable=False)
    user = relationship("User", back_populates="user_verification")

class PackageItems(BaseModel):
    __tablename__ = "package_items"
    item_name = Column(String(length=50),nullable=False,default="", index=True)
    status = Column(String(length=15),nullable=False,default="", index=True)
    
class Package(BaseModel):
    __tablename__ = "packages"
    package_name = Column(String(length=50),nullable=False,default="", index=True)
    package_price = Column(String(length=50),nullable=False,default="", index=True)      
    package_description = Column(String(length=50),nullable=False,default="", index=True)

class PackageItemAssignment(BaseModel):
    __tablename__ = "package_item_assignments"
    package_item = Column(String(length=50),nullable=False,default="", index=True)
    package_item_id = Column(String(length=10),nullable=False,default="", index=True)


class Feature(BaseModel):
    __tablename__ = "features"
    feature_name = Column(String(length=50),nullable=False,default="", index=True)
    feature_description = Column(String(length=50),nullable=False,default="", index=True)
    icon = Column(String(length=50),nullable=False,default="", index=True)
    status = Column(String(length=50),nullable=False,default="", index=True)

class Equipment(BaseModel):
    __tablename__ = "equipments"
    equipment_name = Column(String(length=50),nullable=False,default="", index=True)
    equipment_id = Column(String(length=10),nullable=False,default="", index=True)
    marker_icon = Column(String(length=50),nullable=False,default="", index=True)
    marker_icon_colour = Column(String(length=50),nullable=False,default="", index=True)

class EquipmentType(BaseModel):
    __tablename__ = "equipment_types"
    equipment_type_name = Column(String(length=50),nullable=False,default="", index=True)
    
class Onboarding(BaseModel):
    __tablename__ = "onboarding"
    asset_type_id = Column(String(length=10),nullable=False,default="", index=True)
    number_of_assets = Column(String(length=10),nullable=False,default="", index=True)
    package_id = Column(String(length=10),nullable=False,default="", index=True)
    user_id = Column(String(length=10),nullable=False,default="", index=True)
    
class OnboardingFeatureAssignment(BaseModel):
    __tablename__ = "onboarding_features_assignments"
    onboarding_id = Column(String(length=10),nullable=False,default="", index=True)
    feature_id = Column(String(length=10),nullable=False,default="", index=True)
    
class ContactSales(BaseModel):
    __tablename__ = "contact_sales"
    phone_number = Column(String(length=20), nullable=True, default="", index=True)
    call_time = Column(String(length=20), nullable=True, default="", index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(length=50),nullable=False,default="", index=True)
    