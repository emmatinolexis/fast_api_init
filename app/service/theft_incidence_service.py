from app.repository.theft_incidence_repository import TheftIncidenceRepository
from app.service.base_service import BaseService


class TheftIncidenceService(BaseService):
    def __init__(self, theft_incidence_repository: TheftIncidenceRepository):
        self.theft_incidence_repository = theft_incidence_repository
        super().__init__(theft_incidence_repository)
