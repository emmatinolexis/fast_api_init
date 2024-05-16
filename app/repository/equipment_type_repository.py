from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.equipment_type import EquipmentType
from app.repository.base_repository import BaseRepository


class EquipmentTypeRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, EquipmentType)

    def get_equipment_types_by_equipment_uuid(self, uuid: str) -> EquipmentType:
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.equipment_uuid == uuid)
                .all()
            )

    def get_all_equipment_types(self):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .options(joinedload(self.model.equipment))
                .all()
            )
