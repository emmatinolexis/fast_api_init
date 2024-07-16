from app.repository.asset_repository import AssetRepository
from app.repository.device_repository import DeviceRepository
from app.repository.user_repository import UserRepository
from app.service.base_service import BaseService


class ReportService(BaseService):
    def __init__(
        self,
        device_repository: DeviceRepository,
        user_repository: UserRepository,
        asset_repository: AssetRepository,
    ):
        self.asset_repository = (asset_repository,)
        self.device_repository = (device_repository,)
        self.user_repository = (user_repository,)
        # super().__init__(asset_repository)

    def generate_report(self):
        try:
            return "ok"
        except Exception as e:
            raise e

    # def generate_distance_traveled_user_report(self, user_uuid: str):
    #     try:
    #         user_assets = self.asset_repository.
    #     except Exception as e:
    #         raise e
    #
    # def generate_distance_traveled_buisiness_report(self, user_uuid: str):
    #     try:
    #         user = "i"
    #     except Exception as e:
    #         raise e
