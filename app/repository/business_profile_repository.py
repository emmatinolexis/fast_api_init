from contextlib import AbstractAsyncContextManager
from datetime import datetime, timedelta
from typing import Callable, Optional

from sqlalchemy import and_, case, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.logger import get_logger
from app.model.business_profile import BusinessProfile
from app.model.user import User
from app.model.user_subscription import UserSubscription
from app.repository.base_repository import BaseRepository
from app.util.enums import ActiveStatus, SubscriptionStatus
from app.util.utils import parse_date


class BusinessProfileRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, BusinessProfile)

    async def get_businesses(
        self,
        search_parameter: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        status: Optional[ActiveStatus] = None,
    ):
        async with self.session_factory() as session:
            try:
                start_date_obj = parse_date(start_date) if start_date else None
                end_date_obj = parse_date(end_date) if end_date else None
            except ValueError as e:
                raise e

            if start_date_obj and end_date_obj:
                delta = end_date_obj - start_date_obj
                previous_end_date_obj = start_date_obj - timedelta(days=1)
                previous_start_date_obj = previous_end_date_obj - delta
            else:
                previous_start_date_obj = None
                previous_end_date_obj = None

            current_query = (
                session.query(self.model)
                .options(joinedload(self.model.payments))
                .options(joinedload(self.model.subscriptions))
            )

            current_query = self.apply_filters(
                current_query, search_parameter, start_date_obj, end_date_obj, status
            )

            total_records = await session.scalar(
                current_query.statement.with_only_columns([func.count()])
            )
            total_pages = (total_records + page_size - 1) // page_size

            businesses = await session.execute(
                current_query.limit(page_size).offset((page - 1) * page_size)
            )
            businesses = businesses.scalars().all()

            if not businesses:
                get_logger().warn("No businesses found for the given criteria.")
                return {
                    "businesses": [],
                    "current_page": page,
                    "page_size": page_size,
                    "total_records": total_records,
                    "total_pages": total_pages,
                    "total_subscriptions": 0,
                    "total_active_subscriptions": 0,
                    "total_inactive_subscriptions": 0,
                    "previous_total_subscriptions": 0,
                    "previous_total_active_subscriptions": 0,
                    "previous_total_inactive_subscriptions": 0,
                }

            current_filters = []
            if search_parameter:
                current_filters.append(
                    self.model.business_name.ilike(f"%{search_parameter}%")
                )
            if start_date_obj:
                current_filters.append(self.model.created_at >= start_date_obj)
            if end_date_obj:
                current_filters.append(self.model.created_at <= end_date_obj)
            if status:
                current_filters.append(User.status == status)

            current_counts = await session.execute(
                session.query(
                    func.count(UserSubscription.id).label("total"),
                    func.sum(
                        case(
                            (UserSubscription.status == SubscriptionStatus.ACTIVE, 1),
                            else_=0,
                        )
                    ).label("active"),
                    func.sum(
                        case(
                            (UserSubscription.status != SubscriptionStatus.ACTIVE, 1),
                            else_=0,
                        )
                    ).label("inactive"),
                )
                .join(
                    BusinessProfile,
                    UserSubscription.business_profile_uuid == BusinessProfile.uuid,
                )
                .join(User, UserSubscription.user_email == User.email_address)
                .filter(and_(*current_filters))
            )
            current_counts = current_counts.one()

            total_subscriptions = current_counts.total
            total_active_subscriptions = current_counts.active or 0
            total_inactive_subscriptions = current_counts.inactive or 0

            if previous_start_date_obj and previous_end_date_obj:
                previous_filters = []
                if search_parameter:
                    previous_filters.append(
                        self.model.business_name.ilike(f"%{search_parameter}%")
                    )
                if previous_start_date_obj:
                    previous_filters.append(
                        self.model.created_at >= previous_start_date_obj
                    )
                if previous_end_date_obj:
                    previous_filters.append(
                        self.model.created_at <= previous_end_date_obj
                    )
                if status:
                    previous_filters.append(User.status == status)

                previous_counts = await session.execute(
                    session.query(
                        func.count(UserSubscription.id).label("total"),
                        func.sum(
                            case(
                                (
                                    UserSubscription.status
                                    == SubscriptionStatus.ACTIVE,
                                    1,
                                ),
                                else_=0,
                            )
                        ).label("active"),
                        func.sum(
                            case(
                                (
                                    UserSubscription.status
                                    != SubscriptionStatus.ACTIVE,
                                    1,
                                ),
                                else_=0,
                            )
                        ).label("inactive"),
                    )
                    .join(
                        BusinessProfile,
                        UserSubscription.business_profile_uuid == BusinessProfile.uuid,
                    )
                    .join(User, UserSubscription.user_email == User.email_address)
                    .filter(and_(*previous_filters))
                )
                previous_counts = previous_counts.one()

                previous_total_subscriptions = previous_counts.total
                previous_total_active_subscriptions = previous_counts.active or 0
                previous_total_inactive_subscriptions = previous_counts.inactive or 0
            else:
                previous_total_subscriptions = 0
                previous_total_active_subscriptions = 0
                previous_total_inactive_subscriptions = 0

            return {
                "businesses": businesses,
                "current_page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
                "total_subscriptions": total_subscriptions,
                "total_active_subscriptions": total_active_subscriptions,
                "total_inactive_subscriptions": total_inactive_subscriptions,
                "previous_total_subscriptions": previous_total_subscriptions,
                "previous_total_active_subscriptions": previous_total_active_subscriptions,
                "previous_total_inactive_subscriptions": previous_total_inactive_subscriptions,
            }

    def apply_filters(
        self,
        query,
        search_parameter: Optional[str],
        start_date_obj: Optional[datetime],
        end_date_obj: Optional[datetime],
        status: Optional[ActiveStatus],
    ):
        if search_parameter:
            query = query.filter(
                self.model.business_name.ilike(f"%{search_parameter}%")
            )

        if start_date_obj:
            query = query.filter(self.model.created_at >= start_date_obj)

        if end_date_obj:
            query = query.filter(self.model.created_at <= end_date_obj)

        if status:
            query = query.join(self.model.users).filter(User.status == status)

        return query
