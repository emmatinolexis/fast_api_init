from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.model.asset import Asset
from app.repository.base_repository import BaseRepository


class AssetRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Asset)

    def read_all_assets_by_uuid(self, uuid: str) -> Asset:
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.user_uuid == uuid)
                .options(joinedload(Asset.marker_icon))
                .options(joinedload(Asset.asset_type))
                .all()
            )

    def read_all_assets(self) -> Asset:
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .options(joinedload(Asset.marker_icon))
                .options(joinedload(Asset.asset_type))
                .all()
            )
