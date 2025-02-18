from app.repository.third_party_app_user_repository import ThirdPartAppUserRepository
from app.service.base_service import BaseService


class ThirdPartyAppUserService(BaseService):
    def __init__(self, third_party_app_user_repository: ThirdPartAppUserRepository):
        self.third_party_app_user_repository = third_party_app_user_repository
        super().__init__(third_party_app_user_repository)

    async def get_app_users(self):
        try:
            devices = await self.third_party_app_user_repository.get_app_users()
            return devices
        except Exception as e:
            raise e
