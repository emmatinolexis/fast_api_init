from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session, joinedload

from app.core.security import extract_user_data
from app.model.theft_incidence import TheftIncidence
from app.repository.base_repository import BaseRepository


class TheftIncidenceRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, TheftIncidence)

    def get_all_incidence(self):
        with self.session_factory() as session:
            incidences = (
                session.query(self.model)
                .options(joinedload(self.model.user))
                .options(joinedload(self.model.asset))
                .all()
            )
            result = []
            for incidence in incidences:
                incidence_data = {
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
                result.append(incidence_data)
            return result
