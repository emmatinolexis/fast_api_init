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

def parse_date(date_str: str) -> datetime:
    """
    Parses a date string into a datetime object.

    Supported formats:
    - YYYY-MM-DD
    - YYYY-MM-DD HH:MM:SS
    - DD/MM/YYYY
    - MM/DD/YYYY
    - DD-MM-YYYY
    - DD-MM-YYYY HH:MM:SS

    Args:
        date_str (str): The date string to parse.

    Returns:
        datetime: The parsed datetime object.

    Raises:
        ValueError: If the date format is not recognized.
    """
    # List of potential date formats including date and time
    date_formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%d-%m-%Y %H:%M:%S",
    ]

    for fmt in date_formats:
        try:
            # Try to parse the date with the current format
            return datetime.strptime(date_str, fmt)
        except ValueError:
            # Continue to the next format if this one fails
            continue

    # Raise an exception if none of the formats matched
    raise ValueError(f"Date format for '{date_str}' not recognized. Expected formats: YYYY-MM-DD, DD/MM/YYYY, etc.")


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
    ) -> Dict:
        with self.session_factory() as session:
            # Parse dates
            try:
                start_date_obj = parse_date(start_date) if start_date else None
                end_date_obj = parse_date(end_date) if end_date else None
            except ValueError as e:
                # Print and re-raise the exception for debugging
                print(f"Date parsing error: {e}")
                raise

            # Calculate previous period
            if start_date_obj and end_date_obj:
                delta = end_date_obj - start_date_obj
                previous_end_date_obj = start_date_obj - timedelta(days=1)
                previous_start_date_obj = previous_end_date_obj - delta
            else:
                previous_start_date_obj = None
                previous_end_date_obj = None

            # Build current query
            current_query = (
                session.query(self.model)
                .options(joinedload(self.model.payments))
                .options(joinedload(self.model.subscriptions))
            )

            # Apply current filters
            current_query = self.apply_filters(
                current_query, search_parameter, start_date_obj, end_date_obj, status
            )

            # Pagination
            total_records = current_query.count()
            total_pages = (total_records + page_size - 1) // page_size

            businesses = current_query.limit(page_size).offset((page - 1) * page_size).all()

            if not businesses:
                # No businesses found; print and return zero counts
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

            # Define filters for current period based on BusinessProfile
            current_filters = []
            if search_parameter:
                current_filters.append(self.model.business_name.ilike(f"%{search_parameter}%"))
            if start_date_obj:
                current_filters.append(self.model.created_at >= start_date_obj)
            if end_date_obj:
                current_filters.append(self.model.created_at <= end_date_obj)
            if status:
                current_filters.append(User.status == status)

            # Aggregate current counts using conditional aggregation with join
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

            # Print current counts for debugging
            print("Current Period Counts:")
            print(f"Total Subscriptions: {total_subscriptions}")
            print(f"Active Subscriptions: {total_active_subscriptions}")
            print(f"Inactive Subscriptions: {total_inactive_subscriptions}")

            # Aggregate previous counts using conditional aggregation with join
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

                # Print previous counts for debugging
                print("\nPrevious Period Counts:")
                print(f"Total Subscriptions: {previous_total_subscriptions}")
                print(f"Active Subscriptions: {previous_total_active_subscriptions}")
                print(f"Inactive Subscriptions: {previous_total_inactive_subscriptions}")
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

        if status:
            query = query.join(self.model.users).filter(
                User.status == status
            )

        return query

