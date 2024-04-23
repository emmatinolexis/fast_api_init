from app.repository.order_address_assignment_repository import (
    OrderAddressAssignmentRepository,
)
from app.service.base_service import BaseService


class OrderAddressAssignmentService(BaseService):
    def __init__(self, order_address_repository: OrderAddressAssignmentRepository):
        self.order_address_repository = order_address_repository
        super().__init__(order_address_repository)
