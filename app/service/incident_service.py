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

    def get_all_incidents(self, incident_type: IncidenceType):
        try:
            return self.incident_repository.get_all_incidents(
                incident_type=incident_type
            )
        except Exception as e:
            raise e

    def get_incidents_by_location(
        self, longitude: float, latitude: float
    ) -> list[Incident]:
        try:
            return self.incident_repository.get_incidents_by_location(
                longitude=longitude, latitude=latitude
            )
        except Exception as e:
            raise e
