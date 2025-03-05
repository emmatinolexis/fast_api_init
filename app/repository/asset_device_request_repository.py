from typing import Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import subqueryload

from app.model.asset import Asset
from app.model.asset_device_request import AssetDeviceRequest
from app.repository.base_repository import BaseRepository
from app.schema.asset_schema import CreateAssetDeviceRequestPayload
from app.util.enums import AssetDeviceRequestStatus


class AssetDeviceRequestRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, AssetDeviceRequest)

    async def get_asset_device_request_by_user_by_asset_type_uuid(
        self, user_uuid: str, asset_type_uuid: str
    ):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).filter(
                    self.model.asset_type_uuid == asset_type_uuid,
                    self.model.user_uuid == user_uuid,
                )
            )
            return result.scalars().first()

    async def update_status(self, request_uuid: str):
        async with self.session_factory() as session:
            try:
                result = await session.execute(
                    select(self.model).filter(self.model.uuid == request_uuid)
                )
                request = result.scalars().first()
                request.status = AssetDeviceRequestStatus.PROCESSING
                await session.commit()
                await session.refresh(request)
                return request
            except Exception as e:
                return Exception(e)

    async def create_asset_device_request(
        self, asset_device_request: CreateAssetDeviceRequestPayload
    ):
        device_request = AssetDeviceRequest(
            user_uuid=asset_device_request.user_uuid,
            metrics=asset_device_request.metrics,
            status=asset_device_request.status,
        )

        async with self.session_factory() as session:
            try:
                session.add(device_request)
                await session.commit()
                await session.refresh(device_request)

                # Fetch Asset objects corresponding to the provided UUIDs
                result = await session.execute(
                    select(Asset).filter(
                        Asset.uuid.in_(asset_device_request.asset_uuids)
                    )
                )
                assets = result.scalars().all()
                # Append the fetched Asset objects to device_request.assets
                device_request.assets.extend(assets)

                await session.commit()

            except Exception as e:
                return Exception(e)
            return device_request

    async def get_asset_device_requests_by_user_uuid(self, user_uuid: str):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model)
                .filter(self.model.user_uuid == user_uuid)
                .options(subqueryload(AssetDeviceRequest.assets))
                .options(subqueryload(self.model.user))
            )
            return result.scalars().all()

    async def get_asset_device_requests(self):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model)
                .options(subqueryload(AssetDeviceRequest.assets))
                .options(subqueryload(self.model.user))
            )
            return result.scalars().all()
