from contextlib import AbstractContextManager
from typing import Callable, List

from sqlalchemy import text

from app.model.incident import Incident
from app.repository.base_repository import BaseRepository
from app.util.enums import IncidenceType


class IncidentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager]):
        self.session_factory = session_factory
        super().__init__(session_factory, Incident)

    def get_all_incidents(self, incident_type: IncidenceType = None) -> List[Incident]:
        with self.session_factory() as session:
            if incident_type:
                return (
                    session.query(self.model)
                    .filter_by(incident_type=incident_type)
                    .all()
                )
            return self.read_all()

    def get_incidents_by_location(
        self, longitude: float, latitude: float, radius: int = 2000
    ) -> List[Incident]:
        with self.session_factory() as session:
            query = text(
                """
            SELECT *
            FROM incidents
            WHERE ST_DWithin(
                geography(ST_MakePoint(longitude, latitude)),
                geography(ST_MakePoint(:longitude, :latitude)),
                :radius
            )
            """
            )

        result = session.execute(
            query, {"longitude": longitude, "latitude": latitude, "radius": radius}
        )

        incidents = []
        for row in result:
            row_dict = dict(row._mapping)
            incidents.append(Incident(**row_dict))

        return incidents
