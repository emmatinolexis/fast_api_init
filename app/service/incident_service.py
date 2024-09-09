from app.repository.incident_repository import IncidentRepository
from app.schema.incident_schema import IncidentPayload
from app.service.base_service import BaseService
from app.util.enums import CrowdIncidentType
from app.model.incident import Incident

class IncidentService(BaseService):
    def __init__(self, incident_repository: IncidentRepository):
        self.incident_repository = incident_repository
        super().__init__(incident_repository)

    def create_incident(self, incident_payload: IncidentPayload):
        try:
            incident = self.incident_repository.create(incident_payload)
            return incident
        except Exception as e:
            raise e

    def get_all_incidents(self,incident_type:CrowdIncidentType): 
        try:
             return self.incident_repository.get_all_incidents(incident_type=incident_type)
        except Exception as e:
            raise e