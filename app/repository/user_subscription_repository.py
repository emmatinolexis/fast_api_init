import logging
from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

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

            user_email = payload["data"]["customer"]["email"]
            user = self.get_user_by_email(session, user_email)

            if user is None:
                logging.info(
                    f"user with email {user_email} not found, cannot process subscription event: {event_type}"
                )
                return

            existing_subscription = self.get_user_subscription_(session, user_email)

            if event_type in ["subscription.not_renew", "invoice.payment_failed"]:
                self.handle_subscription_deactivation(
                    session, user_email, existing_subscription
                )
            elif event_type == "subscription.create":
                subscription_code = payload["data"]["subscription_code"]
                self.handle_subscription_creation(
                    session, user_email, subscription_code, existing_subscription
                )
            else:
                logging.info(f"Unhandled event type: {event_type}")

    def get_user_by_email(self, session, user_email):
        return session.query(User).filter(User.email_address == user_email).first()

    def get_user_subscription_(self, session, user_email):
        return (
            session.query(UserSubscription)
            .filter(UserSubscription.user_email == user_email)
            .first()
        )

    def handle_subscription_deactivation(
        self, session, user_email, existing_subscription
    ):
        if existing_subscription:
            session.delete(existing_subscription)
            session.commit()
            logging.info(
                f"Subscription for user with email {user_email} has been deleted"
            )
        else:
            logging.info(
                f"No existing subscription found for user with email {user_email}"
            )

    def handle_subscription_creation(
        self, session, user_email, subscription_code, existing_subscription
    ):
        if existing_subscription:
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
