from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.model.payment import Payment
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.util.enums import PaymentStatus
from app.util.utils import parse_date


class PaymentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Payment)

    def get_all_payments(
        self,
        search_parameter: str = None,
        start_date: str = None,
        end_date: str = None,
        page: int = None,
        page_size: int = None,
    ):
        with self.session_factory() as session:
            # Initialize date variables
            start_date_obj = None
            end_date_obj = None

            if start_date and end_date:
                start_date_obj = parse_date(start_date)
                end_date_obj = parse_date(end_date)

            # Build the query with joinedload
            query = session.query(self.model).options(joinedload(self.model.user))

            # Apply filters (search parameter and date range)
            query = self.apply_filters(
                query, search_parameter, start_date_obj, end_date_obj
            )

            # Get total number of records for pagination metadata before applying limit and offset
            total_records = query.count()
            total_pages = (total_records + page_size - 1) // page_size

            # Apply pagination
            paginated_query = query.limit(page_size).offset((page - 1) * page_size)

            # Execute paginated query
            payments = paginated_query.all()

            # Count successful and failed payments within the filtered query
            successful_payments = query.filter(
                self.model.status == PaymentStatus.SUCCESS
            ).count()
            failed_payments = query.filter(
                self.model.status == PaymentStatus.FAILED
            ).count()

            return {
                "payments": payments,
                "current_page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
                "successful_payments": successful_payments,
                "failed_payments": failed_payments,
            }

    def apply_filters(
        self, query, search_parameter, start_date_obj=None, end_date_obj=None
    ):
        # Filter by search parameter (user's first name)
        if search_parameter:
            query = query.filter(
                or_(
                    self.model.user.has(User.first_name.ilike(f"%{search_parameter}%")),
                    self.model.user.has(User.last_name.ilike(f"%{search_parameter}%")),
                )
            )

        # Filter by start date (created_at >= start_date)
        if start_date_obj:
            query = query.filter(self.model.created_at >= start_date_obj)

        # Filter by end date (created_at <= end_date)
        if end_date_obj:
            query = query.filter(self.model.created_at <= end_date_obj)

        return query
