from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.vehicle_models import VehicleModel
from app.repository.base_repository import BaseRepository


class VehicleModelRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, VehicleModel)

    def get_vehicle_model_name(self, name: str):
        with self.session_factory() as session:
            model = session.query(self.model).filter_by(name=name).first()
            return model
