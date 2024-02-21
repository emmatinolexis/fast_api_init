from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable, List, Tuple

from sqlalchemy import desc, label
from sqlalchemy.orm import Session, joinedload

from app.model.asset import Asset
from app.model.device import Device
from app.model.tracking_event import TrackingEvent
from app.model.user import User
from app.repository.base_repository import BaseRepository
from app.util.enums import AssetStatus
from app.util.utils import get_status


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
            # return query
            if asset_type_uuid is not None:
                query = query.filter(self.model.asset_type_uuid == asset_type_uuid)

            query = (
                query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )

            assets = (
                query.options(joinedload(Asset.asset_type))
                .options(joinedload(Asset.driver))
                .options(joinedload(Asset.device))
                .all()
            )
            for asset in assets:
                # check if asset has device imei
                if asset.device_imei:
                    # Get device's last known location
                    last_tracking_event = (
                        session.query(
                            label("lat", TrackingEvent.latitude),
                            label("lng", TrackingEvent.longitude),
                            TrackingEvent.speed,
                            TrackingEvent.course,
                            label("timestamp", TrackingEvent.event_datetime),
                            label("event_type", get_status(TrackingEvent.event_type)),
                        )
                        .filter(TrackingEvent.device_imei == asset.device_imei)
                        .order_by(desc(TrackingEvent.event_datetime))
                        .first()
                    )

                    if last_tracking_event:
                        # Construct a dictionary with the retrieved fields
                        last_tracking_event_dict = {
                            "lat": last_tracking_event.lat,
                            "lng": last_tracking_event.lng,
                            "speed": last_tracking_event.speed,
                            "course": last_tracking_event.course,
                            "timestamp": last_tracking_event.timestamp,
                            "event_type": last_tracking_event.event_type,
                        }
                        # Add last_tracking_event_dict to asset dictionary
                        asset.last_tracking_event = last_tracking_event_dict
                    else:
                        # Handle case where no result is found
                        pass

            return assets, total_assets

    def assign_device_imei(self, asset_uuid, imei: str) -> Asset:
        with self.session_factory() as session:
            device = (
                session.query(Device).filter(Device.device_serial_no == imei).first()
            )
            # check if imei is valid
            if not device:
                raise Exception("Imei not found")

            # check if device already assigned
            if device.device_serial_no:
                raise Exception("Device already assigned to an asset")

            asset = (
                session.query(self.model).filter(self.model.uuid == asset_uuid).first()
            )

            # check if asset exist
            if not asset:
                raise Exception("Asset not found")

            # update asset with device imei
            asset.device_imei = imei
            asset.asset_status = AssetStatus.ACTIVE
            session.commit()
            session.refresh(asset)

            # update device with user_uuid, business_uuid if user type is business
            user = session.query(User).filter(User.uuid == asset.user_uuid).first()

            device.assign_to_asset_status = datetime.now()
            device.user_uuid = user.uuid

            if user.business_profile_uuid:
                device.business_profile_uuid = user.business_profile_uuid

            session.commit()
            session.refresh(device)

            updated_asset = (
                session.query(self.model).filter(self.model.uuid == asset_uuid).first()
            )

            return updated_asset
