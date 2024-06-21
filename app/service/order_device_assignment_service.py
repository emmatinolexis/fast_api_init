from app.repository.order_device_assignment_repository import \
    OrderDeviceAssignmentRepository
from app.service.base_service import BaseService


class OrderDeviceAssignmentService(BaseService):
    def __init__(self, order_device_repository: OrderDeviceAssignmentRepository):
        self.order_device_repository = order_device_repository
        super().__init__(order_device_repository)
