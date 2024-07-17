import logging

import requests

from app.core.settings import settings
from app.repository.user_subscription_repository import UserSubscriptionRepository
from app.service.base_service import BaseService


class UserSubscriptionService(BaseService):
    def __init__(self, user_subscription_repository: UserSubscriptionRepository):
        self.user_subscription_repository = user_subscription_repository
        super().__init__(user_subscription_repository)

    def create_user_subscription(self, payload):
        try:
            # check if subscription exist
            subscription_code = payload["data"]["subscription_code"]

            paystack_subscription = requests.get(
                settings.PAYSTACK_SUBSCRIPTION_URL + f"/{subscription_code}",
                headers=settings.PAYSTACK_HEADERS,
            )

            logging.info(paystack_subscription.raise_for_status())
            paystack_subscription.raise_for_status()

            return self.user_subscription_repository.create_user_subscription(payload)
        except Exception as e:
            raise e
