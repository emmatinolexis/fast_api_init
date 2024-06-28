import logging
from contextlib import AbstractContextManager
from typing import Callable

import requests
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.model.user import User
from app.model.user_subscription import UserSubscription
from app.repository.base_repository import BaseRepository


class UserSubscriptionRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, UserSubscription)

    def get_user_subscription(self, user_email):
        with self.session_factory() as session:
            user_plan = (
                session.query(self.model)
                .filter(self.model.user_email == user_email)
                .first()
            )
            return user_plan

    def create_user_subscription(self, payload):
        with self.session_factory() as session:
            event_type = payload["event"]
            logging.info(payload)

            if event_type == "subscription.create":
                user_email = payload["data"]["customer"]["email"]
                subscription_code = payload["data"]["subscription_code"]

                user = (
                    session.query(User).filter(User.email_address == user_email).first()
                )

                if user is None:
                    raise Exception("User not found")

                # check if user already has plan
                existing_subscription = (
                    session.query(UserSubscription)
                    .filter(UserSubscription.user_email == user_email)
                    .first()
                )

                if existing_subscription:
                    if existing_subscription.subscription_code == subscription_code:
                        raise Exception("You have already subscribed to this plan")

                    # get paystack existing plan
                    paystack_existing_subscription = requests.get(
                        settings.PAYSTACK_SUBSCRIPTION_URL
                        + f"/{existing_subscription.subscription_code}",
                        headers=settings.PAYSTACK_HEADERS,
                    )

                    paystack_existing_subscription_code = (
                        paystack_existing_subscription.json()["data"][
                            "subscription_code"
                        ]
                    )

                    paystack_existing_subscription_token = (
                        paystack_existing_subscription.json()["data"]["email_token"]
                    )

                    # deactivate existing package from autorenewal
                    paystack_subscription = requests.post(
                        settings.PAYSTACK_SUBSCRIPTION_URL + "/disable",
                        headers=settings.PAYSTACK_HEADERS,
                        json={
                            "code": paystack_existing_subscription_code,
                            "token": paystack_existing_subscription_token,
                        },
                    )

                    logging.info(paystack_subscription.raise_for_status())

                    # update existing user plan with new plan code
                    existing_subscription.subscription_code = subscription_code
                    session.commit()
                    session.refresh(existing_subscription)

                    logging.info("Subscription updated successfully")

                    return "Subscription updated successfully"
                else:
                    user_subscription = UserSubscription(
                        user_email=user_email, subscription_code=subscription_code
                    )

                    session.add(user_subscription)
                    session.commit()

                    logging.info("Subscription created successfully")

                    return "Subscription created successfully"
