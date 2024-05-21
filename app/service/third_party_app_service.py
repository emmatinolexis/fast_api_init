from app.repository.third_party_app_repository import ThirdPartyAppRepository
from app.service.base_service import BaseService


class ThirdPartyAppService(BaseService):
    def __init__(self, third_party_app_repository: ThirdPartyAppRepository):
        self.third_party_app_repository = third_party_app_repository
        super().__init__(third_party_app_repository)
