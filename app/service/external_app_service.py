from app.core.security import generate_access_token_for_third_party_app
from app.repository.external_app_repository import ExternalAppRepository
from app.schema.external_app_schema import (
    ExternalAppGenerateTokenPayload,
    ExternalAppPayload,
)
from app.service.base_service import BaseService
from app.util.enums import UserRole
from app.util.utils import days_to_minutes


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

    def get_app_service_by_secret_key(self, secret_key: str):
        try:
            external_app = self.external_app_repository.get_app_service_by_secret_key(
                secret_key
            )
            return external_app
        except Exception as e:
            raise e

    def generate_token(self, payload: ExternalAppGenerateTokenPayload):
        try:
            external_app = self.external_app_repository.get_app_service(payload)
            expiry_minutes = days_to_minutes(external_app.no_of_days_to_expire)
            generated_token = generate_access_token_for_third_party_app(
                external_app.secret_key, expiry_minutes, UserRole.THIRD_PARTY_APP
            )
            app_service_data = {
                "access_token": generated_token[0],
                "expiry_date": generated_token[1],
            }
            return app_service_data
        except Exception as e:
            raise e
