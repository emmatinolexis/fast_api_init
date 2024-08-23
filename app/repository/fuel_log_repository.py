from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from sqlalchemy import Date, and_, cast, or_
from sqlalchemy.orm import Session, joinedload

from app.core.settings import get_settings, settings
from app.model.asset import Asset
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

            query = query.order_by(FuelLog.created_at.desc())
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

            query = query.order_by(FuelLog.created_at.desc())
            return query.all()

    def get_fuel_log_by_asset(
        self,
        asset_uuid: str,
        start_date: str,
        end_date: str,
    ):
        with self.session_factory() as session:
            date_from_obj = datetime.strptime(
                start_date, get_settings().DATE_FORMAT_YEAR
            ).date()
            date_to_obj = datetime.strptime(
                end_date, get_settings().DATE_FORMAT_YEAR
            ).date()

            # Build the base query
            base_query = session.query(self.model).options(
                joinedload(self.model.asset).joinedload(Asset.equipment)
            )

            # Define the filters
            filters = [
                self.model.asset_uuid == asset_uuid,
                and_(
                    cast(self.model.purchase_date, Date) >= date_from_obj,
                    cast(self.model.purchase_date, Date) <= date_to_obj,
                ),
            ]

            # Apply the filters and execute the query
            violations = base_query.filter(and_(*filters)).all()

            return violations
