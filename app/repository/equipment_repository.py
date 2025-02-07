from typing import Any, Callable, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.model.equipment import Equipment
from app.repository.base_repository import BaseRepository
from app.util.enums import ActiveStatus


class EquipmentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, Equipment)

    async def get_equipments_by_asset_uuid(self, asset_uuid: str) -> List[Equipment]:
        async with self.session_factory() as session:
            query = (
                select(self.model)
                .filter_by(asset_uuid=asset_uuid)
                .options(joinedload(self.model.asset_type))
            )
            result = await session.execute(query)
            return list(result.scalars().unique().all())

    async def get_equipment_by_asset_uuid(self, asset_uuid: str) -> Optional[Equipment]:
        async with self.session_factory() as session:
            query = (
                select(self.model)
                .filter_by(asset_uuid=asset_uuid)
                .options(joinedload(self.model.asset_type))
            )
            result = await session.execute(query)
            return result.unique().scalar_.one_or_none()

    async def get_equipments(
        self,
        page: int = 1,
        page_size: int = 10,
        search_query: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        async with self.session_factory() as session:
            # Base query with join
            query = select(self.model).options(joinedload(self.model.asset_type))

            # Apply filters
            if search_query:
                query = query.filter(self.model.name.ilike(f"%{search_query}%"))

            if status:
                query = query.filter(self.model.status == ActiveStatus(status))

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await session.execute(count_query)
            total_records = total_result.scalar()

            # Apply pagination
            offset = (page - 1) * page_size
            paginated_query = query.offset(offset).limit(page_size)

            # Execute query
            result = await session.execute(paginated_query)
            equipments = result.unique().scalars().all()

            return {
                "data": equipments,
                "total_records": total_records,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_records + page_size - 1) // page_size,
            }
