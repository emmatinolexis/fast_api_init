from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.equipment import Equipment
from app.repository.base_repository import BaseRepository
from app.util.enums import ActiveStatus


class EquipmentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Equipment)

    def get_equipments_by_asset_uuid(self, asset_uuid: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter_by(asset_uuid=asset_uuid)
                .options(joinedload(self.model.asset_type))
                .all()
            )

    def get_equipment_by_asset_uuid(self, asset_uuid: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter_by(asset_uuid=asset_uuid)
                .options(joinedload(self.model.asset_type))
                .first()
            )

    def get_equipments(
        self, page: int = 1, page_size: int = 10, search_query: str = None, status=None
    ):
        with self.session_factory() as session:
            query = session.query(self.model).options(joinedload(self.model.asset_type))

            if search_query:
                query = query.filter(self.model.name.ilike(f"%{search_query}%"))

            if status:
                query = query.filter(self.model.status == ActiveStatus(status))

            total_records = query.count()
            offset = (page - 1) * page_size
            equipments = query.offset(offset).limit(page_size).all()

            return {
                "data": equipments,
                "total_records": total_records,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_records + page_size - 1) // page_size,
            }
