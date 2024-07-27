from contextlib import AbstractContextManager
from typing import Any, Callable, Dict

from sqlalchemy import asc
from sqlalchemy.orm import Session, joinedload

from app.model.buildings import Building
from app.model.gas_cylinders import GasCylinder
from app.repository.base_repository import BaseRepository
from app.util.utils import calculate_gas_level_percentage


class BuildingRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Building)

    def read_all_building(
        self,
        user_uuid: str = None,
        business_uuid: str = None,
        page=1,
        page_size=10,
    ) -> Dict[str, Any]:
        with self.session_factory() as session:
            # Calculate the offset based on the page and per_page values
            offset = (page - 1) * page_size
            buildings = []
            # Start with a base query
            base_query = session.query(self.model)

            if user_uuid is not None:
                # Add filter for user UUID
                base_query = base_query.filter(self.model.user_uuid == user_uuid)

            if business_uuid is not None:
                # Add filter for business UUID
                base_query = base_query.filter(
                    self.model.business_profile_uuid == business_uuid
                )

            # Query to get the total count of assets
            total_assets = base_query.count()

            # Calculate total pages
            total_pages = (total_assets + page_size - 1) // page_size

            # Apply ordering and pagination
            paginated_query = (
                base_query.order_by(asc(self.model.created_at))
                .offset(offset)
                .limit(page_size)
            )

            assets = paginated_query.options(
                joinedload(self.model.gas_cylinders).joinedload(GasCylinder.gas_events),
                joinedload(self.model.gas_cylinders).joinedload(GasCylinder.gas_device),
                joinedload(self.model.gas_cylinders).joinedload(
                    GasCylinder.cylinder_type
                ),
            ).all()

            for asset in assets:
                building_cylinders = []
                for event in asset.gas_cylinders:
                    cylinder_type = event.cylinder_type
                    if event.gas_events:
                        last_gas_event = event.gas_events[-1]

                        gas_level = calculate_gas_level_percentage(
                            cylinder_type.empty_weight,
                            cylinder_type.full_weight,
                            last_gas_event.current_weight,
                        )
                    else:
                        gas_level = 0  # Set gas level to 0 if there are no gas events

                    cylinder = {
                        "cylinder_name": event.cylinder_name,
                        "status": event.status,
                        "gas_level_in_percentage": round(gas_level),
                        "gas_device": {
                            "device_name": event.gas_device.device_name,
                            "serial_number": event.gas_device.serial_number,
                            "status": event.gas_device.status,
                            "created_at": event.gas_device.created_at,
                        },
                    }

                    building_cylinders.append(cylinder)

                building_asset = {
                    "building_name": asset.building_name,
                    "longitude": asset.longitude,
                    "latitude": asset.latitude,
                    "status": asset.status,
                    "image_url": asset.image_url,
                    "cylinders": building_cylinders,
                }
                buildings.append(building_asset)

            return {
                "assets": buildings,
                "total_assets": total_assets,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }
