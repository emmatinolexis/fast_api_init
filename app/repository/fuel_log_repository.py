from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.model.fuel_log import FuelLog
from app.repository.base_repository import BaseRepository


class FuelLogRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, FuelLog)

    def _apply_common_filters(self, query, search, start_date, end_date):
        if search:
            search_pattern = f"%{search}%"
            try:
                search_numeric = float(search)
                query = query.filter(
                    or_(
                        FuelLog.amount == search_numeric,
                        FuelLog.driver_name.ilike(search_pattern),
                    )
                )
            except ValueError:
                query = query.filter(FuelLog.driver_name.ilike(search_pattern))

        if start_date:
            # Convert start_date to the same string format as the purchase_date in the database
            start_date_str = datetime.strptime(
                start_date, settings.PURCHASE_DATE_FORMAT
            ).strftime(settings.PURCHASE_DATE_FORMAT)
            query = query.filter(FuelLog.purchase_date >= start_date_str)

        if end_date:
            # Convert end_date to the same string format as the purchase_date in the database
            end_date_str = datetime.strptime(
                end_date, settings.PURCHASE_DATE_FORMAT
            ).strftime(settings.PURCHASE_DATE_FORMAT)
            query = query.filter(FuelLog.purchase_date <= end_date_str)

        return query

    def get_fuel_logs_by_user_uuid(
        self,
        user_uuid: str,
        search: str = None,
        start_date: str = None,
        end_date: str = None,
    ):
        with self.session_factory() as session:
            query = session.query(FuelLog).filter(FuelLog.user_uuid == user_uuid)
            query = self._apply_common_filters(query, search, start_date, end_date)
            return query.all()

    def get_fuel_logs_by_business_uuid(
        self,
        business_uuid: str,
        search: str = None,
        start_date: str = None,
        end_date: str = None,
    ):
        with self.session_factory() as session:
            query = session.query(FuelLog).filter(
                FuelLog.business_profile_uuid == business_uuid
            )
            query = self._apply_common_filters(query, search, start_date, end_date)
            return query.all()
