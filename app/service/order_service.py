import requests

from app.core.settings import settings
from app.repository.order_device_assignment_repository import (
    OrderDeviceAssignmentRepository,
)
from app.repository.order_repository import OrderRepository
from app.repository.order_shipping_address_repository import (
    OrderShippingAddressRepository,
)
from app.schema.order_schema import OrderPayload
from app.service.base_service import BaseService
from app.util.enums import OrderPickUpLocation, OrderStatus


class OrderService(BaseService):
    def __init__(
        self,
        order_repository: OrderRepository,
        order_device_assignment_repository: OrderDeviceAssignmentRepository,
        order_shipping_address_repository: OrderShippingAddressRepository,
    ):
        self.order_repository = order_repository
        self.order_device_assignments_repository = order_device_assignment_repository
        self.order_shipping_address_repository = order_shipping_address_repository
        super().__init__(order_repository)

    def create_order(self, order_payload: OrderPayload):
        try:
            order = self.order_repository.create_order(order_payload)
            if order:
                self.order_device_assignments_repository.create_order_devices(
                    order_payload, order.uuid
                )
                self.order_shipping_address_repository.create_order_address(
                    order_payload, order.uuid
                )
                return order
        except Exception as e:
            raise e

    def get_all_orders(self):
        try:
            orders = self.order_repository.get_all_orders()
            return orders
        except Exception as e:
            raise e

    def update_order_status_to_ready(self, order_uuid: str):
        try:
            order = self.order_repository.update_order_status(
                order_uuid, OrderStatus.PROCESSING
            )

            if order:
                rtd_data = {
                    "order_reference": order_uuid,
                    "order_description": "order from mvi",
                    "special_instructions": "",
                    "from_address": {
                        "name": OrderPickUpLocation.name,
                        "longitude": float(OrderPickUpLocation.lng),
                        "latitude": float(OrderPickUpLocation.lat),
                    },
                    "to_address": {
                        "name": order.order_shipping_address.address.get(
                            "address_name"
                        ),
                        "longitude": order.order_shipping_address.address.get("lng"),
                        "latitude": order.order_shipping_address.address.get("lat"),
                    },
                    "customer": {
                        "name": OrderPickUpLocation.name,
                        "email": OrderPickUpLocation.email,
                        "phone_number": OrderPickUpLocation.phone,
                    },
                    "recipient": {
                        "name": f"{order.order_shipping_address.first_name} {order.order_shipping_address.last_name}",
                        "email": f"{order.order_shipping_address.email}",
                        "phone_number": f"{order.order_shipping_address.phone}",
                    },
                    "created_at": order.created_at.isoformat(),
                }

                rtd_order = requests.post(
                    settings.RTD_BASE_URL,
                    headers=settings.RTD_HEADERS,
                    json=rtd_data,
                )
            return rtd_order.json()
        except Exception as e:
            raise e

    def update_order_status(self, order_uuid: str, status: str):
        try:
            order = self.order_repository.update_order_status(order_uuid, status)
            return order
        except Exception as e:
            raise e

    def update_order_status_to_delivered(self, order_uuid: str):
        try:
            order = self.order_repository.update_order_status(
                order_uuid, OrderStatus.DELIVERED
            )
            return order
        except Exception as e:
            raise e
