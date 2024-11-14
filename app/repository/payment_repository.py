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
            current_start_date, current_end_date = self.determine_current_period(start_date, end_date)
            
            previous_start_date, previous_end_date = self.determine_previous_period(current_start_date, current_end_date)

            query_current = session.query(self.model).options(joinedload(self.model.user))
            query_current = self.apply_filters(
                query_current, search_parameter, current_start_date, current_end_date, status
            )

            total_records = query_current.count()
            total_pages = (total_records + page_size - 1) // page_size

            paginated_query = query_current.limit(page_size).offset((page - 1) * page_size)
            payments = paginated_query.all()

            metrics_current = self.calculate_metrics(
                session, search_parameter, status, current_start_date, current_end_date
            )
            metrics_previous = self.calculate_metrics(
                session, search_parameter, status, previous_start_date, previous_end_date
            )

            sum_percentage_change = calculate_percentage_change(metrics_current['sum'], metrics_previous['sum'])
            success_percentage_change = calculate_percentage_change(
                metrics_current['count_success'], metrics_previous['count_success']
            )
            failed_percentage_change = calculate_percentage_change(
                metrics_current['count_failed'], metrics_previous['count_failed']
            )

            return {
                "payments": payments,
                "current_page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
                "successful_payments": metrics_current['count_success'],
                "failed_payments": metrics_current['count_failed'],
                "total_payment_amount": metrics_current['sum'],
                "total_payment_amount_percentage_change": sum_percentage_change,
                "successful_payments_percentage_change": success_percentage_change,
                "failed_payments_percentage_change": failed_percentage_change,
            }

    def determine_current_period(self, start_date: Optional[str], end_date: Optional[str]):
        try:
            if start_date and end_date:
                parsed_start = parse_date(start_date)
                parsed_end = parse_date(end_date)
                current_start_date = datetime.strptime(parsed_start, "%Y-%m-%d")
                current_end_date = datetime.strptime(parsed_end, "%Y-%m-%d")
            else:
                if end_date:
                    parsed_end = parse_date(end_date)
                    current_end_date = datetime.combine(
                        datetime.strptime(parsed_end, "%Y-%m-%d"),
                        datetime.max.time()
                    )
                else:
                    current_end_date = datetime.utcnow()
                
                if start_date:
                    parsed_start = parse_date(start_date)
                    current_start_date = datetime.combine(
                        datetime.strptime(parsed_start, "%Y-%m-%d"),
                        datetime.min.time()
                    )
                else:
                    current_start_date = current_end_date - relativedelta(months=6)

            return current_start_date, current_end_date

        except ValueError as ve:
            raise ValueError(f"Date parsing error: {ve}")

    def determine_previous_period(self, current_start: datetime, current_end: datetime):
        """Determine the previous period based on the current period's duration."""
        delta = current_end - current_start
        previous_start_date = current_start - delta
        previous_end_date = current_start - timedelta(days=1)
        return previous_start_date, previous_end_date

    def calculate_metrics(
        self, 
        session: Session, 
        search_parameter: Optional[str], 
        status: Optional[str],
        start_date: datetime, 
        end_date: datetime
    ) :
        sum_query = session.query(func.sum(self.model.amount.cast(Float))).filter(
            self.model.created_at >= start_date,
            self.model.created_at <= end_date,
        )
        if search_parameter:
            sum_query = sum_query.filter(
                or_(
                    self.model.user.has(User.first_name.ilike(f"%{search_parameter}%")),
                    self.model.user.has(User.last_name.ilike(f"%{search_parameter}%")),
                )
            )
        if status:
            sum_query = sum_query.filter(self.model.status == PaymentStatus(status))
        total_sum = Decimal(sum_query.scalar() or '0.00')

        count_success = session.query(func.count(self.model.uuid)).filter(
            self.model.status == PaymentStatus.SUCCESS,
            self.model.created_at >= start_date,
            self.model.created_at <= end_date,
        )
        if search_parameter:
            count_success = count_success.filter(
                or_(
                    self.model.user.has(User.first_name.ilike(f"%{search_parameter}%")),
                    self.model.user.has(User.last_name.ilike(f"%{search_parameter}%")),
                )
            )
        count_success = count_success.scalar()

        count_failed = session.query(func.count(self.model.uuid)).filter(
            self.model.status == PaymentStatus.FAILED,
            self.model.created_at >= start_date,
            self.model.created_at <= end_date,
        )
        if search_parameter:
            count_failed = count_failed.filter(
                or_(
                    self.model.user.has(User.first_name.ilike(f"%{search_parameter}%")),
                    self.model.user.has(User.last_name.ilike(f"%{search_parameter}%")),
                )
            )
        count_failed = count_failed.scalar()

        return {
            "sum": total_sum,
            "count_success": count_success,
            "count_failed": count_failed,
        }

    def apply_filters(
        self,
        query,
        search_parameter,
        start_date_obj: Optional[datetime] = None,
        end_date_obj: Optional[datetime] = None,
        status: Optional[PaymentStatus] = None,
    ):
        if search_parameter:
            query = query.filter(
                or_(
                    self.model.user.has(User.first_name.ilike(f"%{search_parameter}%")),
                    self.model.user.has(User.last_name.ilike(f"%{search_parameter}%")),
                )
            )

        if start_date_obj:
            query = query.filter(self.model.created_at >= start_date_obj)

        if end_date_obj:
            query = query.filter(self.model.created_at <= end_date_obj)

        if status:
            query = query.filter(self.model.status == PaymentStatus(status))

        return query
