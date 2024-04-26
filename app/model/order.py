import uuid

from sqlalchemy import JSON, Column, ForeignKey, Integer, String
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
    payment_reference_id = Column(String(length=100), nullable=False, index=True)
    total_amount = Column(Integer, nullable=False)
    order_devices = relationship("OrderDeviceAssignment", back_populates="order")
    order_shipping_address = relationship("OrderShippingAddress", uselist=False)


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
    quantity = Column(Integer, nullable=False)
    order = relationship("Order", back_populates="order_devices")
    device = relationship("Device")


class OrderShippingAddress(BaseModel):
    __tablename__ = "order_shipping_address"
    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    order_uuid = Column(UUID(as_uuid=True), ForeignKey("orders.uuid"), nullable=False)
    country = Column(String(length=100))
    first_name = Column(String(length=100))
    city = Column(String(length=100))
    last_name = Column(String(length=100))
    address = Column(JSON)
    post_code = Column(String(length=100), nullable=True)
    email = Column(String(length=100))
    phone = Column(String(length=100))
