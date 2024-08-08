from contextlib import AbstractContextManager
from typing import Any, Callable, Dict

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.model.driver import Driver
from app.repository.base_repository import BaseRepository


class DriverRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Driver)

    def get_drivers_by_user_uuid(
        self, user_uuid: str, page: int = 1, page_size: int = 10
    ) -> Dict[str, Any]:
        with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Query to get the total count of drivers
            total_drivers = (
                session.query(func.count(self.model.id))
                .filter(self.model.user_uuid == user_uuid)
                .scalar()
            )

            # Calculate total pages
            total_pages = (total_drivers + page_size - 1) // page_size

            # Query to get the paginated drivers
            drivers = (
                session.query(self.model)
                .filter(self.model.user_uuid == user_uuid)
                .order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .all()
            )

            return {
                "drivers": drivers,
                "total_drivers": total_drivers,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    def update_driver_asset(self, asset_uuid, driver_uuid):
        with self.session_factory() as session:
            query = session.query(self.model)
            driver = query.filter(self.model.uuid == driver_uuid).first()

            driver.asset_uuid = asset_uuid
            session.commit()
            session.refresh(driver)

            return driver

    def get_drivers_by_business_uuid(self, business_uuid, page=1, page_size=10):
        with self.session_factory() as session:
            offset = (page - 1) * page_size

            # Query to get the total count of drivers
            total_drivers = (
                session.query(func.count(self.model.id))
                .filter(self.model.business_uuid == business_uuid)
                .scalar()
            )

            # Calculate total pages
            total_pages = (total_drivers + page_size - 1) // page_size

            # Fetch paginated results
            drivers = (
                session.query(self.model)
                .filter(self.model.business_uuid == business_uuid)
                .order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
                .all()
            )

            return {
                "drivers": drivers,
                "total_drivers": total_drivers,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    def get_driver_phone_number(self, phone_number: str):
        with self.session_factory() as session:
            query = session.query(self.model)
            driver = query.filter(self.model.phone_number == phone_number).first()
            return driver

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

    def get_driver_by_email(self, email: str) -> Driver:
        with self.session_factory() as session:
            query = session.query(self.model)
            driver = query.filter(self.model.email == email).first()
            return driver
