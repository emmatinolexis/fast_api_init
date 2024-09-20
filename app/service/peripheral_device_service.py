from app.core.constants import (
    INITIAL_GAS_DEVICE_SERIAL_NUMBER,
    INITIAL_GATEWAY_DEVICE_SERIAL_NUMBER,
    INITIAL_PYROGUARD_DEVICE_SERIAL_NUMBER,
)
from app.repository.peripheral_devices_repository import PeripheralDeviceRepository
from app.schema.peripheral_device_schema import (
    CreatePeripheralDevice,
    CreatePeripheralDeviceInput,
)
from app.service.base_service import BaseService
from app.util.enums import DeviceType
from app.util.utils import generate_serial_numbers


class PeripheralDeviceService(BaseService):
    def __init__(self, peripheral_device_repository: PeripheralDeviceRepository):
        self.peripheral_device_repository = peripheral_device_repository
        super().__init__(peripheral_device_repository)

    def get_list(self, page=1, page_size=10, device_type=None, search=None):
        try:
            return self.peripheral_device_repository.read_all(
                page=page, page_size=page_size, device_type=device_type, search=search
            )
        except Exception as e:
            raise e
        
    def create_peripheral_device(self, payload: CreatePeripheralDevice):
        try:
            device_type = payload.device_type
            last_created_device = self.peripheral_device_repository.get_last_device(
                payload.device_type
            )

            if last_created_device:
                serial_numbers = generate_serial_numbers(
                    last_created_device.serial_number,
                    payload.device_type,
                    payload.no_of_devices,
                )

                for serial_number in serial_numbers:
                    data = CreatePeripheralDeviceInput(
                        serial_number=serial_number, device_type=device_type
                    )
                    self.peripheral_device_repository.create(data)
            else:
                if device_type == DeviceType.PYROGUARD_NODE_DEVICE:
                    initial_data = CreatePeripheralDeviceInput(
                        serial_number=INITIAL_PYROGUARD_DEVICE_SERIAL_NUMBER,
                        device_type=device_type,
                    )
                    self.peripheral_device_repository.create(initial_data)

                if device_type == DeviceType.GAS_NODE_DEVICE:
                    initial_data = CreatePeripheralDeviceInput(
                        serial_number=INITIAL_GAS_DEVICE_SERIAL_NUMBER,
                        device_type=device_type,
                    )
                    self.peripheral_device_repository.create(initial_data)

                if device_type == DeviceType.GATEWAY_DEVICE:
                    initial_data = CreatePeripheralDeviceInput(
                        serial_number=INITIAL_GATEWAY_DEVICE_SERIAL_NUMBER,
                        device_type=device_type,
                    )
                    self.peripheral_device_repository.create(initial_data)
        except Exception as e:
            raise e

