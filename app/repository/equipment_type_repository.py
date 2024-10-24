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

   
    def get_equipment_types(self, page: int = 1, page_size: int = 10, search_query: str = None):
        with self.session_factory() as session:
            query = session.query(self.model).options(joinedload(self.model.equipment))

            if search_query:
                query = query.filter(self.model.equipment_type_name.ilike(f"%{search_query}%"))

            total_records = query.count()
            offset = (page - 1) * page_size
            equipment_types = query.offset(offset).limit(page_size).all()

            return {
                "data": equipment_types,
                "total_records": total_records,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_records + page_size - 1) // page_size,
            }
