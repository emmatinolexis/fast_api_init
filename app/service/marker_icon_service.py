from app.repository.marker_icon_repository import MarkerIconRepository
from app.service.base_service import BaseService


class MarkerIconService(BaseService):
    def __init__(self, marker_icon_repository: MarkerIconRepository):
        self.marker_icon_repository = marker_icon_repository
        super().__init__(marker_icon_repository)
