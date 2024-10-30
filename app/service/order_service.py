import requests

from app.core.settings import settings
from app.repository.device_repository import DeviceRepository
from app.repository.inventory_repository import InventoryRepository
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
        device_repository: DeviceRepository,
        inventory_repository: InventoryRepository,
    ):
        self.order_repository = order_repository
        self.order_device_assignments_repository = order_device_assignment_repository
        self.order_shipping_address_repository = order_shipping_address_repository
        self.device_repository = device_repository
        self.inventory_repository = inventory_repository

        super().__init__(order_repository)

    def create_order(self, order_payload: OrderPayload):
        try:
            order = self.order_repository.create_order(order_payload)
            if order:
                for device in order_payload.devices:
                    self.order_device_assignments_repository.create_order_device(
                        device, order.uuid
                    )

                    self.inventory_repository.reduce_inventory_no(
                        device.inventory_uuid, device.quantity
                    )

                self.order_shipping_address_repository.create_order_address(
                    order_payload, order.uuid
                )
                return order
        except Exception as e:
            raise e

    def get_all_orders(
        self, page=1, page_size=10, search_query=None, start_date=None, end_date=None
    ):
        try:
            orders = self.order_repository.get_all_orders(
                page=page,
                page_size=page_size,
                search_query=search_query,
                start_date=start_date,
                end_date=end_date,
            )
            return orders
        except Exception as e:
            raise e

    def update_order_status_to_ready(self, order_uuid: str):
        try:
            order = self.order_repository.update_order_status(
                order_uuid, OrderStatus.READY_FOR_PICKUP
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

    def get_total_orders_count(self, search_query=None):
        try:
            total_orders = self.order_repository.get_total_orders_count(
                search_query=search_query
            )
            return total_orders
        except Exception as e:
            raise e
