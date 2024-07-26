from app.repository.gas_device_repository import GasDeviceRepository
from app.service.base_service import BaseService


class GasDeviceService(BaseService):
    def __init__(self, gas_device_repository: GasDeviceRepository):
        self.gas_device_repository = gas_device_repository
        super().__init__(gas_device_repository)

    def get_device_by_uuid(self, uuid: str):
        return self.gas_device_repository.read_by_uuid(uuid)

    def get_gas_device_by_serial_no(self, device_serial_no: str):
        try:
            device = self.gas_device_repository.get_device_by_serial_no(
                device_serial_no
            )
            return device
        except Exception as e:
            raise e
