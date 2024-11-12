from contextlib import AbstractContextManager
from typing import Callable, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from sqlalchemy import or_, func, Float
from sqlalchemy.orm import Session, joinedload

from app.model.payment import Payment
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.util.enums import PaymentStatus
from app.util.utils import parse_date, calculate_percentage_change

class PaymentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Payment)

    def get_all_payments(
        self,
        search_parameter: str = None,
        start_date: str = None,
        end_date: str = None,
        page: int = 1,
        page_size: int = 10,
        status=None,
    ):
        with self.session_factory() as session:
            # Parse and convert to datetime objects
            if start_date and end_date:
                try:
                    # parse_date returns a string in "%Y-%m-%d" format
                    parsed_start_str = parse_date(start_date)
                    parsed_end_str = parse_date(end_date)
                    
                    # Convert the parsed strings back to datetime objects
                    current_start_date = datetime.strptime(parsed_start_str, "%Y-%m-%d")
                    current_end_date = datetime.strptime(parsed_end_str, "%Y-%m-%d")
                except ValueError as ve:
                    raise ValueError(f"Date parsing error: {ve}")
            else:
                if end_date:
                    try:
                        parsed_end_str = parse_date(end_date)
                        current_end_date = datetime.combine(
                            datetime.strptime(parsed_end_str, "%Y-%m-%d"), 
                            datetime.max.time()
                        )
                    except ValueError as ve:
                        raise ValueError(f"Date parsing error: {ve}")
                else:
                    current_end_date = datetime.utcnow()
                
                if start_date:
                    try:
                        parsed_start_str = parse_date(start_date)
                        current_start_date = datetime.combine(
                            datetime.strptime(parsed_start_str, "%Y-%m-%d"), 
                            datetime.min.time()
                        )
                    except ValueError as ve:
                        raise ValueError(f"Date parsing error: {ve}")
                else:
                    current_start_date = current_end_date - relativedelta(months=12)

            # Determine previous period dates
            delta = current_end_date - current_start_date
            previous_start_date = current_start_date - delta
            previous_end_date = current_start_date - timedelta(days=1)

            # Apply filters for the current period
            query_current = session.query(self.model).options(joinedload(self.model.user))
            query_current = self.apply_filters(
                query_current, search_parameter, current_start_date, current_end_date, status
            )

            # Get pagination metadata
            total_records = query_current.count()
            total_pages = (total_records + page_size - 1) // page_size

            # Apply pagination
            paginated_query = query_current.limit(page_size).offset((page - 1) * page_size)
            payments = paginated_query.all()

            # Calculate current period totals
            sum_current = session.query(func.sum(self.model.amount.cast(Float))).filter(
                self.model.created_at >= current_start_date,
                self.model.created_at <= current_end_date,
            )
            if search_parameter:
                sum_current = sum_current.filter(
                    or_(
                        self.model.user.has(User.first_name.ilike(f"%{search_parameter}%")),
                        self.model.user.has(User.last_name.ilike(f"%{search_parameter}%")),
                    )
                )
            if status:
                sum_current = sum_current.filter(self.model.status == PaymentStatus(status))
            sum_current = sum_current.scalar() or Decimal('0.00')

            count_success_current = session.query(func.count(self.model.uuid)).filter(
                self.model.status == PaymentStatus.SUCCESS,
                self.model.created_at >= current_start_date,
                self.model.created_at <= current_end_date,
            )
            if search_parameter:
                count_success_current = count_success_current.filter(
                    or_(
                        self.model.user.has(User.first_name.ilike(f"%{search_parameter}%")),
                        self.model.user.has(User.last_name.ilike(f"%{search_parameter}%")),
                    )
                )
            count_success_current = count_success_current.scalar()

            count_failed_current = session.query(func.count(self.model.uuid)).filter(
                self.model.status == PaymentStatus.FAILED,
                self.model.created_at >= current_start_date,
                self.model.created_at <= current_end_date,
            )
            if search_parameter:
                count_failed_current = count_failed_current.filter(
                    or_(
                        self.model.user.has(User.first_name.ilike(f"%{search_parameter}%")),
                        self.model.user.has(User.last_name.ilike(f"%{search_parameter}%")),
                    )
                )
            count_failed_current = count_failed_current.scalar()

            # Calculate previous period totals
            sum_previous = session.query(func.sum(self.model.amount.cast(Float))).filter(
                self.model.created_at >= previous_start_date,
                self.model.created_at <= previous_end_date,
            )
            if search_parameter:
                sum_previous = sum_previous.filter(
                    or_(
                        self.model.user.has(User.first_name.ilike(f"%{search_parameter}%")),
                        self.model.user.has(User.last_name.ilike(f"%{search_parameter}%")),
                    )
                )
            if status:
                sum_previous = sum_previous.filter(self.model.status == PaymentStatus(status))
            sum_previous = sum_previous.scalar() or Decimal('0.00')

            count_success_previous = session.query(func.count(self.model.uuid)).filter(
                self.model.status == PaymentStatus.SUCCESS,
                self.model.created_at >= previous_start_date,
                self.model.created_at <= previous_end_date,
            )
            if search_parameter:
                count_success_previous = count_success_previous.filter(
                    or_(
                        self.model.user.has(User.first_name.ilike(f"%{search_parameter}%")),
                        self.model.user.has(User.last_name.ilike(f"%{search_parameter}%")),
                    )
                )
            count_success_previous = count_success_previous.scalar()

            count_failed_previous = session.query(func.count(self.model.uuid)).filter(
                self.model.status == PaymentStatus.FAILED,
                self.model.created_at >= previous_start_date,
                self.model.created_at <= previous_end_date,
            )
            if search_parameter:
                count_failed_previous = count_failed_previous.filter(
                    or_(
                        self.model.user.has(User.first_name.ilike(f"%{search_parameter}%")),
                        self.model.user.has(User.last_name.ilike(f"%{search_parameter}%")),
                    )
                )
            count_failed_previous = count_failed_previous.scalar()

            # Compute percentage changes
            sum_percentage_change = calculate_percentage_change(sum_current, sum_previous)
            print('current',sum_current,'prev',sum_previous)
            success_percentage_change = calculate_percentage_change(count_success_current, count_success_previous)
            failed_percentage_change = calculate_percentage_change(count_failed_current, count_failed_previous)

            return {
                "payments": payments,
                "current_page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
                "successful_payments": count_success_current,
                "failed_payments": count_failed_current,
                "total_payment_amount": sum_current,
                "total_payment_amount_percentage_change": sum_percentage_change,
                "successful_payments_percentage_change": success_percentage_change,
                "failed_payments_percentage_change": failed_percentage_change,
            }

    def apply_filters(
        self,
        query,
        search_parameter,
        start_date_obj: Optional[datetime] = None,
        end_date_obj: Optional[datetime] = None,
        status: Optional[PaymentStatus] = None,
    ):
        # Filter by search parameter (user's first or last name)
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

        if status:
            query = query.filter(self.model.status == PaymentStatus(status))

        return query
