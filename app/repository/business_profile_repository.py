from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.model.business_profile import BusinessProfile
from app.model.user_subscription import UserSubscription
from app.repository.base_repository import BaseRepository
from app.util.enums import SubscriptionStatus
from app.util.utils import parse_date


class BusinessProfileRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, BusinessProfile)

    def get_by_uuid(self, uuid: str) -> BusinessProfile:
        with self.session_factory() as session:
            return session.query(self.model).filter(self.model.uuid == uuid).first()

    def get_businesses(
        self,
        search_parameter: str = None,
        start_date: str = None,
        end_date: str = None,
        page: int = None,
        page_size: int = None,
    ):
        try:
            with self.session_factory() as session:
                # Initialize date variables
                start_date_obj = None
                end_date_obj = None

                if start_date and end_date:
                    start_date_obj = parse_date(start_date)
                    end_date_obj = parse_date(end_date)

                # Build the query
                query = (
                    session.query(self.model)
                    .options(joinedload(self.model.payments))
                    .options(joinedload(self.model.subscriptions))
                )

                # Apply filters (search parameter and date range)
                query = self.apply_filters(
                    query, search_parameter, start_date_obj, end_date_obj
                )

                total_records = (
                    query.count()
                )  # Get total number of records for pagination metadata

                total_pages = (total_records + page_size - 1) // page_size

                query = query.limit(page_size).offset((page - 1) * page_size)

                # Execute the query and return results
                businesses = query.all()

                # Query total subscriptions with date filters
                total_subscriptions_query = session.query(UserSubscription)

                # Active subscriptions (status = ACTIVE) with date filters
                total_active_subscriptions_query = session.query(
                    UserSubscription
                ).filter(UserSubscription.status == SubscriptionStatus.ACTIVE)

                # Inactive subscriptions (status = NON_RENEWING) with date filters
                total_inactive_subscriptions_query = session.query(
                    UserSubscription
                ).filter(UserSubscription.status == SubscriptionStatus.NON_RENEWING)

                if start_date_obj and end_date_obj:
                    total_subscriptions_query = total_subscriptions_query.filter(
                        and_(
                            UserSubscription.created_at >= start_date_obj,
                            UserSubscription.created_at <= end_date_obj,
                        )
                    )
                    total_inactive_subscriptions_query = (
                        total_inactive_subscriptions_query.filter(
                            and_(
                                UserSubscription.created_at >= start_date_obj,
                                UserSubscription.created_at <= end_date_obj,
                            )
                        )
                    )
                    total_active_subscriptions_query = (
                        total_active_subscriptions_query.filter(
                            and_(
                                UserSubscription.created_at >= start_date_obj,
                                UserSubscription.created_at <= end_date_obj,
                            )
                        )
                    )

                total_subscriptions = total_subscriptions_query.count()
                total_active_subscriptions = total_active_subscriptions_query.count()
                total_inactive_subscriptions = (
                    total_inactive_subscriptions_query.count()
                )

                return {
                    "businesses": businesses,
                    "current_page": page,
                    "page_size": page_size,
                    "total_records": total_records,
                    "total_pages": total_pages,
                    "total_subscriptions": total_subscriptions,
                    "total_active_subscriptions": total_active_subscriptions,
                    "total_inactive_subscriptions": total_inactive_subscriptions,
                }

        except Exception as e:
            raise e

    def apply_filters(
        self, query, search_parameter, start_date_obj=None, end_date_obj=None
    ):
        # Filter by search parameter (business name)
        if search_parameter:
            query = query.filter(
                self.model.business_name.ilike(f"%{search_parameter}%")
            )

        # Filter by start date (business creation date >= start date)
        if start_date_obj:
            query = query.filter(self.model.created_at >= start_date_obj)

        # Filter by end date (business creation date <= end date)
        if end_date_obj:
            query = query.filter(self.model.created_at <= end_date_obj)

        return query
