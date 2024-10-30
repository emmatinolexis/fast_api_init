import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core import constants
from app.model.base_model import BaseModel
from app.util.enums import AccountType, ActiveStatus, DriverType, UserRole


class User(BaseModel):
    __tablename__ = "users"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    first_name = Column(String(length=30), nullable=False, index=True)
    last_name = Column(String(length=30), nullable=False, index=True)
    phone_number = Column(String(length=50), nullable=True, unique=True, index=True)
    email_address = Column(String(length=100), nullable=False, unique=True, index=True)
    password = Column(String(length=200), nullable=False)
    verifiedAt = Column(String(length=100), nullable=True, default=None, index=True)
    location = Column(String(length=100), nullable=True, index=True)
    address = Column(String(length=50), nullable=True, index=True)
    account_type = Column(Enum(AccountType), nullable=False, index=True)
    onboarding_status = Column(String(length=50), nullable=True, index=True)
    country = Column(String(length=50), nullable=True, index=True)
    currency = Column(String(length=50), nullable=True, index=True)
    status = Column(Enum(ActiveStatus), default=ActiveStatus.ACTIVE, nullable=False)
    deactivation_reason = Column(String(length=250), nullable=True)
    avatar_url = Column(String(length=200), nullable=True)
    phone_verified_at = Column(DateTime, nullable=True)
    role = Column(
        Enum(UserRole), nullable=False, default=UserRole.CUSTOMER.value, index=True
    )
    business_profile_uuid = Column(
        UUID(as_uuid=True), ForeignKey("business_profiles.uuid"), nullable=True
    )
    user_role_uuid = Column(UUID(as_uuid=True), ForeignKey("roles.uuid"), nullable=True)
    license_url = Column(String, nullable=True)
    operator_type = Column(Enum(DriverType), nullable=True)
    business_profile = relationship(
        "BusinessProfile", uselist=False, back_populates="users"
    )
    user_role = relationship("Role", uselist=False)
    user_verification = relationship(
        "EmailVerification", uselist=False, back_populates="user"
    )
    phone_otp_token = relationship(
        "PhoneOtpToken", uselist=False, back_populates="user"
    )
    theft_incidents = relationship("TheftIncidence", back_populates="user")

    asset_device_requests = relationship("AssetDeviceRequest", back_populates="user")

    user_devices = relationship("Device", uselist=True, back_populates="user")

    operated_assets = relationship(
        "Asset", secondary="asset_operator_assignments", back_populates="operators"
    )
    driver_license = relationship("DriverLicense", uselist=False, back_populates="user")
    installations = relationship("Installation", back_populates="installer")

    # business_profile_assignments = relationship(UserOrganisationAssignment, back_populates='user')


def set_currency_based_on_country(target, value, oldvalue, initiator):
    if value in constants.COUNTRY_CURRENCY_MAP:
        target.currency = constants.COUNTRY_CURRENCY_MAP[value]
    else:
        target.currency = None  # or some default value


event.listen(User.country, "set", set_currency_based_on_country, retval=False)
