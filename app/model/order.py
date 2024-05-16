import uuid

from sqlalchemy import JSON, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.model.base_model import BaseModel
from app.util.enums import OrderStatus


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
    order_inventories = relationship("OrderDeviceAssignment", back_populates="order")
    order_shipping_address = relationship("OrderShippingAddress", uselist=False)
    order_status = Column(Enum(OrderStatus))


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
    inventory_uuid = Column(
        UUID(as_uuid=True), ForeignKey("inventories.uuid"), nullable=False
    )
    quantity = Column(Integer, nullable=False)
    order = relationship("Order", back_populates="order_inventories")
    inventory = relationship("Inventory")


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
