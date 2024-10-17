import math
from contextlib import AbstractContextManager
from datetime import date
from typing import Callable, List, Tuple

import requests
from requests.exceptions import HTTPError
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.core.constants import FREE_PACKAGE, FREE_PACKAGE_ITEMS
from app.core.settings import settings
from app.model.business_profile import BusinessProfile
from app.model.package import Package
from app.model.package_item_assignment import PackageItemAssignment
from app.model.plan_upgrade import PlanUpgrade
from app.model.subscription import Subscription
from app.model.user import User
from app.model.user_subscription import UserSubscription
from app.repository.base_repository import BaseRepository
from app.schema.subscription import PaystackSubscriptionPayload
from app.util.enums import ActiveStatus


class SubscriptionRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Subscription)

    def read_all_subscriptions_(self):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .options(joinedload(Subscription.user))
                .options(joinedload(Subscription.package))
                .all()
            )

    def get_subscription_by_business_uuid(self, business_profile_uuid: str, plan: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter_by(business_profile_uuid=business_profile_uuid)
                .filter_by(plan=plan)
                .first()
            )

    def get_paystack_subscription(self, subscription_code: str):
        with self.session_factory() as session:
            paystack_subscription = requests.get(
                settings.PAYSTACK_SUBSCRIPTION_URL + f"/{subscription_code}",
                headers=settings.PAYSTACK_HEADERS,
            )

            paystack_subscription.raise_for_status()

            if paystack_subscription.status_code == 200:
                subscription = paystack_subscription.json()["data"]

                user_email = subscription["customer"]["email"]

                user = session.query(User).filter_by(email_address=user_email).first()
                subscription["customer"]["first_name"] = user.first_name
                subscription["customer"]["last_name"] = user.last_name
                subscription["customer"]["phone"] = user.phone_number
                subscription["customer"]["user_uuid"] = user.uuid

                plan_code = subscription["plan"]["plan_code"]

                package_items = (
                    session.query(PackageItemAssignment)
                    .filter(PackageItemAssignment.paystack_plan_code == plan_code)
                    .options(joinedload(PackageItemAssignment.package_item))
                    .all()
                )

                subscription["package_items"] = package_items

                return subscription

            return paystack_subscription.json()

    def get_paystack_subscription_by_email(self, email: str):
        with self.session_factory() as session:
            user = (
                session.query(UserSubscription)
                .filter(UserSubscription.user_email == email)
                .first()
            )
            if user:
                paystack_subscription = self.get_paystack_subscription(
                    user.subscription_code
                )
                # return paystack_subscription["package_items"]
                subscription = {
                    "package_name": paystack_subscription["plan"]["name"],
                    "package_items": paystack_subscription["package_items"],
                }
                return subscription
            else:
                subscription = {
                    "package_name": FREE_PACKAGE,
                    "package_items": FREE_PACKAGE_ITEMS,
                }
            return subscription

    def create_paystack_subscription(self, payload: PaystackSubscriptionPayload):
        try:
            # Create Paystack subscription
            subscription_response = requests.post(
                settings.PAYSTACK_INITIALIZE_SUBSCRIPTION_URL,
                headers=settings.PAYSTACK_HEADERS,
                json=payload.dict(),
            )
            subscription_response.raise_for_status()  # Raise exception for HTTP errors

            # save subscription in db

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

    def read_all_paystack_subscriptions(self, page=1, page_size=10):
        # Ensure page and page_size are integers
        page = int(page)
        page_size = int(page_size)

        with self.session_factory() as session:
            # Prepare pagination parameters for Paystack API
            params = {"page": page, "perPage": page_size}

            paystack_subscription = requests.get(
                settings.PAYSTACK_SUBSCRIPTION_URL,
                headers=settings.PAYSTACK_HEADERS,
                params=params,  # Adding pagination parameters to the request
            )

            if paystack_subscription.status_code == 200:
                subscriptions = []
                response_data = paystack_subscription.json()

                # Extract metadata (total count, etc.) and ensure they are integers
                total_subscriptions = int(response_data.get("meta", {}).get("total", 0))
                current_page = int(response_data.get("meta", {}).get("page", page))
                per_page = int(response_data.get("meta", {}).get("perPage", page_size))

                # Calculate total pages
                total_pages = math.ceil(total_subscriptions / per_page)

                for subscription in response_data["data"]:
                    user_email = subscription["customer"]["email"]

                    user = (
                        session.query(User).filter_by(email_address=user_email).first()
                    )

                    if not user:
                        return f"{user_email} not found"

                    # Update subscription with user details
                    subscription["customer"]["first_name"] = user.first_name
                    subscription["customer"]["last_name"] = user.last_name
                    subscription["customer"]["phone"] = user.phone_number
                    subscription["customer"]["user_uuid"] = user.uuid

                    plan_code = subscription["plan"]["plan_code"]

                    # Fetch package items based on plan code
                    package_items = (
                        session.query(PackageItemAssignment)
                        .filter(PackageItemAssignment.paystack_plan_code == plan_code)
                        .options(joinedload(PackageItemAssignment.package_item))
                        .all()
                    )

                    subscription["package_items"] = package_items
                    subscriptions.append(subscription)

                # Return result with pagination metadata
                result = {
                    "subscriptions": subscriptions,
                    "page": current_page,
                    "page_size": per_page,
                    "total": total_subscriptions,
                    "total_pages": total_pages,
                }
                return result

            return paystack_subscription.json()

    def read_all_subscriptions(
        self, page=1, page_size=10
    ) -> Tuple[List[Subscription], int]:
        with self.session_factory() as session:
            offset = (page - 1) * page_size

            query = session.query(self.model)
            total_subscription = query.count()

            query = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )

            subscriptions = (
                query.options(
                    joinedload(Subscription.user)
                    .joinedload(User.business_profile)
                    .joinedload(BusinessProfile.users)
                )
                .options(
                    joinedload(Subscription.package).joinedload(
                        Package.package_item_assignments
                    )
                )
                .all()
            )

            return subscriptions, total_subscription

    def subscriptions_today(self):
        with self.session_factory() as session:
            today = date.today()
            # Query for plan upgrades with start date today
            plan_upgrades_today = (
                session.query(PlanUpgrade).filter(PlanUpgrade.start_date == today).all()
            )

            # Create subscriptions for each plan upgrade
            for plan_upgrade in plan_upgrades_today:
                if plan_upgrade.package.package_price == plan_upgrade.payment.amount:
                    existing_subscription = (
                        session.query(self.model)
                        .filter(self.model.user_uuid == plan_upgrade.user_uuid)
                        .first()
                    )

                    if existing_subscription:
                        # Update existing subscription
                        existing_subscription.subscription_type = (
                            plan_upgrade.subscription_type
                        )
                        existing_subscription.subscription_period = (
                            plan_upgrade.subscription_period
                        )
                        existing_subscription.start_date = today
                        existing_subscription.end_date = plan_upgrade.end_date
                        existing_subscription.subscription_amount = (
                            plan_upgrade.package.package_price,
                        )
                        existing_subscription.package_uuid = (
                            plan_upgrade.package_uuid,
                        )
                        existing_subscription.status = ActiveStatus.ACTIVE
                    else:
                        # Create new subscription
                        subscription = Subscription(
                            subscription_type=plan_upgrade.subscription_type,
                            subscription_period=plan_upgrade.subscription_period,
                            start_date=today,
                            end_date=plan_upgrade.end_date,
                            subscription_amount=plan_upgrade.package.package_price,
                            user_uuid=plan_upgrade.user_uuid,
                            package_uuid=plan_upgrade.package_uuid,
                            status=ActiveStatus.ACTIVE,
                        )
                        session.add(subscription)
                session.commit()
