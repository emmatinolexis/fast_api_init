from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.asset_type import AssetType
from app.repository.base_repository import BaseRepository
from typing import Optional
from app.util.enums import ActiveStatus

class AssetTypeRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, AssetType)
    
    def get_asset_types(self, status: str = None):
        with self.session_factory() as session:
            query = session.query(self.model)

            if status:
                query = query.filter(self.model.status == ActiveStatus(status)) 

            asset_types = query.all()
            return asset_types

