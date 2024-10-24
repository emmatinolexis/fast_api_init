from app.repository.user_subscription_repository import UserSubscriptionRepository

from app.service.base_service import BaseService


class UserSubscriptionService(BaseService):
    def __init__(self, user_subscription_repository: UserSubscriptionRepository):
        self.user_subscription_repository = user_subscription_repository
        super().__init__(user_subscription_repository)

    def create_user_subscription(self, payload):
        try:
            return self.user_subscription_repository.create_user_subscription(payload)
        except Exception as e:
            raise e

    def create_paystack_subscription(
        self,
        payload: dict,
        plan: dict,
        business_profile_uuid: str,
        update_subscription: bool = False,
    ):
        try:
            return self.user_subscription_repository.create_paystack_subscription(
                payload, plan, business_profile_uuid, update_subscription
            )
        except Exception as e:
            raise e

    def get_subscription_by_business_uuid(self, business_profile_uuid: str, plan: str):
        try:
            return self.user_subscription_repository.get_subscription_by_business_uuid(
                business_profile_uuid, plan
            )
        except Exception as e:
            raise e

    def get_subscription_by_email(self, email: str):
        try:
            return self.user_subscription_repository.get_user_subscription(email)
        except Exception as e:
            raise e
