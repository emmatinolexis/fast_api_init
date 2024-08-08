from contextlib import AbstractContextManager
from typing import Callable, Optional

from sqlalchemy.orm import Session

from app.model.gas_cylinders import CylinderTypes
from app.repository.base_repository import BaseRepository


class GasCylinderTypeRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, CylinderTypes)

    def filter_by_status(self, status: Optional[str] = None):
        with self.session_factory() as session:
            query = session.query(CylinderTypes)
            if status:
                query = query.filter(CylinderTypes.status == status)
            return query.all()
