import logging
from contextlib import AbstractContextManager
from typing import Callable

import requests
from requests.exceptions import HTTPError
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.model.payment import Payment
from app.model.user import User
from app.model.user_subscription import UserSubscription
from app.repository.base_repository import BaseRepository
from app.schema.subscription import PaystackSubscriptionPayload
from app.util.enums import SubscriptionStatus


class UserSubscriptionRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, UserSubscription)

    # def get_user_subscription(self, user_email):
    #     with self.session_factory() as session:
    #         user = session.query(User).filter(User.email_address == user_email).first()
    #         user_plan = (
    #             session.query(self.model)
    #             .filter(self.model.business_profile_uuid == user.business_profile_uuid)
    #             .first()
    #         )
    #         return user_plan

    def get_user_subscription(self, user_email):
        with self.session_factory() as session:
            # Fetch the user from the database
            user = session.query(User).filter(User.email_address == user_email).first()

            if not user:
                logging.warning(f"No user found with email: {user_email}")
                return None

            # Fetch the user's subscription plan
            user_plan = (
                session.query(self.model)
                .filter(self.model.business_profile_uuid == user.business_profile_uuid)
                .first()
            )

            if not user_plan:
                logging.warning(f"No subscription plan found for user: {user_email}")
                return None

            return user_plan

    def create_user_subscription(self, payload):
        with self.session_factory() as session:
            event_type = payload.get("event")

            logging.info(payload)

            user_email = payload["data"]["customer"]["email"]
            user = self.get_user_by_email(session, user_email)

            if not user:
                user_not_found = f"user with email {user_email} not found, cannot process subscription event: {event_type}"
                logging.info(user_not_found)
                return

            # get all existing subscription and update statuses to non-renewing
            existing_subscription = self.get_user_subscription_(
                session, user_email, payload["data"]["plan"]["plan_code"]
            )

            if existing_subscription:
                subscription_status = None  # Initialize the variable

                if event_type in ["subscription.not_renew", "invoice.payment_failed"]:
                    self.handle_subscription_deactivation(
                        session, user_email, existing_subscription
                    )
                elif event_type == "subscription.create":
                    subscription_code = payload["data"]["subscription_code"]
                    subscription_status = payload["data"]["status"]
                    next_payment_date = payload["data"]["next_payment_date"]
                    self.handle_subscription_creation(
                        session,
                        # user_email,
                        subscription_code,
                        existing_subscription,
                        subscription_status,
                        next_payment_date,
                    )
                elif event_type == "charge.success":
                    payment_data = Payment(
                        reference_no=payload["data"]["reference"],
                        amount=payload["data"]["amount"],
                        status=payload["data"]["status"],
                        user_email=payload["data"]["customer"]["email"],
                        payment_type=payload["data"]["metadata"]["payment_type"],
                        business_profile_uuid=payload["data"]["metadata"][
                            "business_profile_uuid"
                        ],
                        channel=payload["data"]["channel"],
                    )
                    session.add(payment_data)
                    session.commit()
                else:
                    logging.info(f"Unhandled event type: {event_type}")
                    return

                # Only reference `subscription_status` if it has been set
                success_msg = f"Subscription status: {subscription_status if subscription_status else 'Unknown'}"
                logging.info(success_msg)
                return success_msg
            else:
                logging.error("Subscription not found")
                return


    def get_user_by_email(self, session, user_email):
        return session.query(User).filter(User.email_address == user_email).first()

    def get_user_subscription_(self, session, user_email, plan_code):
        return (
            session.query(UserSubscription)
            .filter(UserSubscription.user_email == user_email)
            .filter(UserSubscription.plan_code == plan_code)
            .first()
        )

    def get_active_subscription_by_business_uuid(
        self, business_profile_uuid: str, plan: str
    ):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter_by(business_profile_uuid=business_profile_uuid)
                .filter_by(plan_code=plan)
                .filter_by(status=SubscriptionStatus.ACTIVE)
                .first()
            )

    def handle_subscription_deactivation(
        self, session, user_email, existing_subscription
    ):
        existing_subscription.status = SubscriptionStatus.NON_RENEWING
        session.commit()
        session.refresh(existing_subscription)

    def handle_subscription_creation(
        self,
        session,
        subscription_code,
        existing_subscription,
        subscription_status,
        next_payment_date,
    ):
        existing_subscription.subscription_code = subscription_code
        existing_subscription.status = subscription_status
        existing_subscription.next_payment_date = next_payment_date
        session.commit()
        session.refresh(existing_subscription)
        logging.info("Subscription updated successfully")
        return

    def create_paystack_subscription(
        self,
        payload: dict,
        plan: dict,
        business_profile_uuid: str,
        update_subscription: bool = False,
    ):
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
                if subscription_response.json().get("status"):
                    if update_subscription:
                        subscription = (
                            session.query(self.model)
                            .filter_by(user_email=payload_email)
                            .first()
                        )
                        subscription.plan_code = payload_plan
                    else:
                        # save subscription in db
                        data = UserSubscription(
                            user_email=payload_email,
                            plan_code=payload_plan,
                            business_profile_uuid=business_profile_uuid,
                            status=SubscriptionStatus.PENDING,
                            plan={
                                "name": plan.get("name"),
                                "amount": plan.get("amount"),
                                "plan_code": plan.get("plan_code"),
                            },
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

    def update_existing_paystack_subscription(
        self, payload: PaystackSubscriptionPayload, business_profile_uuid: str
    ):
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
                data = UserSubscription(plan_code=payload.plan)
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
