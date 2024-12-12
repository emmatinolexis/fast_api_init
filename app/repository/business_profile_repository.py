from contextlib import AbstractContextManager
from typing import Callable, Optional, Dict
from datetime import datetime, timedelta

from sqlalchemy import and_, func, case
from sqlalchemy.orm import Session, joinedload

from app.model.business_profile import BusinessProfile
from app.model.user_subscription import UserSubscription
from app.repository.base_repository import BaseRepository
from app.util.enums import ActiveStatus, SubscriptionStatus
from app.model.user import User
from app.util.utils import parse_date

class BusinessProfileRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, BusinessProfile)

    def get_businesses(
        self,
        search_parameter: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        status: Optional[ActiveStatus] = None,
    ):
        with self.session_factory() as session:
            try:
                start_date_obj = parse_date(start_date) if start_date else None
                end_date_obj = parse_date(end_date) if end_date else None
            except ValueError as e:
                print(f"Date parsing error: {e}")
                raise

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

            total_records = current_query.count()
            total_pages = (total_records + page_size - 1) // page_size

            businesses = current_query.limit(page_size).offset((page - 1) * page_size).all()

            if not businesses:
                print("No businesses found for the given criteria.")
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
                current_filters.append(self.model.business_name.ilike(f"%{search_parameter}%"))
            if start_date_obj:
                current_filters.append(self.model.created_at >= start_date_obj)
            if end_date_obj:
                current_filters.append(self.model.created_at <= end_date_obj)
            if status:
                current_filters.append(User.status == status)

            current_counts = session.query(
                func.count(UserSubscription.id).label('total'),
                func.sum(
                    case(
                        (UserSubscription.status == SubscriptionStatus.ACTIVE, 1),
                        else_=0
                    )
                ).label('active'),
                func.sum(
                    case(
                        (UserSubscription.status != SubscriptionStatus.ACTIVE, 1),
                        else_=0
                    )
                ).label('inactive'),
            ).join(BusinessProfile, UserSubscription.business_profile_uuid == BusinessProfile.uuid
            ).join(User, UserSubscription.user_email == User.email_address
            ).filter(and_(*current_filters)).one()

            total_subscriptions = current_counts.total
            total_active_subscriptions = current_counts.active or 0
            total_inactive_subscriptions = current_counts.inactive or 0

            if previous_start_date_obj and previous_end_date_obj:
                previous_filters = []
                if search_parameter:
                    previous_filters.append(self.model.business_name.ilike(f"%{search_parameter}%"))
                if previous_start_date_obj:
                    previous_filters.append(self.model.created_at >= previous_start_date_obj)
                if previous_end_date_obj:
                    previous_filters.append(self.model.created_at <= previous_end_date_obj)
                if status:
                    previous_filters.append(User.status == status)

                previous_counts = session.query(
                    func.count(UserSubscription.id).label('total'),
                    func.sum(
                        case(
                            (UserSubscription.status == SubscriptionStatus.ACTIVE, 1),
                            else_=0
                        )
                    ).label('active'),
                    func.sum(
                        case(
                            (UserSubscription.status != SubscriptionStatus.ACTIVE, 1),
                            else_=0
                        )
                    ).label('inactive'),
                ).join(BusinessProfile, UserSubscription.business_profile_uuid == BusinessProfile.uuid
                ).join(User, UserSubscription.user_email == User.email_address
                ).filter(and_(*previous_filters)).one()

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
            query = query.join(self.model.users).filter(
                User.status == status
            )

        return query

