from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.driver import Driver
from app.repository.base_repository import BaseRepository


class DriverRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Driver)

    def get_driver_by_user_uuid(self, user_uuid):
        with self.session_factory() as session:
            query = session.query(self.model)
            query = query.filter(self.model.user_uuid == user_uuid).all()
            return query

    def get_driver_by_business_uuid(self, business_uuid):
        with self.session_factory() as session:
            query = session.query(self.model)
            query = query.filter(self.model.business_uuid == business_uuid).all()
            return query
