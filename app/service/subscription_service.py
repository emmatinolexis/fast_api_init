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

    # def get_all_paystack_subscriptions(self, page, page_size):
    #     try:
    #
    #         return self.subscription_repository.read_all_paystack_subscriptions(
    #             page, page_size
    #         )
    #     except Exception as e:
    #         raise e

    def get_all_paystack_subscriptions(self, page, page_size):
        try:
            # Fetch subscription data
            result = self.subscription_repository.read_all_paystack_subscriptions(page, page_size)

            # Extract relevant fields from each subscription
            subscriptions_data = [
                {
                    "uuid": sub.uuid,
                    "customer": {
                        "first_name": sub.user.first_name,
                        "last_name": sub.user.first_name,
                    },
                    "plan": {
                            "name": sub.plan.get("name", "N/A")
                    },
                    "status": sub.status,
                    "amount": sub.plan.get("amount", 0),
                    "createdAt": sub.created_at,
                }
                for sub in result["subscriptions"]
            ]

            # Construct final response
            return {
                "subscriptions": subscriptions_data,
                "page": result["page"],
                "page_size": result["page_size"],
                "total": result["total"],
                "total_pages": result["total_pages"],
                "total_amount": result["total_amount"],
            }

        except Exception as e:
            raise e


    def get_paystack_subscription(self, subscription_code):
        try:
            return self.subscription_repository.get_paystack_subscription(
                subscription_code
            )
        except Exception as e:
            raise e

    def get_paystack_payments(self):
        try:
            paystack_payments = requests.get(
                settings.PAYSTACK_PAYMENT_URL, headers=settings.PAYSTACK_HEADERS
            )

            paystack_payments.raise_for_status()  # Raise an error for non-200 responses

            payments = paystack_payments.json()["data"]
            return payments
        except Exception as e:
            raise e

    def get_subscription_by_business_uuid(self, business_profile_uuid: str, plan: str):
        try:
            return self.subscription_repository.get_subscription_by_business_uuid(
                business_profile_uuid, plan
            )
        except Exception as e:
            raise e

    def get_paystack_subscription_by_email(self, email):
        try:
            return self.subscription_repository.get_paystack_subscription_by_email(
                email
            )
        except Exception as e:
            raise e

    def subscriptions_upgrade(self, background_tasks: BackgroundTasks):
        return background_tasks.add_task(
            self.subscription_repository.subscriptions_today()
        )

    def create_paystack_subscription(self, payload: PaystackSubscriptionPayload):
        try:
            return self.subscription_repository.create_paystack_subscription(payload)
        except Exception as e:
            raise e
