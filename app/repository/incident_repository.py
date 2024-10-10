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

    def get_all_incidents(
        self, incident_type: IncidenceType = None, page: int = 1, page_size: int = 10
    ) -> List[Incident]:
        with self.session_factory() as session:
            offset = (page - 1) * page_size
            if incident_type:
                return (
                    session.query(self.model)
                    .filter_by(incident_type=incident_type)
                    .offset(offset)
                    .limit(page_size)
                    .all()
                )

            return session.query(self.model).offset(offset).limit(page_size).all()

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

    def get_all_incident_count(self) -> int:
        with self.session_factory() as session:
            return session.query(self.model).count()

    def get_incidents_report(self, page: int = 1, page_size: int = 10):
        with self.session_factory() as session:
            offset = (page - 1) * page_size
            limit = page_size
            query = text(
                """
            with cluster_incidents_by_type AS (
            SELECT i.id, i.incident_type, i.longitude, i.latitude, i.user_uuid, i.created_at,
                ROW_NUMBER() OVER (PARTITION BY i.incident_type ORDER BY i.id) AS rn
            FROM incidents i
            )
            SELECT 
                cl.id AS id,
                cl.incident_type AS incident_type,
                cl.longitude AS longitude,
                cl.latitude AS latitude,
                u.first_name  AS first_name,
                u.last_name  AS last_name,
                (SELECT COUNT(*)
                FROM incidents i
                WHERE i.incident_type = cl.incident_type
                AND ST_DWithin(
                    geography(ST_MakePoint(i.longitude, i.latitude)),
                    geography(ST_MakePoint(cl.longitude, cl.latitude)),
                    2000
                )
               ) AS count,
                cl.created_at as created_at
            FROM cluster_incidents_by_type cl
            JOIN users u ON cl.user_uuid = u.uuid
            WHERE cl.rn = 1 
            LIMIT :limit OFFSET :offset;
        """
            )

        result = session.execute(query, {"limit": limit, "offset": offset}).fetchall()
        return result
