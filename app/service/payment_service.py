from app.repository.payment_repository import PaymentRepository
from app.service.base_service import BaseService


class PaymentService(BaseService):
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository
        super().__init__(payment_repository)
