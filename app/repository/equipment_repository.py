from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.equipment import Equipment
from app.repository.base_repository import BaseRepository


class EquipmentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Equipment)

    def get_all_equipments(self):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .options(joinedload(self.model.asset_type))
                .all()
            )

    def get_equipments_by_asset_uuid(self, asset_uuid: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter_by(asset_uuid=asset_uuid)
                .options(joinedload(self.model.asset_type))
                .all()
            )
