from app.model.incident import Incident
from app.repository.incident_repository import IncidentRepository
from app.schema.incident_schema import IncidentPayload
from app.service.base_service import BaseService
from app.util.enums import IncidenceType
from app.util.utils import convert_date


class IncidentService(BaseService):
    def __init__(self, incident_repository: IncidentRepository):
        self.incident_repository = incident_repository
        super().__init__(incident_repository)

    def create_incident(self, incident_payload: IncidentPayload) -> Incident:
        try:
            return self.incident_repository.create_incident(incident_payload)
        except Exception as e:
            raise e

    def get_all_incidents(
        self,
        incident_type: IncidenceType,
        page: int = 1,
        page_size: int = 10,
        status=None,
    ):
        try:
            return self.incident_repository.get_all_incidents(
                incident_type=incident_type,
                page=page,
                page_size=page_size,
                status=status,
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

    def get_incidents_by_location_incident_type(
        self,
        longitude: float,
        latitude: float,
        radius: int,
        incident_type: IncidenceType,
    ) -> list[Incident]:
        try:
            return self.incident_repository.get_incidents_by_location_incident_type(
                longitude=longitude,
                latitude=latitude,
                radius=radius,
                incident_type=incident_type,
            )
        except Exception as e:
            raise e

    def get_all_incidents_count(self) -> int:
        try:
            return self.incident_repository.get_all_incident_count()
        except Exception as e:
            raise e

    def get_incident_reports(
        self,
        start_date: str = None,
        end_date: str = None,
        search_parameter: str = None,
        page: int = 1,
        page_size: int = 10,
        status=None,
    ):
        try:
            date_format = "%d/%m/%Y"
            if start_date:
                start_date = convert_date(start_date, format=date_format)
            if end_date:
                end_date = convert_date(end_date, format=date_format)

            incidents = self.incident_repository.get_incidents_report(
                start_date=start_date,
                end_date=end_date,
                page=page,
                page_size=page_size,
                status=status,
                search_parameter=search_parameter,
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
                        "status": incident[8],
                    }
                    for incident in incidents
                ],
            }

        except Exception as e:
            raise e
