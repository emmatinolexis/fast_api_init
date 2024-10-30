from app.repository.installation_repository import InstallationRepository
from app.schema.installation_schema import InstallationPayload


class InstallationService:
    def __init__(self, installation_repository: InstallationRepository):
        self.installation_repository = installation_repository

    def create_installation(self, installation_payload: InstallationPayload):
        try:
            return self.installation_repository.create_installation(installation_payload)
        except Exception as e:
            raise e
    
    def fetch_all_installers(self):
        try:
            return self.installation_repository.get_installers()
        except Exception as e:
            raise e
            
    
