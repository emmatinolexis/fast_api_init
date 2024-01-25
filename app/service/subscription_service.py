from app.repository.subscription_repository import SubscriptionRepository
from app.service.base_service import BaseService


class SubscriptionService(BaseService):
    def __init__(self, subscription_repository: SubscriptionRepository):
        self.subscription_repository = subscription_repository
        super().__init__(subscription_repository)

    def get_all_subscriptions(self, page=1, page_size=10):
        try:
            return self.subscription_repository.read_all_subscriptions(page, page_size)
        except Exception as e:
            raise e
