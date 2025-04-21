from datetime import datetime, timedelta
from typing import Callable, Optional

from sqlalchemy import and_, case, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.logger import get_logger
from app.model.business_profile import BusinessProfile
from app.model.user import User

from app.repository.base_repository import BaseRepository
from app.util.enums import ActiveStatus, SubscriptionStatus
from app.util.utils import parse_date


class BusinessProfileRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
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
        async with self.session_factory() as session:  # Async session context
            start_date_obj, end_date_obj = self._parse_dates(start_date, end_date)
            (
                previous_start_date_obj,
                previous_end_date_obj,
            ) = self._get_previous_date_range(start_date_obj, end_date_obj)

            # Query businesses with necessary relationships
            current_query = select(self.model).options(
                joinedload(self.model.payments),
                joinedload(self.model.subscriptions),
            )
            current_query = self.apply_filters(
                current_query,
                search_parameter,
                start_date_obj,
                end_date_obj,
                status,
            )

            total_records = await session.scalar(
                select(func.count()).select_from(current_query.subquery())
            )
            total_pages = (total_records + page_size - 1) // page_size

            businesses = await session.execute(
                current_query.limit(page_size).offset((page - 1) * page_size)
            )
            businesses = businesses.unique().scalars().all()

            if not businesses:
                get_logger().warn("No businesses found for the given criteria.")
                return self._default_response(
                    page, page_size, total_records, total_pages
                )

            # Get subscription statistics
            (
                total_subscriptions,
                total_active_subscriptions,
                total_inactive_subscriptions,
            ) = (0, 0, 0)

            if previous_start_date_obj and previous_end_date_obj:
                (
                    previous_total_subscriptions,
                    previous_total_active_subscriptions,
                    previous_total_inactive_subscriptions,
                ) = (0, 0, 0)
            else:
                (
                    previous_total_subscriptions,
                    previous_total_active_subscriptions,
                    previous_total_inactive_subscriptions,
                ) = (0, 0, 0)

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

    def _parse_dates(self, start_date, end_date):
        """Helper function to parse dates safely."""
        try:
            start_date_obj = parse_date(start_date) if start_date else None
            end_date_obj = parse_date(end_date) if end_date else None
        except ValueError as e:
            raise e
        return start_date_obj, end_date_obj

    def _get_previous_date_range(self, start_date_obj, end_date_obj):
        """Calculates previous date range."""
        if start_date_obj and end_date_obj:
            delta = end_date_obj - start_date_obj
            previous_end_date_obj = start_date_obj - timedelta(days=1)
            previous_start_date_obj = previous_end_date_obj - delta
            return previous_start_date_obj, previous_end_date_obj
        return None, None

    def _default_response(self, page, page_size, total_records, total_pages):
        """Default response structure when no businesses are found."""
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
