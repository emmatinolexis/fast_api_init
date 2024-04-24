from app.repository.external_app_repository import ExternalAppRepository
from app.schema.external_app_schema import ExternalAppPayload
from app.service.base_service import BaseService


class ExternalAppService(BaseService):
    def __init__(self, external_app_repository: ExternalAppRepository):
        self.external_app_repository = external_app_repository
        super().__init__(external_app_repository)

    def create_external_app(self, payload: ExternalAppPayload):
        try:
            external_app = self.external_app_repository.create_external_app(payload)
            return external_app
        except Exception as e:
            raise e
