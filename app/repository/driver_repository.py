from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.driver import Driver
from app.repository.base_repository import BaseRepository


class DriverRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Driver)

    def get_drivers_by_user_uuid(self, user_uuid):
        with self.session_factory() as session:
            query = session.query(self.model)
            query = query.filter(self.model.user_uuid == user_uuid).all()
            return query

    def update_driver_asset(self, asset_uuid, driver_uuid):
        with self.session_factory() as session:
            query = session.query(self.model)
            driver = query.filter(self.model.uuid == driver_uuid).first()

            driver.asset_uuid = asset_uuid
            session.commit()
            session.refresh(driver)

            return driver

    def get_drivers_by_business_uuid(self, business_uuid):
        with self.session_factory() as session:
            query = session.query(self.model)
            query = query.filter(self.model.business_uuid == business_uuid).all()
            return query

    def unassign_driver(self, driver_uuid) -> Driver:
        with self.session_factory() as session:
            query = session.query(self.model)
            driver = query.filter(self.model.uuid == driver_uuid).first()
            if not driver:
                raise Exception("Driver not found")
            driver.asset_uuid = None
            session.commit()
            session.refresh(driver)
            return driver
