from app.repository.business_profile_repository import BusinessProfileRepository
from app.service.base_service import BaseService


class BusinessProfileService(BaseService):
    def __init__(self, business_profile_repository: BusinessProfileRepository):
        self.business_profile_repository = business_profile_repository
        super().__init__(business_profile_repository)
