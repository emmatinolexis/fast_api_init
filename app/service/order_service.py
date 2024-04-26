from app.repository.order_device_assignment_repository import (
    OrderDeviceAssignmentRepository,
)
from app.repository.order_repository import OrderRepository
from app.repository.order_shipping_address_repository import (
    OrderShippingAddressRepository,
)
from app.schema.order_schema import OrderPayload
from app.service.base_service import BaseService


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
