from app.repository.order_shipping_address_repository import (
    OrderShippingAddressRepository,
)
from app.service.base_service import BaseService


class OrderShippingAddressService(BaseService):
    def __init__(
        self, order_shipping_address_repository: OrderShippingAddressRepository
    ):
        self.order_shipping_address_repository = order_shipping_address_repository
        super().__init__(order_shipping_address_repository)
