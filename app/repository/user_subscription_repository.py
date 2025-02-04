import logging
from contextlib import AbstractContextManager
from typing import Callable

import aiohttp
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.model.payment import Payment
from app.model.user import User
from app.model.user_subscription import UserSubscription
from app.repository.base_repository import BaseRepository
from app.schema.subscription import PaystackSubscriptionPayload
from app.util.enums import SubscriptionStatus


class UserSubscriptionRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, UserSubscription)

    async def get_user_subscription(self, user_email):
        async with self.session_factory() as session:
            # Fetch the user from the database
            user = await session.execute(
                select(User).filter(User.email_address == user_email)
            )
            user = user.scalars().first()

            if not user:
                logging.warning(f"No user found with email: {user_email}")
                return None

            # Fetch the user's subscription plan
            user_plan = await session.execute(
                select(self.model)
                .filter(self.model.business_profile_uuid == user.business_profile_uuid)
                .filter(self.model.status == SubscriptionStatus.ACTIVE)
            )
            user_plan = user_plan.scalars().first()

            if not user_plan:
                logging.warning(f"No subscription plan found for user: {user_email}")
                return None

            return user_plan

    async def create_user_subscription(self, payload):
        async with self.session_factory() as session:
            event_type = payload.get("event")

            logging.info(payload)

            user_email = payload["data"]["customer"]["email"]
            user = await self.get_user_by_email(session, user_email)

            if not user:
                user_not_found = f"user with email {user_email} not found, cannot process subscription event: {event_type}"
                logging.info(user_not_found)
                return

            # get active subscription
            existing_active_subscription = await self.get_user_subscription_(
                session, user_email, payload["data"]["plan"]["plan_code"]
            )

            if existing_active_subscription:
                subscription_status = None  # Initialize the variable

                # deactivate expired subscription if paystack event type is subscription.not_renew
                if event_type in ["subscription.not_renew"]:
                    await self.handle_subscription_deactivation(
                        session, existing_active_subscription
                    )

                # create subscription if paystack event type subscription.create
                elif event_type == "subscription.create":

                    await self.update_all_business_subscriptions_(
                        session, payload["data"]["customer"]["business_profile_uuid"]
                    )

                    subscription_code = payload["data"]["subscription_code"]
                    subscription_status = SubscriptionStatus.ACTIVE
                    next_payment_date = payload["data"]["next_payment_date"]

                    await self.handle_subscription_creation(
                        session,
                        subscription_code,
                        existing_active_subscription,
                        subscription_status,
                        next_payment_date,
                    )

                # create payment if paystack event type is charge.success
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
                    await session.commit()
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

    async def get_user_by_email(self, session, user_email):
        result = await session.execute(
            select(User).filter(User.email_address == user_email)
        )
        return result.scalars().first()

    async def get_user_subscription_(self, session, user_email, plan_code):
        result = await session.execute(
            select(UserSubscription)
            .filter(UserSubscription.user_email == user_email)
            .filter(UserSubscription.plan_code == plan_code)
            .filter(UserSubscription.status == SubscriptionStatus.ACTIVE)
        )
        return result.scalars().first()

    async def update_all_business_subscriptions_(self, session, business_uuid):
        await session.execute(
            update(UserSubscription)
            .where(UserSubscription.business_profile_uuid == business_uuid)
            .values(status=SubscriptionStatus.NON_RENEWING)
        )
        await session.commit()

    async def get_active_subscription_by_business_uuid(
        self, business_profile_uuid: str, plan: str
    ):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model)
                .filter_by(business_profile_uuid=business_profile_uuid)
                .filter_by(plan_code=plan)
                .filter_by(status=SubscriptionStatus.ACTIVE)
            )
            return result.scalars().first()

    async def handle_subscription_deactivation(self, session, existing_subscription):
        existing_subscription.status = SubscriptionStatus.NON_RENEWING
        await session.commit()
        await session.refresh(existing_subscription)

    async def handle_subscription_creation(
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
        await session.commit()
        await session.refresh(existing_subscription)
        logging.info("Subscription updated successfully")
        return

    async def create_paystack_subscription(
        self,
        payload: dict,
        plan: dict,
        business_profile_uuid: str,
        update_subscription: bool = False,
    ):
        async with aiohttp.ClientSession() as session:
            try:
                payload_email = payload.get("email")
                payload_plan = payload.get("plan")

                # Create Paystack subscription
                async with session.post(
                    settings.PAYSTACK_INITIALIZE_SUBSCRIPTION_URL,
                    headers=settings.PAYSTACK_HEADERS,
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    subscription_response = await response.json()

                    if subscription_response.get("status"):
                        async with self.session_factory() as db_session:
                            if update_subscription:
                                subscription = await db_session.execute(
                                    select(self.model).filter_by(
                                        user_email=payload_email
                                    )
                                )
                                subscription = subscription.scalars().first()
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
                                db_session.add(data)

                            await db_session.commit()
                            # If successful, return subscription data
                            subscription_data = subscription_response["data"]
                            return subscription_data

            except aiohttp.ClientResponseError as e:
                # If there's an HTTP error, return the error response from Paystack
                error_message = await e.response.json()
                return f"Error creating subscription: {error_message.get('message', 'Unknown HTTP Error')}"

            except Exception as err:
                # For any other exceptions, return a generic error message
                return f"Error creating subscription: {str(err)}"

    async def update_existing_paystack_subscription(
        self, payload: PaystackSubscriptionPayload, business_profile_uuid: str
    ):
        async with aiohttp.ClientSession() as session:
            try:
                # Create Paystack subscription
                async with session.post(
                    settings.PAYSTACK_INITIALIZE_SUBSCRIPTION_URL,
                    headers=settings.PAYSTACK_HEADERS,
                    json=payload.dict(),
                ) as response:
                    response.raise_for_status()
                    subscription_response = await response.json()

                    async with self.session_factory() as db_session:
                        # save subscription in db
                        data = UserSubscription(plan_code=payload.plan)
                        await db_session.refresh(data)
                        await db_session.commit()

                        # If successful, return subscription data
                        subscription_data = subscription_response["data"]
                        return subscription_data

            except aiohttp.ClientResponseError as e:
                # If there's an HTTP error, return the error response from Paystack
                error_message = await e.response.json()
                return f"Error creating subscription: {error_message.get('message', 'Unknown HTTP Error')}"

            except Exception as err:
                # For any other exceptions, return a generic error message
                return f"Error creating subscription: {str(err)}"
