from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.asset import Asset
from app.repository.base_repository import BaseRepository


class AssetRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Asset)

    def read_all_assets_by_uuid(self, uuid: str, asset_type_uuid=None) -> Asset:
        with self.session_factory() as session:
            query = session.query(self.model).filter(self.model.user_uuid == uuid)
            if asset_type_uuid:
                query = query.filter(self.model.asset_type_uuid == asset_type_uuid)
            assets = (
                query.options(joinedload(Asset.marker_icon))
                .options(joinedload(Asset.asset_type))
                .all()
            )
            return assets
