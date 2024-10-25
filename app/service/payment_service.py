from app.repository.payment_repository import PaymentRepository
from app.service.base_service import BaseService


class PaymentService(BaseService):
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository
        super().__init__(payment_repository)

    def get_payments(self, search_parameter: str = None, start_date: str = None, end_date: str = None, page: int = None, page_size: int = None) -> list:
        try:
            return self.payment_repository.get_all_payments(search_parameter, start_date, end_date, page, page_size)
        except Exception as e:
            raise e
