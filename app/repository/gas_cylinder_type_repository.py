from contextlib import AbstractContextManager
from typing import Callable, Optional

from sqlalchemy import String, cast
from sqlalchemy.orm import Session

from app.model.gas_cylinders import CylinderTypes
from app.repository.base_repository import BaseRepository
from app.util.enums import ActiveStatus


class GasCylinderTypeRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, CylinderTypes)

    
    async def filter_by_status_and_name(
        self,
        status: Optional[str] = None,
        search_query: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ):
        async with self.session_factory() as session:
            stmt = select(CylinderTypes)

            # Apply status filter
            if status:
                stmt = stmt.filter(CylinderTypes.status == ActiveStatus(status))

            # Apply search filter
            if search_query:
                stmt = stmt.filter(cast(CylinderTypes.name, String).ilike(f"%{search_query}%"))

            # Get total record count
            total_records_stmt = select(func.count()).select_from(stmt.subquery())
            total_records_result = await session.execute(total_records_stmt)
            total_records = total_records_result.scalar()

            # Apply pagination
            offset = (page - 1) * page_size
            stmt = stmt.offset(offset).limit(page_size)

            # Execute main query
            result = await session.execute(stmt)
            cylinder_types = result.scalars().all()

            return {
                "data": cylinder_types,
                "total_records": total_records,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_records + page_size - 1) // page_size if total_records else 0,
            }
