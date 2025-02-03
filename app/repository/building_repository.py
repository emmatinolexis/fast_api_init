from contextlib import AbstractAsyncContextManager
from typing import Any, Callable, Dict, Optional

from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.model.buildings import Building
from app.model.gas_cylinders import GasCylinder
from app.model.peripheral_devices import PeripheralDevice
from app.repository.base_repository import BaseRepository
from app.util.enums import ActiveStatus, BuildingStatus
from app.util.utils import calculate_gas_level_percentage


class BuildingRepository(BaseRepository):
    def __init__(
        self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    ):
        self.session_factory = session_factory
        super().__init__(session_factory, Building)

    async def read_building_by_uuid(
        self,
        building_uuid: str = None,
    ) -> Dict[str, Any]:
        async with self.session_factory() as session:
            building = await session.execute(
                select(self.model)
                .filter(self.model.uuid == building_uuid)
                .options(
                    joinedload(self.model.gas_cylinders).joinedload(
                        GasCylinder.gas_events
                    ),
                    joinedload(self.model.gas_cylinders).joinedload(
                        GasCylinder.gas_device
                    ),
                    joinedload(self.model.gas_cylinders).joinedload(
                        GasCylinder.cylinder_type
                    ),
                )
            )
            building = building.scalars().first()

            cylinders = []

            for cylinder in building.gas_cylinders:
                cylinder_type = cylinder.cylinder_type
                gas_events = cylinder.gas_events

                gas_level = self._get_gas_level(cylinder_type, gas_events)

                cylinder_data = {
                    "cylinder_uuid": cylinder.uuid,
                    "cylinder_name": cylinder.cylinder_name,
                    "cylinder_type_uuid": cylinder.cylinder_type_uuid,
                    "status": cylinder.status,
                    "gas_level_in_percentage": gas_level,
                    "gas_device": cylinder.gas_device,
                }

                cylinders.append(cylinder_data)

            building_data = {
                "building_uuid": building.uuid,
                "building_name": building.building_name,
                "longitude": building.longitude,
                "latitude": building.latitude,
                "status": building.status,
                "image_url": building.image_url,
                "cylinders": cylinders,
            }

            return building_data

    async def read_all_building(
        self,
        user_uuid: str = None,
        business_uuid: str = None,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        async with self.session_factory() as session:
            offset = (page - 1) * page_size
            base_query = await self._build_base_query(session, user_uuid, business_uuid)

            if search:
                search_pattern = f"%{search}%"
                base_query = base_query.filter(
                    self.model.building_name.ilike(search_pattern)
                )

            total_assets = base_query.count()
            total_pages = (total_assets + page_size - 1) // page_size

            paginated_query = (
                base_query.order_by(desc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )

            assets = self._load_related_models(paginated_query).all()
            buildings = self._build_building_assets(assets)

            return {
                "assets": buildings,
                "total_assets": total_assets,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }

    async def _build_base_query(
        self, session, user_uuid: str = None, business_uuid: str = None
    ):
        base_query = select(self.model)

        if user_uuid:
            base_query = base_query.filter(self.model.user_uuid == user_uuid)

        if business_uuid:
            base_query = base_query.filter(
                self.model.business_profile_uuid == business_uuid
            )

        return base_query

    def _load_related_models(self, query):
        return query.options(
            joinedload(self.model.gas_cylinders).joinedload(GasCylinder.gas_events),
            joinedload(self.model.gas_cylinders).joinedload(GasCylinder.gas_device),
            joinedload(self.model.gas_cylinders).joinedload(GasCylinder.cylinder_type),
            joinedload(self.model.peripheral_devices).joinedload(
                PeripheralDevice.building
            ),
        )

    def _build_building_assets(self, assets):
        buildings = []

        for asset in assets:
            building_cylinders = self._build_cylinder_info(asset.gas_cylinders)
            building_info = self._build_building_info(asset, building_cylinders)
            buildings.append(building_info)

        return buildings

    def _build_cylinder_info(self, cylinders):
        building_cylinders = []

        for cylinder in cylinders:
            cylinder_type = cylinder.cylinder_type
            gas_events = cylinder.gas_events

            gas_level = self._get_gas_level(cylinder_type, gas_events)
            gas_device_info = self._get_gas_device_info(cylinder.gas_device)

            cylinder_info = {
                "cylinder_name": cylinder.cylinder_name,
                "cylinder_type_uuid": cylinder.cylinder_type_uuid,
                "status": cylinder.status,
                "gas_level_in_percentage": round(gas_level, 2),
                "gas_device": gas_device_info,
            }

            building_cylinders.append(cylinder_info)

        return building_cylinders

    def _get_gas_level(self, cylinder_type, gas_events):
        if gas_events:
            # last_gas_event = gas_events[-1]
            last_gas_event = max(gas_events, key=lambda x: x.created_at)

            gas_level = calculate_gas_level_percentage(
                cylinder_type.empty_weight,
                cylinder_type.full_weight,
                last_gas_event.current_weight,
            )

            gas_level = max(
                0, min(gas_level, 100)
            )  # Ensure gas level is between 0 and 100
        else:
            gas_level = 0

        return gas_level

    def _get_gas_device_info(self, gas_device):
        if gas_device:
            return {
                "uuid": gas_device.uuid,
                "device_location": gas_device.location,
                "serial_number": gas_device.serial_number,
                "status": gas_device.status,
                "created_at": gas_device.created_at,
            }
        return {}

    def _build_building_info(self, asset, building_cylinders):
        # Check if there are no cylinders
        if not building_cylinders:
            status = BuildingStatus.PENDING_INSTALLATION
        else:
            status = BuildingStatus.SAFE

            # Loop through cylinders to check for low gas levels in active cylinders
            for cylinder in building_cylinders:
                if (
                    cylinder["status"] == ActiveStatus.ACTIVE
                    and cylinder["gas_level_in_percentage"] < 25
                ):
                    status = BuildingStatus.ATTENTION_NEEDED
                    break

        return {
            "building_uuid": asset.uuid,
            "building_name": asset.building_name,
            "longitude": asset.longitude,
            "latitude": asset.latitude,
            "status": status,
            "image_url": asset.image_url,
            "cylinders": building_cylinders,
            "created_at": asset.created_at,
        }

    async def read_all_assets_by_uuid_no_pagination(
        self,
        user_uuid: str = None,
        business_uuid: str = None,
        asset_uuid: str = None,
    ):
        async with self.session_factory() as session:
            if user_uuid is not None:
                if asset_uuid:
                    query = select(self.model).filter(self.model.uuid == asset_uuid)
                    result = await session.execute(query)
                    return result.scalars().all()
                else:
                    query = select(self.model).filter(self.model.user_uuid == user_uuid)
                    result = await session.execute(query)
                    return result.scalars().all()

            if business_uuid is not None:
                if asset_uuid:
                    query = select(self.model).filter(self.model.uuid == asset_uuid)
                    result = await session.execute(query)
                    return result.scalars().all()
                else:
                    query = select(self.model).filter(
                        self.model.business_profile_uuid == business_uuid
                    )
                    result = await session.execute(query)
                    return result.scalars().all()

            return []
