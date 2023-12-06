from app.repository.feature_repository import FeatureRepository
from app.service.base_service import BaseService


class FeatureService(BaseService):
    def __init__(self, feature_repository: FeatureRepository):
        self.feature_repository = feature_repository
        super().__init__(feature_repository)
