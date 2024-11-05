from contextlib import AbstractContextManager
from typing import Callable, Optional

from sqlalchemy import String, cast
from sqlalchemy.orm import Session

from app.model.gas_cylinders import CylinderTypes
from app.repository.base_repository import BaseRepository
from app.util.enums import ActiveStatus

class GasCylinderTypeRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, CylinderTypes)

    def filter_by_status_and_name(
        self,
        status: Optional[str] = None,
        search_query: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ):
        with self.session_factory() as session:
            query = session.query(CylinderTypes)

            if status:
                query = query.filter(CylinderTypes.status == ActiveStatus(status))

            if search_query:
                query = query.filter(
                    cast(CylinderTypes.name, String).ilike(f"%{search_query}%")
                )

            total_records = query.count()
            offset = (page - 1) * page_size
            cylinder_types = query.offset(offset).limit(page_size).all()

            return {
                "data": cylinder_types,
                "total_records": total_records,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_records + page_size - 1) // page_size,
            }
