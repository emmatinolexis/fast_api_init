from datetime import date
from typing import Callable, List, Tuple

import aiohttp
from sqlalchemy import Numeric, String, cast, desc, func, or_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

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
from app.util.enums import ActiveStatus, SubscriptionStatus


class SubscriptionRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, Subscription)

    async def read_all_subscriptions_(self):
        async with self.session_factory() as session:
            result = await session.execute(
                session.query(self.model)
                .options(joinedload(Subscription.user))
                .options(joinedload(Subscription.package))
            )
            return result.unique().scalars().all()

    async def get_subscription_by_business_uuid(
        self, business_profile_uuid: str, plan: str
    ):
        async with self.session_factory() as session:
            result = await session.execute(
                session.query(self.model)
                .filter_by(business_profile_uuid=business_profile_uuid)
                .filter_by(plan=plan)
            )
            return result.scalar()

    async def get_paystack_subscription(self, subscription_code: str):
        async with self.session_factory() as session:
            async with aiohttp.ClientSession() as client_session:
                async with client_session.get(
                    settings.PAYSTACK_SUBSCRIPTION_URL + f"/{subscription_code}",
                    headers=settings.PAYSTACK_HEADERS,
                ) as response:
                    response.raise_for_status()
                    paystack_subscription = await response.json()

            if response.status == 200:
                subscription = paystack_subscription["data"]

                user_email = subscription["customer"]["email"]

                result = await session.execute(
                    session.query(User).filter_by(email_address=user_email)
                )
                user = result.scalar()
                subscription["customer"]["first_name"] = user.first_name
                subscription["customer"]["last_name"] = user.last_name
                subscription["customer"]["phone"] = user.phone_number
                subscription["customer"]["user_uuid"] = user.uuid

                plan_code = subscription["plan"]["plan_code"]

                result = await session.execute(
                    session.query(PackageItemAssignment)
                    .filter(PackageItemAssignment.paystack_plan_code == plan_code)
                    .options(joinedload(PackageItemAssignment.package_item))
                )
                package_items = result.unique().scalars().all()

                subscription["package_items"] = package_items

                return subscription

            return paystack_subscription

    async def get_paystack_subscription_by_email(self, email: str):
        async with self.session_factory() as session:
            result = await session.execute(
                session.query(UserSubscription).filter(
                    UserSubscription.user_email == email
                )
            )
            user = result.scalar()
            if user:
                paystack_subscription = await self.get_paystack_subscription(
                    user.subscription_code
                )
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

    async def create_paystack_subscription(self, payload: PaystackSubscriptionPayload):
        try:
            async with aiohttp.ClientSession() as client_session:
                async with client_session.post(
                    settings.PAYSTACK_INITIALIZE_SUBSCRIPTION_URL,
                    headers=settings.PAYSTACK_HEADERS,
                    json=payload.dict(),
                ) as response:
                    response.raise_for_status()
                    subscription_data = await response.json()
                    return subscription_data["data"]

        except aiohttp.ClientResponseError as e:
            return f"Error creating subscription: {e.message}"

        except Exception as err:
            return f"Error creating subscription: {str(err)}"

    async def read_all_paystack_subscriptions(self, page=1, per_page=10):
        page = int(page)
        per_page = int(per_page)
        offset_value = (page - 1) * per_page

        async with self.session_factory() as session:
            query = (
                session.query(
                    UserSubscription,
                    func.count().over().label("total_subscriptions"),
                    func.coalesce(
                        func.sum(
                            cast(
                                cast(UserSubscription.plan["amount"], JSONB).cast(
                                    String
                                ),
                                Numeric,
                            )
                        ).over(),
                        0,
                    ).label("total_amount"),
                )
                .options(joinedload(UserSubscription.user))
                .filter(
                    or_(
                        UserSubscription.status == SubscriptionStatus.ACTIVE.value,
                        UserSubscription.status
                        == SubscriptionStatus.NON_RENEWING.value,
                    )
                )
                .limit(per_page)
                .offset(offset_value)
            )

            result = await session.execute(query)
            results = result.unique().scalars().all()

            if results:
                total_subscriptions = results[0].total_subscriptions
                total_amount = results[0].total_amount
            else:
                total_subscriptions = 0
                total_amount = 0

            subscriptions = [row[0] for row in results]

            total_pages = (total_subscriptions + per_page - 1) // per_page

            result = {
                "subscriptions": subscriptions,
                "page": page,
                "page_size": per_page,
                "total": total_subscriptions,
                "total_pages": total_pages,
                "total_amount": total_amount,
            }

            return result

    async def read_all_subscriptions(
        self, page=1, page_size=10
    ) -> Tuple[List[Subscription], int]:
        async with self.session_factory() as session:
            offset = (page - 1) * page_size

            query = session.query(self.model)
            total_subscription = await session.scalar(query.count())

            query = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )

            result = await session.execute(
                query.options(
                    joinedload(Subscription.user)
                    .joinedload(User.business_profile)
                    .joinedload(BusinessProfile.users)
                ).options(
                    joinedload(Subscription.package).joinedload(
                        Package.package_item_assignments
                    )
                )
            )
            subscriptions = result.unique().scalars().all()

            return subscriptions, total_subscription

    async def subscriptions_today(self):
        async with self.session_factory() as session:
            today = date.today()
            result = await session.execute(
                session.query(PlanUpgrade).filter(PlanUpgrade.start_date == today)
            )
            plan_upgrades_today = result.scalars().all()

            for plan_upgrade in plan_upgrades_today:
                if plan_upgrade.package.package_price == plan_upgrade.payment.amount:
                    result = await session.execute(
                        session.query(self.model).filter(
                            self.model.user_uuid == plan_upgrade.user_uuid
                        )
                    )
                    existing_subscription = result.scalar()

                    if existing_subscription:
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
                await session.commit()
