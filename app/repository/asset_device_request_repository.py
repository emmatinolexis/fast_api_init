from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.asset_device_request import AssetDeviceRequest
from app.repository.base_repository import BaseRepository
from app.schema.asset_schema import CreateAssetDeviceRequestPayload


class AssetDeviceRequestRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, AssetDeviceRequest)

    def get_asset_device_request_by_user_by_asset_type_uuid(
        self, user_uuid: str, asset_type_uuid: str
    ):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(
                    self.model.asset_type_uuid == asset_type_uuid
                    and self.model.user_uuid == user_uuid
                )
                .first()
            )

    def create_asset_device_request(
        self, asset_device_request: CreateAssetDeviceRequestPayload
    ):
        return super().create(asset_device_request)

    def get_asset_device_requests_by_user_uuid(self, user_uuid: str):
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.user_uuid == user_uuid)
                .all()
            )
