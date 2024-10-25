from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.core.security import extract_user_data
from app.model.theft_incidence import TheftIncidence
from app.model.asset import Asset
from app.repository.base_repository import BaseRepository
from app.util.enums import IncidentStatus
from sqlalchemy import cast, Date,func


class TheftIncidenceRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, TheftIncidence)


    def get_all_incidence(self, page=1, page_size=10, search_query=None, start_date=None, end_date=None):
        with self.session_factory() as session:
            try:
                offset = (page - 1) * page_size

                base_query = (
                    session.query(self.model)
                    .join(self.model.asset)  
                    .options(joinedload(self.model.user), joinedload(self.model.asset))
                )
                
                if search_query:
                    base_query = base_query.filter(
                        self.model.asset.has(Asset.asset_name.ilike(f"%{search_query}%"))
                    )
                    
                if start_date:
                    base_query = base_query.filter(cast(self.model.created_at, Date) >= start_date)
                if end_date:
                    base_query = base_query.filter(cast(self.model.created_at, Date) <= end_date)

                total_incidences = base_query.count()

                resolved_count = session.query(func.count()).filter(self.model.status == IncidentStatus.RESOLVED).scalar()
                unresolved_count = session.query(func.count()).filter(self.model.status == IncidentStatus.UNRESOLVED).scalar()

                paginated_incidences = base_query.offset(offset).limit(page_size).all()

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
                    "unresolved_count": unresolved_count
                }
            except Exception as e:
                session.rollback()
                raise e

    def mark_as_resolve(self, incident_uuid: str):
        with self.session_factory() as session:
            incidence = session.query(self.model).filter_by(uuid=incident_uuid).first()
            incidence.status = IncidentStatus.RESOLVED
            session.commit()
            session.refresh(incidence)
            return incidence
