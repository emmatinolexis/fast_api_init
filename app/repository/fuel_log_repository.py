from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.model.fuel_log import FuelLog
from app.repository.base_repository import BaseRepository


class FuelLogRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, FuelLog)

    def get_fuel_logs_by_user_uuid(self, user_uuid: str, search: str = None):
        with self.session_factory() as session:
            query = session.query(FuelLog).filter(FuelLog.user_uuid == user_uuid)

            if search:
                search_pattern = f"%{search}%"
                try:
                    search_numeric = float(search)
                    query = query.filter(
                        or_(
                            FuelLog.driver_name.ilike(search_pattern),
                            FuelLog.amount == search_numeric,
                        )
                    )
                except ValueError:
                    query = query.filter(FuelLog.driver_name.ilike(search_pattern))

            return query.all()

    def get_fuel_logs_by_business_uuid(self, business_uuid: str, search: str = None):
        with self.session_factory() as session:
            query = session.query(FuelLog).filter(
                FuelLog.business_profile_uuid == business_uuid
            )

            if search:
                search_pattern = f"%{search}%"
                try:
                    search_numeric = float(search)
                    query = query.filter(
                        or_(
                            FuelLog.driver_name.ilike(search_pattern),
                            FuelLog.amount == search_numeric,
                        )
                    )
                except ValueError:
                    query = query.filter(FuelLog.driver_name.ilike(search_pattern))

            return query.all()
