from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.driver_license import DriverLicense
from app.repository.base_repository import BaseRepository


class DriverLicenseRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, DriverLicense)

    def get_license_by_license_number(self, license_number: str) -> DriverLicense:
        with self.session_factory() as session:
            return (
                session.query(DriverLicense)
                .filter(DriverLicense.license_number == license_number)
                .first()
            )

    def get_license_by_user_id(self, user_uuid: str) -> DriverLicense:
        with self.session_factory() as session:
            return (
                session.query(DriverLicense)
                .filter(DriverLicense.user_id == user_uuid)
                .first()
            )

    def get_all_licenses(self) -> list[DriverLicense]:
        with self.session_factory() as session:
            return session.query(DriverLicense).all()
