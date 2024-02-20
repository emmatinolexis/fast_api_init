from app.core import messages
from app.core.exceptions import NotFoundError
from app.repository.asset_repository import AssetRepository
from app.repository.asset_type_repository import AssetTypeRepository
from app.repository.driver_repository import DriverRepository
from app.repository.equipment_repository import EquipmentRepository
from app.repository.equipment_type_repository import EquipmentTypeRepository
from app.repository.user_repository import UserRepository
from app.schema.asset_schema import AssetInput, AssetPayload
from app.service.base_service import BaseService


class AssetService(BaseService):
    def __init__(
        self,
        asset_repository: AssetRepository,
        asset_type_repository: AssetTypeRepository,
        user_repository: UserRepository,
        equipment_repository: EquipmentRepository,
        equipment_type_repository: EquipmentTypeRepository,
        driver_repository: DriverRepository,
    ):
        self.asset_repository = asset_repository
        self.asset_type_repository = asset_type_repository
        self.user_repository = user_repository
        self.equipment_repository = equipment_repository
        self.equipment_type_repository = equipment_type_repository
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
            # created_asset = self.asset_repository.create(AssetInput(**asset.dict()))
            if asset.add_driver:
                if self.driver_repository.read_by_uuid(asset.driver_uuid) is None:
                    raise NotFoundError(
                        detail=messages.DRIVER_NOT_FOUND + str(asset.driver_uuid)
                    )
                created_asset = self.asset_repository.create(AssetInput(**asset.dict()))

                updated_driver = self.driver_repository.update_driver_asset(
                    created_asset.uuid, asset.driver_uuid
                )

                created_asset_data = {
                    "user_uuid": created_asset.user_uuid,
                    "asset_type_uuid": created_asset.asset_type_uuid,
                    "asset_name": created_asset.asset_name,
                    "vehicle_license_no": created_asset.vehicle_license_no,
                    "asset_status": created_asset.asset_status,
                    "equipment_type_uuid": created_asset.equipment_type_uuid,
                    "device_imei": created_asset.device_imei,
                    "vin": created_asset.vin,
                    "marker_color": created_asset.marker_color,
                    "equipment_uuid": created_asset.equipment_uuid,
                    "serial_number": created_asset.serial_number,
                    "make": created_asset.make,
                    "model": created_asset.model,
                    "driver": updated_driver,
                }

                return created_asset_data
            else:
                created_asset = self.asset_repository.create(AssetInput(**asset.dict()))
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

    def assign_device_imei(self, uuid: str, imei: str):
        try:
            asset = self.asset_repository.assign_device_imei(uuid, imei)
            return asset
        except Exception as e:
            raise e
