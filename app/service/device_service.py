from app.repository.device_repository import DeviceRepository
from app.service.base_service import BaseService
from typing import Optional

class DeviceService(BaseService):
    def __init__(self, device_repository: DeviceRepository):
        self.device_repository = device_repository
        super().__init__(device_repository)

    def get_devices_by_user_uuid(self, user_uuid: str):
        try:
            devices = self.device_repository.get_devices_by_user_uuid(user_uuid)
            return devices
        except Exception as e:
            raise e

    def get_devices_by_business_uuid(self, business_uuid: str):
        try:
            devices = self.device_repository.get_devices_by_business_uuid(business_uuid)
            # return devices
            device_data = []
            for device in devices:
                data = {
                    "uuid": device.uuid,
                    "device_name": device.inventory.device_name,
                    "device_imei": device.device_imei,
                    "asset_name": device.asset.asset_name if device.asset else None,
                    "asset_vehicle_number": device.asset.vehicle_license_no
                    if device.asset
                    else None,
                    "device_image_url": device.inventory.images[0].image_url,
                }
                device_data.append(data)
            return device_data
        except Exception as e:
            raise e

    def get_user_data_by_device_uuid(self, device_imei: str):
        try:
            device = self.device_repository.get_user_data_by_device_uuid(device_imei)
            return device
        except Exception as e:
            raise e

    def get_all_devices(self, page: int = 1, page_size: int = 10, search_query: Optional[str] = None,status=None):
        try:
            devices = self.device_repository.get_all_devices(
                page=page, page_size=page_size, search_query=search_query,status=status
            )
            return devices
        except Exception as e:
            raise e

    def assign_imei(self, device_uuid: str, imei: str):
        try:
            device = self.device_repository.assign_imei(device_uuid, imei)
            return device
        except Exception as e:
            raise e
