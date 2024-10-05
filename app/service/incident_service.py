from typing import Dict

from app.model.incident import Incident
from app.repository.incident_repository import IncidentRepository
from app.schema.incident_schema import IncidentPayload
from app.service.base_service import BaseService
from app.util.enums import IncidenceType


class IncidentService(BaseService):
    def __init__(self, incident_repository: IncidentRepository):
        self.incident_repository = incident_repository
        super().__init__(incident_repository)

    def create_incident(self, incident_payload: IncidentPayload) -> Incident:
        try:
            return self.incident_repository.create(incident_payload)
        except Exception as e:
            raise e

    def get_all_incidents(
        self, incident_type: IncidenceType, page: int = 1, page_size: int = 10
    ):
        try:
            return self.incident_repository.get_all_incidents(
                incident_type=incident_type, page=page, page_size=page_size
            )
        except Exception as e:
            raise e

    def get_incidents_by_location(
        self,
        longitude: float,
        latitude: float,
        radius: int,
    ) -> list[Incident]:
        try:
            return self.incident_repository.get_incidents_by_location(
                longitude=longitude, latitude=latitude, radius=radius
            )
        except Exception as e:
            raise e

    def get_all_incidents_count(self) -> int:
        try:
            return self.incident_repository.get_all_incident_count()
        except Exception as e:
            raise e

    def get_incident_reports(self, page: int = 1, page_size: int = 10):
        try:
            incidents = self.incident_repository.get_incidents_report(
                page=page, page_size=page_size
            )

            total_incidents = len(incidents)

            return {
                "total": total_incidents,
                "data": [
                    {
                        "id": incident[0],
                        "incidentType": incident[1].lower(),
                        "longitude": incident[2],
                        "latitude": incident[3],
                        "firstName": incident[4],
                        "lastName": incident[5],
                        "count": incident[6],
                        "createdAt": incident[7],
                    }
                    for incident in incidents
                ],
            }

        except Exception as e:
            raise e

    def total_pages(self, count: int, limit: int) -> int:
        return int(count / limit) + (count % limit > 0)

    def pagination(
        self, total: int, current_page: int, limit: int, total_pages: int
    ) -> Dict[str, int]:
        return {
            "total": total,
            "page": current_page,
            "pageSize": limit,
            "totalPages": total_pages,
        }
