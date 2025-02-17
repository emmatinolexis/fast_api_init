from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable, Optional

from dateutil.relativedelta import relativedelta
from sqlalchemy import Float, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.model.payment import Payment
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.util.enums import PaymentStatus
from app.util.utils import calculate_percentage_change, parse_date


class PaymentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, Payment)

    async def get_all_payments(
        self,
        search_parameter: str = None,
        start_date: str = None,
        end_date: str = None,
        page: int = 1,
        page_size: int = 10,
        status=None,
    ):
        async with self.session_factory() as session:
            current_start_date, current_end_date = self.determine_current_period(
                start_date, end_date
            )

            previous_start_date, previous_end_date = self.determine_previous_period(
                current_start_date, current_end_date
            )

            query_current = select(self.model).options(joinedload(self.model.user))

            # Apply filters
            query_current = self.apply_filters(
                query_current,
                search_parameter,
                current_start_date,
                current_end_date,
                status,
            )

            total_records = await session.scalar(
                select(func.count()).select_from(query_current.subquery())
            )
            total_pages = (total_records + page_size - 1) // page_size

            paginated_query = query_current.limit(page_size).offset(
                (page - 1) * page_size
            )
            result = await session.execute(paginated_query)
            payments = result.scalars().all()

            metrics_current = await self.calculate_metrics(
                session, search_parameter, status, current_start_date, current_end_date
            )
            metrics_previous = await self.calculate_metrics(
                session,
                search_parameter,
                status,
                previous_start_date,
                previous_end_date,
            )

            sum_percentage_change = calculate_percentage_change(
                metrics_current["sum"], metrics_previous["sum"]
            )
            success_percentage_change = calculate_percentage_change(
                metrics_current["count_success"], metrics_previous["count_success"]
            )
            failed_percentage_change = calculate_percentage_change(
                metrics_current["count_failed"], metrics_previous["count_failed"]
            )

            return {
                "payments": payments,
                "current_page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
                "successful_payments": metrics_current["count_success"],
                "failed_payments": metrics_current["count_failed"],
                "total_payment_amount": metrics_current["sum"] / 100,
                "total_payment_amount_percentage_change": sum_percentage_change,
                "successful_payments_percentage_change": success_percentage_change,
                "failed_payments_percentage_change": failed_percentage_change,
            }

    def determine_current_period(
        self, start_date: Optional[str], end_date: Optional[str]
    ):
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
                        datetime.strptime(parsed_end, "%Y-%m-%d"), datetime.max.time()
                    )
                else:
                    current_end_date = datetime.utcnow()

                if start_date:
                    parsed_start = parse_date(start_date)
                    current_start_date = datetime.combine(
                        datetime.strptime(parsed_start, "%Y-%m-%d"), datetime.min.time()
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

    async def calculate_metrics(
        self,
        session: AsyncSession,
        search_parameter: Optional[str],
        status: Optional[str],
        start_date: datetime,
        end_date: datetime,
    ):
        filters = [
            self.model.created_at >= start_date,
            self.model.created_at <= end_date,
        ]

        if search_parameter:
            filters.append(
                or_(
                    self.model.user.has(User.first_name.ilike(f"%{search_parameter}%")),
                    self.model.user.has(User.last_name.ilike(f"%{search_parameter}%")),
                )
            )

        if status:
            filters.append(self.model.status == PaymentStatus(status))

        sum_query = select(func.sum(self.model.amount.cast(Float))).where(*filters)
        total_sum_result = await session.execute(sum_query)
        total_sum = Decimal(total_sum_result.scalar() or "0.00")

        count_success_query = select(func.count(self.model.uuid)).where(
            self.model.status == PaymentStatus.SUCCESS, *filters
        )
        count_success_result = await session.execute(count_success_query)
        count_success = count_success_result.scalar()

        count_failed_query = select(func.count(self.model.uuid)).where(
            self.model.status == PaymentStatus.FAILED, *filters
        )
        count_failed_result = await session.execute(count_failed_query)
        count_failed = count_failed_result.scalar()

        return {
            "sum": total_sum,
            "count_success": count_success or 0,
            "count_failed": count_failed or 0,
        }

    def apply_filters(
        self,
        query,
        search_parameter: Optional[str] = None,
        start_date_obj: Optional[datetime] = None,
        end_date_obj: Optional[datetime] = None,
        status: Optional[PaymentStatus] = None,
    ):
        filters = []

        if search_parameter:
            filters.append(
                or_(
                    self.model.user.has(User.first_name.ilike(f"%{search_parameter}%")),
                    self.model.user.has(User.last_name.ilike(f"%{search_parameter}%")),
                )
            )

        if start_date_obj:
            filters.append(self.model.created_at >= start_date_obj)

        if end_date_obj:
            filters.append(self.model.created_at <= end_date_obj)

        if status:
            filters.append(self.model.status == PaymentStatus(status))

        # ✅ Apply filters using `.where()` instead of `.filter()`
        return query.where(*filters)

    # def apply_filters(
    #     self,
    #     query,
    #     search_parameter,
    #     start_date_obj: Optional[datetime] = None,
    #     end_date_obj: Optional[datetime] = None,
    #     status: Optional[PaymentStatus] = None,
    # ):
    #     if search_parameter:
    #         query = query.filter(
    #             or_(
    #                 self.model.user.has(User.first_name.ilike(f"%{search_parameter}%")),
    #                 self.model.user.has(User.last_name.ilike(f"%{search_parameter}%")),
    #             )
    #         )

    #     if start_date_obj:
    #         query = query.filter(self.model.created_at >= start_date_obj)

    #     if end_date_obj:
    #         query = query.filter(self.model.created_at <= end_date_obj)

    #     if status:
    #         query = query.filter(self.model.status == PaymentStatus(status))

    #     return query
