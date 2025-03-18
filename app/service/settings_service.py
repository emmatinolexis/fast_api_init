from app.repository.setting_repository import SettingRepository
from app.service.base_service import BaseService


class SettingService(BaseService):
    def __init__(self, setting_repository: SettingRepository):
        self.setting_repository = setting_repository
        super().__init__(setting_repository)
