from app.core import messages
from app.core.exceptions import NotFoundError
from app.repository.asset_repository import AssetRepository
from app.repository.asset_type_repository import AssetTypeRepository
from app.repository.driver_repository import DriverRepository
from app.repository.equipment_repository import EquipmentRepository
from app.repository.equipment_type_repository import EquipmentTypeRepository
from app.repository.marker_icon_repository import MarkerIconRepository
from app.repository.user_repository import UserRepository
from app.schema.asset_schema import AssetInput, AssetPayload, DriverPayload
from app.service.base_service import BaseService


class AssetService(BaseService):
    def __init__(
        self,
        asset_repository: AssetRepository,
        asset_type_repository: AssetTypeRepository,
        user_repository: UserRepository,
        equipment_repository: EquipmentRepository,
        equipment_type_repository: EquipmentTypeRepository,
        marker_icon_repository: MarkerIconRepository,
        driver_repository: DriverRepository,
    ):
        self.asset_repository = asset_repository
        self.asset_type_repository = asset_type_repository
        self.user_repository = user_repository
        self.equipment_repository = equipment_repository
        self.equipment_type_repository = equipment_type_repository
        self.marker_icon_repository = marker_icon_repository
        self.driver_repository = driver_repository
        super().__init__(asset_repository)

    def create_asset(self, asset: AssetPayload):
        try:
            if self.user_repository.read_by_uuid(asset.user_uuid) is None:
                raise NotFoundError(
                    detail=messages.USER_NOT_FOUND + str(asset.user_uuid)
                )

            if self.asset_type_repository.read_by_uuid(asset.asset_type_uuid) is None:
                raise NotFoundError(
                    detail=messages.ASSET_TYPE_NOT_FOUND + str(asset.asset_type_uuid)
                )

            if self.equipment_repository.read_by_uuid(asset.equipment_uuid) is None:
                raise NotFoundError(
                    detail=messages.EQUIPMENT_NOT_FOUND + str(asset.equipment_uuid)
                )

            if self.marker_icon_repository.read_by_uuid(asset.marker_icon_uuid) is None:
                raise NotFoundError(
                    detail=messages.MARKER_ICON_NOT_FOUND + str(asset.marker_icon_uuid)
                )
            
            created_asset = self.asset_repository.create(AssetInput(**asset.dict()))
            if asset.add_driver:
                driver_data = DriverPayload(
                    asset_uuid=created_asset.uuid,
                    first_name=asset.driver_first_name,
                    last_name=asset.driver_last_name,
                    phone_number=asset.driver_phone_number,
                    license_url=asset.driver_license_url,
                    profile_picture_url=asset.driver_profile_picture_url,
                )
                self.driver_repository.create(driver_data)
            return created_asset
        except Exception as e:
            raise e

    def get_assets_by_user_uuid(
        self, uuid: str, asset_type_uuid: str = None, page=1, page_size=10
    ):
        try:
            return self.asset_repository.read_all_assets_by_uuid(
                uuid, asset_type_uuid, page, page_size
            )
        except Exception as e:
            raise e
