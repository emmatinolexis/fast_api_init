from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.asset_operator_assignment import AssetOperatorAssignment
from app.repository.base_repository import BaseRepository


class AssetOperatorTypeAssignmentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, AssetOperatorAssignment)



    def get_assignment_by_operator_uuid(self, operator_uuid: str) -> AssetOperatorAssignment:
        with self.session_factory() as session:
            return session.query(AssetOperatorAssignment).filter_by(operator_uuid=operator_uuid).first()
        

    def get_assignment_by_asset_uuid(self, asset_uuid: str) -> AssetOperatorAssignment:
        with self.session_factory() as session:
            return session.query(AssetOperatorAssignment).filter_by(asset_uuid=asset_uuid).first()
