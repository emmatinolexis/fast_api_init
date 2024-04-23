import uuid

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel


class Order(BaseModel):
    __tablename__ = "orders"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    payment_reference_id = Column(
        String(length=100), nullable=False, unique=True, index=True
    )
    device_assignments = relationship("OrderDeviceAssignment", back_populates="order")
    address_assignments = relationship("OrderAddressAssignment", back_populates="order")


class OrderDeviceAssignment(BaseModel):
    __tablename__ = "order_device_assignments"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    order_uuid = Column(UUID(as_uuid=True), ForeignKey("orders.uuid"), nullable=False)
    device_uuid = Column(UUID(as_uuid=True), ForeignKey("devices.uuid"), nullable=False)
    quantity = Column(Integer, nullable=False, index=True)
    order = relationship("Order", back_populates="device_assignments")
    device = relationship("Device")


class OrderAddressAssignment(BaseModel):
    __tablename__ = "order_address_assignments"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    order_uuid = Column(UUID(as_uuid=True), ForeignKey("orders.uuid"), nullable=False)
    country = Column(String(length=50), index=True)
    first_name = Column(String(length=100), index=True)
    last_name = Column(String(length=100), index=True)
    street_name = Column(String(length=100), index=True)
    post_code = Column(String(length=100), nullable=True, index=True)
    email = Column(String(length=100), index=True)
    phone = Column(String(length=100), index=True)
    order = relationship("Order", back_populates="address_assignments")
