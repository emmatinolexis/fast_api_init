import logging
from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session
import requests
from app.schema.subscription import PaystackSubscriptionPayload
from requests.exceptions import HTTPError

from app.model.user import User
from app.model.user_subscription import UserSubscription
from app.repository.base_repository import BaseRepository
from app.core.settings import settings
from app.model.payment import Payment


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
            event_type = payload.get("event")

            logging.info(payload)

            user_email = payload["data"]["customer"]["email"]
            user = self.get_user_by_email(session, user_email)

            if not user:
                user_not_found = f"user with email {user_email} not found, cannot process subscription event: {event_type}"
                logging.info(
                   user_not_found
                )
                return user_not_found

            existing_subscription = self.get_user_subscription_(session, user_email)

            if event_type in ["subscription.not_renew", "invoice.payment_failed"]:
                self.handle_subscription_deactivation(
                    session, user_email, existing_subscription
                )
            elif event_type == "subscription.create":
                subscription_code = payload["data"]["subscription_code"]
                subscription_plan = payload["data"]["plan"]
                self.handle_subscription_creation(
                    session, user_email, subscription_code, existing_subscription, subscription_plan
                )
            elif event_type == "charge.success":
                payment_data = Payment(
                    reference_no=payload["data"]["reference"],
                    amount=payload["data"]["amount"],
                    status=payload["data"]["status"],
                    user_email=payload["data"]["customer"]["email"],
                    payment_type=payload["data"]["metadata"]["payment_type"],
                    business_profile_uuid=payload["data"]["metadata"]["business_profile_uuid"],
                    channel=payload["data"]["channel"]
                )
                session.add(payment_data)
                session.commit()
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

    def get_subscription_by_business_uuid(self, business_profile_uuid: str, plan: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter_by(business_profile_uuid=business_profile_uuid)
                .filter_by(plan_code=plan)
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
        self, session, user_email, subscription_code, existing_subscription, subscription_plan
    ):
        if existing_subscription:
            existing_subscription.subscription_code = subscription_code
            existing_subscription.plan = subscription_plan
            session.commit()
            session.refresh(existing_subscription)
            logging.info("Subscription updated successfully")
            return
        else:
            user_subscription = UserSubscription(
                user_email=user_email, subscription_code=subscription_code
            )
            session.add(user_subscription)
            session.commit()
            logging.info("Subscription created successfully")
            return

    def create_paystack_subscription(self, payload: dict, business_profile_uuid: str, update_subscription: bool = False):
        try:
            with self.session_factory() as session:

                payload_email = payload.get("email")
                payload_plan = payload.get("plan")

                # Create Paystack subscription
                subscription_response = requests.post(
                    settings.PAYSTACK_INITIALIZE_SUBSCRIPTION_URL,
                    headers=settings.PAYSTACK_HEADERS,
                    json=payload,
                )

                subscription_response.raise_for_status()

                if update_subscription:
                    subscription = (session.query(self.model)
                                    .filter_by(user_email=payload_email)
                                    .first())
                    subscription.plan_code = payload_plan
                else:
                    # save subscription in db
                    data = UserSubscription(
                        user_email=payload_email,
                        plan_code=payload_plan,
                        business_profile_uuid=business_profile_uuid
                    )
                    session.add(data)

                session.commit()
                # If successful, return subscription data
                subscription_data = subscription_response.json()["data"]
                return subscription_data

        except HTTPError:
            # If there's an HTTP error, return the error response from Paystack
            error_message = subscription_response.json().get(
                "message", "Unknown HTTP Error"
            )
            return f"Error creating subscription: {error_message}"

        except Exception as err:
            # For any other exceptions, return a generic error message
            return f"Error creating subscription: {str(err)}"

    def update_existing_paystack_subscription(self, payload: PaystackSubscriptionPayload, business_profile_uuid: str):
        try:
            with self.session_factory() as session:

                # Create Paystack subscription
                subscription_response = requests.post(
                    settings.PAYSTACK_INITIALIZE_SUBSCRIPTION_URL,
                    headers=settings.PAYSTACK_HEADERS,
                    json=payload.dict(),
                )
                subscription_response.raise_for_status()  # Raise exception for HTTP errors

                # save subscription in db
                data = UserSubscription(
                    plan_code=payload.plan
                )
                session.refresh(data)
                session.commit()

                # If successful, return subscription data
                subscription_data = subscription_response.json()["data"]
                return subscription_data

        except HTTPError:
            # If there's an HTTP error, return the error response from Paystack
            error_message = subscription_response.json().get(
                "message", "Unknown HTTP Error"
            )
            return f"Error creating subscription: {error_message}"

        except Exception as err:
            # For any other exceptions, return a generic error message
            return f"Error creating subscription: {str(err)}"
