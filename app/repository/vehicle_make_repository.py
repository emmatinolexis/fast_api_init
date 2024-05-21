from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.vehicle_models import VehicleMake
from app.repository.base_repository import BaseRepository


class VehicleMakeRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, VehicleMake)

    def get_vehicle_makes(self):
        with self.session_factory() as session:
            make = (
                session.query(self.model).options(joinedload(self.model.models)).all()
            )

            return make

    def get_vehicle_make_name(self, name: str):
        with self.session_factory() as session:
            make = session.query(self.model).filter_by(name=name).first()
            return make
