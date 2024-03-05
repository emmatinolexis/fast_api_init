import requests
from fastapi import BackgroundTasks

from app.core.settings import settings
from app.repository.subscription_repository import SubscriptionRepository
from app.schema.subscription import PaystackSubscriptionPayload
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

    def toggle_subscription_status(self, subscription_code):
        try:
            # Retrieve subscription details
            paystack_subscription = requests.get(
                settings.PAYSTACK_SUBSCRIPTION_URL + f"/{subscription_code}",
                headers=settings.PAYSTACK_HEADERS,
            )

            paystack_subscription.raise_for_status()  # Raise an error for non-200 responses

            subscription = paystack_subscription.json()
            subscription_status = subscription["data"]["status"]
            update_data = {
                "code": subscription_code,
                "token": subscription["data"]["email_token"],
            }
            # Toggle subscription status
            if subscription_status == "active":
                updated_subscription = requests.post(
                    settings.PAYSTACK_SUBSCRIPTION_URL + "/disable",
                    headers=settings.PAYSTACK_HEADERS,
                    json=update_data,
                )

            else:
                updated_subscription = requests.post(
                    settings.PAYSTACK_SUBSCRIPTION_URL + "/enable",
                    headers=settings.PAYSTACK_HEADERS,
                    json=update_data,
                )

            return updated_subscription.json()

        except Exception as e:
            raise e

    def get_all_paystack_subscriptions(self):
        try:
            return self.subscription_repository.read_all_paystack_subscriptions()
        except Exception as e:
            raise e

    def get_paystack_subscription(self, subscription_code):
        try:
            return self.subscription_repository.get_paystack_subscription(
                subscription_code
            )
        except Exception as e:
            raise e

    def subscriptions_upgrade(self, background_tasks: BackgroundTasks):
        return background_tasks.add_task(
            self.subscription_repository.subscriptions_today()
        )

    def create_paystack_subscription(self, payload: PaystackSubscriptionPayload):
        try:
            subscription = requests.post(
                settings.PAYSTACK_INITIALIZE_SUBSCRIPTION_URL,
                headers=settings.PAYSTACK_HEADERS,
                json=payload.dict(),
            )
            return subscription.json()
        except Exception as e:
            raise e
