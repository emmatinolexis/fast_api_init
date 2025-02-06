from contextlib import AbstractAsyncContextManager
from datetime import datetime
from typing import Callable

from sqlalchemy import Date, and_, cast, or_
from sqlalchemy.ext import AsynSession, joinedload

from app.core.settings import get_settings, settings
from app.model.asset import Asset
from app.model.driver import Driver
from app.model.fuel_log import FuelLog
from app.repository.base_repository import BaseRepository


class FuelLogRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsynSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, FuelLog)

    def _apply_common_filters(
        self, query, search, start_date, end_date, is_driver_joined=False
    ):
        # Apply search filter
        if search:
            search_pattern = f"%{search}%"

            if not is_driver_joined:
                query = query.outerjoin(Driver, FuelLog.driver_uuid == Driver.uuid)

            try:
                search_numeric = float(search)
                query = query.filter(
                    or_(
                        FuelLog.amount == search_numeric,
                        FuelLog.quantity == search_numeric,
                        Driver.first_name.ilike(search_pattern),
                        Driver.last_name.ilike(search_pattern),
                    )
                )
            except ValueError:
                query = query.filter(
                    or_(
                        Driver.first_name.ilike(search_pattern),
                        Driver.last_name.ilike(search_pattern),
                    )
                )

        # Apply date filters
        if start_date:
            start_date_str = datetime.strptime(
                start_date, settings.DATE_FORMAT
            ).strftime(settings.DATE_FORMAT)
            query = query.filter(FuelLog.purchase_date >= start_date_str)

        if end_date:
            end_date_str = datetime.strptime(end_date, settings.DATE_FORMAT).strftime(
                settings.DATE_FORMAT
            )
            query = query.filter(FuelLog.purchase_date <= end_date_str)

        return query

    async def get_fuel_logs_by_user_uuid(
        self,
        user_uuid: str,
        search: str = None,
        start_date: str = None,
        end_date: str = None,
    ):
        async with self.session_factory() as session:
            query = select(self.FuelLog).filter(FuelLog.user_uuid == user_uuid)
            query = self._apply_common_filters(query, search, start_date, end_date)
            query = query.order_by(FuelLog.created_at.desc())

            result = await session.execute(query)
            return result.scalars().all()

    async def get_fuel_logs_by_business_uuid(
        self,
        business_uuid: str,
        search: str = None,
        start_date: str = None,
        end_date: str = None,
    ):
        async with self.session_factory() as session:
            query = (
                select(self.FuelLog)
                .outerjoin(Driver, FuelLog.driver_uuid == Driver.uuid)
                .filter(FuelLog.business_profile_uuid == business_uuid)
            )
            query = self._apply_common_filters(
                query, search, start_date, end_date, is_driver_joined=True
            )
            query = query.order_by(FuelLog.created_at.desc())

            result = await session.execute(query)
            return result.scalars().all()

    async def get_fuel_log_by_asset(
        self,
        asset_uuid: str,
        start_date: str,
        end_date: str,
    ):
        async with self.session_factory() as session:
            # Convert date strings to date objects
            date_from_obj = datetime.strptime(
                start_date, get_settings().DATE_FORMAT_YEAR
            ).date()
            date_to_obj = datetime.strptime(
                end_date, get_settings().DATE_FORMAT_YEAR
            ).date()

            # Build query with filters
            stmt = (
                select(self.model)
                .options(joinedload(self.model.asset).joinedload(Asset.equipment))
                .filter(
                    self.model.asset_uuid == asset_uuid,
                    and_(
                        cast(self.model.purchase_date, Date) >= date_from_obj,
                        cast(self.model.purchase_date, Date) <= date_to_obj,
                    ),
                )
            )
            # Execute query
            result = await session.execute(stmt)
            return result.scalars().all()
