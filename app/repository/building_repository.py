from contextlib import AbstractContextManager
from typing import Any, Callable, Dict

from sqlalchemy import asc
from sqlalchemy.orm import Session, joinedload

from app.model.buildings import Building
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

            assets = (
                paginated_query.options(joinedload(self.model.gas_cylinders))
                .options(joinedload(self.model.gas_events))
                .options(joinedload(self.model.gas_device))
                .options(joinedload(self.model.cylinder_type))
                .all()
            )

            for asset in assets:
                last_gas_event = asset.gas_events
                return last_gas_event
                # current_gas_level = calculate_gas_level_percentage(asset.gas)

            return {
                "assets": assets,
                "total_assets": total_assets,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
            }
