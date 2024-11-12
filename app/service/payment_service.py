from app.repository.payment_repository import PaymentRepository
from app.service.base_service import BaseService
from decimal import Decimal

class PaymentService(BaseService):
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository
        super().__init__(payment_repository)
    
    def get_payments(
        self,
        search_parameter: str = None,
        start_date: str = None,
        end_date: str = None,
        page: int = 1,
        page_size: int = 10,
        status=None,
    ):
        try:
            payments = self.payment_repository.get_all_payments(
                search_parameter, start_date, end_date, page, page_size, status
            )
            payments_data = []
            for payment in payments.get("payments"):
                data = {
                    "date": payment.created_at,
                    "amount": str(payment.amount),  # Convert Decimal to string for JSON serialization
                    "payment_method": payment.channel,
                    "status": payment.status.value,  # Assuming status is an Enum
                    "payment_type": payment.payment_type.value,  # Assuming payment_type is an Enum
                    "payment_reference": payment.reference_no,
                    "customer": f"{payment.user.first_name} {payment.user.last_name}",
                    "account_type": payment.user.account_type,
                }
                payments_data.append(data)
    
            return {
                "payments": payments_data,
                "current_page": payments.get("current_page"),
                "page_size": payments.get("page_size"),
                "total_records": payments.get("total_records"),
                "total_pages": payments.get("total_pages"),
                "successful_payments": payments.get("successful_payments"),
                "failed_payments": payments.get("failed_payments"),
                "total_payment_amount": str(payments.get("total_payment_amount")),
                "total_payment_amount_percentage_change": payments.get("total_payment_amount_percentage_change"),
                "successful_payments_percentage_change": payments.get("successful_payments_percentage_change"),
                "failed_payments_percentage_change": payments.get("failed_payments_percentage_change"),
            }
        except Exception as e:
            raise e
