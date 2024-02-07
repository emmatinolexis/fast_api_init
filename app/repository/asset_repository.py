from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable, List, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.model.asset import Asset
from app.model.device import Device
from app.repository.base_repository import BaseRepository


class AssetRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Asset)

    def read_all_assets_by_uuid(
        self, uuid: str, asset_type_uuid: str = None, page=1, page_size=10
    ) -> Tuple[List[Asset], int]:
        with self.session_factory() as session:
            # Calculate the offset based on the page and per_page values
            offset = (page - 1) * page_size

            query = session.query(self.model).filter(self.model.user_uuid == uuid)
            total_assets = query.count()

            if asset_type_uuid is not None:
                query = query.filter(self.model.asset_type_uuid == asset_type_uuid)

            query = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )

            assets = (
                query.options(joinedload(Asset.marker_icon))
                .options(joinedload(Asset.asset_type))
                .all()
            )

            return assets, total_assets

    def assign_device_imei(self, asset_uuid, imei: str) -> Asset:
        with self.session_factory() as session:
            asset = (
                session.query(self.model).filter(self.model.uuid == asset_uuid).first()
            )

            # update asset with device imei
            if not asset:
                raise Exception("New password and confirm password does not match")

            asset.device_imei = imei
            session.commit()
            session.refresh(asset)

            device = (
                session.query(Device)
                .filter(Device.device_serial_no == asset.device_imei)
                .first()
            )

            device.assign_to_asset_status = datetime.now()
            session.commit()
            session.refresh(device)

            updated_asset = (
                session.query(self.model).filter(self.model.uuid == asset_uuid).first()
            )

            return updated_asset
