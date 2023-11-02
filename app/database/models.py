from sqlalchemy import Column, Boolean, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

import uuid
import datetime
from .core import Base

class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
    

class User(BaseModel):
    __tablename__ = "users"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    first_name = Column(String(length=30),nullable=False,default="",index=True)
    last_name = Column(String(length=30),nullable=False,default="",index=True)
    phone_number = Column(String(length=20), nullable=True, default="", index=True)
    email_address = Column(String(length=100), nullable=False, default="", index=True)
    password = Column(String(length=200), nullable=False)
    verifiedAt = Column(String(length=100), nullable=True, default=None, index=True)
    location = Column(String(length=30),nullable=True,default="",index=True)
    address = Column(String(length=50),nullable=True,default="",index=True)
    profile = relationship("Profile", uselist=False, back_populates="user")
    user_verification = relationship("EmailVerification", uselist=False, back_populates="user")
    
class Profile(BaseModel):
    __tablename__ = "profiles"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    user = relationship("User", back_populates="profile")
    
class AssetType(BaseModel):
    __tablename__ = "asset_types"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    asset_type_name = Column(String(length=50), nullable=False, default="", index=True)
    description = Column(String(length=100), nullable=True, default="", index=True)
    icon_url = Column(String(length=50), nullable=False, default="", index=True)
    status = Column(String(length=50), nullable=False, default="", index=True)

class Asset(BaseModel):
    __tablename__ = "assets"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    asset_name = Column(String(length=50),nullable=False,default="", index=True)
    asset_status = Column(String(length=15),nullable=False,default="", index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    asset_type_uuid = Column(UUID(as_uuid=True), ForeignKey("asset_types.uuid"), nullable=False)
    equipment_uuid = Column(UUID(as_uuid=True), ForeignKey("equipments.uuid"), nullable=False)
    vin_no = Column(String(length=100),nullable=True,default="", index=True)
    user = relationship("User", uselist=False)
    asset_type = relationship("AssetType", uselist=False)
    equipment = relationship("Equipment", uselist=False)

class TokenTable(Base):
    __tablename__ = "token"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    access_toke = Column(String(450), primary_key=True)
    refresh_toke = Column(String(450),nullable=False)
    status = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now)
    
class EmailVerification(Base):
    __tablename__ = "email_verifications"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), primary_key=True, unique=True, nullable=False)
    verification_token = Column(String(450))
    expiry_date = Column(String(450),nullable=False)
    user = relationship("User", back_populates="user_verification")

class PackageItem(BaseModel):
    __tablename__ = "package_items"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    item_name = Column(String(length=50),nullable=False,default="", index=True)
    status = Column(String(length=15),nullable=False,default="", index=True)
    
class Package(BaseModel):
    __tablename__ = "packages"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    package_name = Column(String(length=50),nullable=False,default="", index=True)
    package_price = Column(String(length=50),nullable=False,default="", index=True)      
    package_description = Column(String(length=100),nullable=True,default="", index=True)
    package_item_assignments = relationship("PackageItemAssignment", uselist=True)
    
class PackageItemAssignment(BaseModel):
    __tablename__ = "package_item_assignments"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    package_uuid = Column(UUID(as_uuid=True), ForeignKey("packages.uuid"), nullable=False)
    package_item_uuid = Column(UUID(as_uuid=True), ForeignKey("package_items.uuid"), nullable=False)
    package_item = relationship("PackageItem", uselist=False)

class Feature(BaseModel):
    __tablename__ = "features"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    feature_name = Column(String(length=50),nullable=False,default="", index=True)
    feature_description = Column(String(length=100),nullable=False,default="", index=True)
    icon_url = Column(String(length=50),nullable=False,default="", index=True)
    status = Column(String(length=50),nullable=False,default="", index=True)

class Equipment(BaseModel):
    __tablename__ = "equipments"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    equipment_name = Column(String(length=50),nullable=False,default="", index=True)
    equipment_type_uuid = Column(UUID(as_uuid=True), ForeignKey("equipment_types.uuid"))
    marker_icon_url = Column(String(length=50),nullable=False,default="", index=True)
    marker_icon_colour = Column(String(length=50),nullable=False,default="", index=True)
    equipment_type = relationship("EquipmentType", uselist=False)

class EquipmentType(BaseModel):
    __tablename__ = "equipment_types"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    equipment_type_name = Column(String(length=50),nullable=False,default="", index=True)
    status = Column(String(length=50),nullable=False,default="", index=True)

class Onboarding(BaseModel):
    __tablename__ = "onboardings"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    asset_type_uuid = Column(UUID(as_uuid=True), ForeignKey("asset_types.uuid"))
    number_of_assets = Column(Integer,nullable=False,default="", index=True)
    number_of_months = Column(Integer,nullable=False,default="", index=True)
    package_uuid = Column(UUID(as_uuid=True), ForeignKey("packages.uuid"), nullable=False)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    user = relationship("User", uselist=False)
    package = relationship("Package", uselist=False)
    asset_type = relationship("AssetType", uselist=False)
    features = relationship("OnboardingFeatureAssignment", uselist=True)

class OnboardingFeatureAssignment(BaseModel):
    __tablename__ = "onboarding_feature_assignments"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    onboarding_uuid = Column(UUID(as_uuid=True), ForeignKey("onboardings.uuid"), nullable=False)
    feature_uuid = Column(UUID(as_uuid=True), ForeignKey("features.uuid"), nullable=False)
    
class ContactSale(BaseModel):
    __tablename__ = "contact_sales"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    phone_number = Column(String(length=20), nullable=True, default="", index=True)
    call_time = Column(String(length=20), nullable=True, default="", index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    status = Column(String(length=50),nullable=False,default="", index=True)
    user = relationship("User", uselist=False)



