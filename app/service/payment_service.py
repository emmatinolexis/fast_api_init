from app.repository.payment_repository import PaymentRepository
from app.service.base_service import BaseService


class PaymentService(BaseService):
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository
        super().__init__(payment_repository)

    def get_payments(self, search_parameter: str = None, start_date: str = None, end_date: str = None, page: int = None, page_size: int = None):
        try:
            payments = self.payment_repository.get_all_payments(search_parameter, start_date, end_date, page, page_size)
            payments_data = []
            for payment in payments.get("payments"):
                data = {
                    "date": payment.created_at,
                    "amount": payment.amount,
                    "payment_method": payment.channel,
                    "status": payment.status,
                    "payment_type": payment.payment_type,
                    "payment_reference": payment.reference_no,
                    "customer": f"{payment.user.first_name} {payment.user.last_name}",
                    "account_type": payment.user.account_type
                }

                payments_data.append(data)

            return {
                "payments": payments_data,
                "current_page": payments.get("current_page"),
                "page_size": payments.get("page_size"),
                "total_records": payments.get("total_records"),
                "total_pages": payments.get("total_pages"),
                "successful_payments": payments.get("successful_payments"),
                "failed_payments": payments.get("failed_payments")
            }
        except Exception as e:
            raise e
