from app.repository.subscription_payment_repository import SubscriptionPaymentRepository
from app.service.base_service import BaseService


class SubscriptionPaymentService(BaseService):
    def __init__(self, subscription_payment_repository: SubscriptionPaymentRepository):
        self.subscription_payment_repository = subscription_payment_repository
        super().__init__(subscription_payment_repository)
