from contextlib import AbstractContextManager
from datetime import date
from typing import Callable, List, Tuple

import requests
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.core.settings import settings
from app.model.business_profile import BusinessProfile
from app.model.package import Package
from app.model.package_item_assignment import PackageItemAssignment
from app.model.plan_upgrade import PlanUpgrade
from app.model.subscription import Subscription
from app.model.user import User
from app.repository.base_repository import BaseRepository
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

    def get_paystack_subscription(self, subscription_code: str):
        with self.session_factory() as session:
            paystack_subscription = requests.get(
                settings.PAYSTACK_SUBSCRIPTION_URL + f"/{subscription_code}",
                headers=settings.PAYSTACK_HEADERS,
            )

            if paystack_subscription.status_code == 200:
                subscription = paystack_subscription.json()["data"]

                user_email = subscription["customer"]["email"]

                user = session.query(User).filter_by(email_address=user_email).first()
                subscription["customer"]["first_name"] = user.first_name
                subscription["customer"]["last_name"] = user.last_name
                subscription["customer"]["phone"] = user.phone_number

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

    def read_all_paystack_subscriptions(self):
        with self.session_factory() as session:
            paystack_subscription = requests.get(
                settings.PAYSTACK_SUBSCRIPTION_URL,
                headers=settings.PAYSTACK_HEADERS,
            )
            if paystack_subscription.status_code == 200:
                subscriptions = []
                for subscription in paystack_subscription.json()["data"]:
                    user_email = subscription["customer"]["email"]
                    user = (
                        session.query(User).filter_by(email_address=user_email).first()
                    )
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
                    subscriptions.append(subscription)

                return subscriptions
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
