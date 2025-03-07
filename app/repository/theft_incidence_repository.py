from typing import Callable

from sqlalchemy import Date, cast, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.security import extract_user_data
from app.model.asset import Asset
from app.model.theft_incidence import TheftIncidence
from app.repository.base_repository import BaseRepository
from app.util.enums import IncidentStatus
from sqlalchemy.future import select


class TheftIncidenceRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, TheftIncidence)

    async def get_all_incidence(
        self,
        page=1,
        page_size=10,
        search_query=None,
        start_date=None,
        end_date=None,
        status=None,
    ):
        async with self.session_factory() as session:
            try:
                offset = (page - 1) * page_size

                base_query = (
                    select(self.model)
                    .join(self.model.asset)
                    .options(joinedload(self.model.user), joinedload(self.model.asset))
                )

                if search_query:
                    base_query = base_query.where(
                        self.model.asset.has(
                            Asset.asset_name.ilike(f"%{search_query}%")
                        )
                    )
                if status:
                    base_query = base_query.where(
                        self.model.status == IncidentStatus(status)
                    )
                if start_date:
                    base_query = base_query.where(
                        cast(self.model.created_at, Date) >= start_date
                    )
                if end_date:
                    base_query = base_query.where(
                        cast(self.model.created_at, Date) <= end_date
                    )

                # Get total count
                total_incidences = await session.execute(
                    select(func.count()).select_from(base_query.subquery())
                )
                total_incidences = total_incidences.scalar_one()

                # Get resolved and unresolved counts
                resolved_count = await session.execute(
                    select(func.count()).where(
                        self.model.status == IncidentStatus.RESOLVED
                    )
                )
                resolved_count = resolved_count.scalar_one()

                unresolved_count = await session.execute(
                    select(func.count()).where(
                        self.model.status == IncidentStatus.UNRESOLVED
                    )
                )
                unresolved_count = unresolved_count.scalar_one()

                # Fetch paginated results
                results = await session.execute(
                    base_query.offset(offset).limit(page_size)
                )
                paginated_incidences = results.scalars().all()

                result = [
                    {
                        "uuid": incidence.uuid,
                        "incident_type": incidence.incident_type,
                        "id": incidence.id,
                        "updated_at": incidence.updated_at,
                        "user_uuid": incidence.user_uuid,
                        "asset_uuid": incidence.asset_uuid,
                        "status": incidence.status,
                        "created_at": incidence.created_at,
                        "user": extract_user_data(incidence.user),
                        "asset": incidence.asset,
                    }
                    for incidence in paginated_incidences
                ]

                return {
                    "incidences": result,
                    "total_incidences": total_incidences,
                    "total_pages": (total_incidences + page_size - 1) // page_size,
                    "current_page": page,
                    "page_size": page_size,
                    "resolved_count": resolved_count,
                    "unresolved_count": unresolved_count,
                }
            except Exception as e:
                raise e

    async def mark_as_resolve(self, incident_uuid: str):
        async with self.session_factory() as session:
            incidence = await session.get(self.model, incident_uuid)

            if not incidence:
                return None  # Or raise an exception

            incidence.status = IncidentStatus.RESOLVED
            await session.commit()
            await session.refresh(incidence)

            return incidence
