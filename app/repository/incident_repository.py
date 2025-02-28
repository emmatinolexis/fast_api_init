import logging
from typing import Callable, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import LATITUDE, LONGITUDE, RADIUS
from app.model.incident import Incident
from app.repository.base_repository import BaseRepository
from app.schema.incident_schema import IncidentPayload
from app.util.enums import IncidenceType, IncidentStatus, IncidentType


class IncidentRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory
        super().__init__(session_factory, Incident)

    async def create_incident(self, incident: IncidentPayload):
        async with self.session_factory() as session:
            try:
                # return IncidentStatus.VERIFIED.value
                # Fetch similar incidents within a 100m radius
                incidents = await self.get_incidents_by_location_incident_type(
                    incident_type=incident.incident_type,
                    longitude=incident.longitude,
                    latitude=incident.latitude,
                    radius=100,
                )

                # Create a new incident entry
                incident_data = Incident(
                    incident_type=incident.incident_type,
                    longitude=incident.longitude,
                    latitude=incident.latitude,
                    user_uuid=incident.user_uuid,
                )

                if len(incidents) > 1:
                    # If multiple incidents exist, verify unverified ones
                    for existing_incident in incidents:
                        if existing_incident.status.lower() == str(
                            IncidentStatus.UNVERIFIED.lower()
                        ):
                            updated_incident = await self.update_attr_by_uuid(
                                existing_incident.uuid,
                                "status",
                                IncidentStatus.VERIFIED,
                            )
                            logging.info(f"Updated incident: {updated_incident.uuid}")

                    # Set the new incident status to VERIFIED
                    incident_data.status = IncidentStatus.VERIFIED

                # Add the new incident to the session
                session.add(incident_data)
                await session.commit()
                await session.refresh(incident_data)

                return incident_data

            except Exception as e:
                await session.rollback()  # Ensure rollback is awaited
                logging.error(f"Error creating incident: {str(e)}")
                raise e

    def get_all_incidents(
        self,
        incident_type: IncidenceType = None,
        page: int = 1,
        page_size: int = 10,
        status: str = None,
    ) -> List[Incident]:
        with self.session_factory() as session:
            query = session.query(self.model)

            if incident_type:
                query = query.filter_by(incident_type=incident_type)

            if status:
                query = query.filter_by(status=IncidentStatus(status))

            offset = (page - 1) * page_size
            incidents = query.offset(offset).limit(page_size).all()

            return incidents

    def get_incidents_by_location(
        self, longitude: float, latitude: float, radius: int = 50
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
            query, {LONGITUDE: longitude, LATITUDE: latitude, RADIUS: radius}
        )

        incidents = []
        for row in result:
            row_dict = dict(row._mapping)
            incidents.append(Incident(**row_dict))

        return incidents

    async def get_incidents_by_location_incident_type(
        self,
        incident_type: IncidenceType,
        longitude: float,
        latitude: float,
        radius: int = 50,
    ) -> List[Incident]:
        async with self.session_factory() as session:
            query = text(
                """
                SELECT * FROM incidents
                WHERE incident_type = :incident_type
                AND ST_DWithin(
                    geography(ST_MakePoint(longitude, latitude)),
                    geography(ST_MakePoint(:longitude, :latitude)),
                    :radius
                )
                """
            )

            result = await session.execute(
                query,
                {
                    "longitude": longitude,
                    "latitude": latitude,
                    "radius": radius,
                    "incident_type": incident_type.name,
                },
            )

            incidents = [Incident(**row._mapping) for row in result.fetchall()]
            return incidents

    def get_all_incident_count(self) -> int:
        with self.session_factory() as session:
            return session.query(self.model).count()

    def get_incidents_report(
        self,
        start_date: str = None,
        end_date: str = None,
        search_parameter: str = None,
        page: int = 1,
        page_size: int = 10,
        status=None,
    ):
        with self.session_factory() as session:
            offset = (page - 1) * page_size
            limit = page_size

            date_filter = " AND 1=1"
            params = {"limit": limit, "offset": offset}

            if start_date:
                date_filter = " AND cl.created_at >= :start_date"
                params["start_date"] = start_date
            if end_date:
                date_filter += " AND cl.created_at <= :end_date"
                params["end_date"] = end_date

            search_filter = ""
            if search_parameter:
                search_filter = (
                    " AND (u.first_name ILIKE :search OR u.last_name ILIKE :search)"
                )
                params["search"] = f"%{search_parameter}%"

            status_filter = ""
            if status:
                status_filter = " AND cl.status = :status"
                params["status"] = status

            query = text(
                f"""
            with cluster_incidents_by_type AS (
            SELECT i.id, i.incident_type, i.longitude, i.latitude, i.user_uuid, i.created_at, i.status,
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
                    50
                )
               ) AS count,
                cl.created_at AS created_at,
                cl.status AS status
            FROM cluster_incidents_by_type cl
            JOIN users u ON cl.user_uuid = u.uuid
            WHERE cl.rn = 1 
            {search_filter}
            {date_filter}
            {status_filter}
            LIMIT :limit OFFSET :offset;
        """
            )

        result = session.execute(query, params).fetchall()
        return result

    def update_incident_by_incident_type(
        self,
        incident_type: IncidentType,
    ):
        with self.session_factory() as session:
            session.query(Incident).filter_by(
                incident_type=incident_type
            ).filter_by().update()
