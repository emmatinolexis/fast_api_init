from app.core import messages
from app.core.constants import (
    INITIAL_GAS_DEVICE_SERIAL_NUMBER,
    INITIAL_GATEWAY_DEVICE_SERIAL_NUMBER,
    INITIAL_PYROGUARD_DEVICE_SERIAL_NUMBER,
)
from app.core.exceptions import BadRequestError
from app.repository.peripheral_devices_repository import PeripheralDeviceRepository
from app.repository.user_repository import UserRepository
from app.schema.peripheral_device_schema import (
    CreatePeripheralDevice,
    CreatePeripheralDeviceInput,
    UpdatePeripheralDevice,
    UpdatePeripheralDeviceFull,
)
from app.service.base_service import BaseService
from app.transfomers.peripheral_device_transformer import peripheral_device_transformer
from app.util.enums import DeviceType
from app.util.utils import generate_serial_numbers


class PeripheralDeviceService(BaseService):
    def __init__(
        self,
        peripheral_device_repository: PeripheralDeviceRepository,
        user_repository: UserRepository,
    ):
        self.peripheral_device_repository = peripheral_device_repository
        self.user_repository = user_repository
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

    def get_devices_by_serial_number(self, serial_number: str):
        try:
            devices = self.peripheral_device_repository.get_by_serial_number(
                serial_number
            )
            return devices
        except Exception as e:
            raise e

    def update_peripheral_device(
        self, user_uuid, payload: UpdatePeripheralDevice, building_uuid: str
    ):
        try:
            user = self.user_repository.get_user_by_uuid(user_uuid=user_uuid)
            if not user:
                raise BadRequestError(messages.USER_NOT_FOUND + user_uuid)

            peripheral_device = self.peripheral_device_repository.get_by_serial_number(
                payload.serial_number
            )

            if not peripheral_device:
                raise BadRequestError(
                    messages.PERIPHERAL_DEVICE_NOT_FOUND + payload.device_serial_number
                )

            data = UpdatePeripheralDeviceFull(
                user_uuid=str(user_uuid),
                business_profile_uuid=str(user.get("business_profile").uuid)
                if user.get("business_profile")
                else None,
                location=payload.location,
                serial_number=payload.serial_number,
                building_uuid=building_uuid,
            )

            self.peripheral_device_repository.update_by_uuid(
                uuid=peripheral_device.uuid, schema=data
            )

            response = messages.UPDATE_SUCCESS + "device"
            return response

        except Exception as e:
            raise e

    def get_user_devices(self, user_uuid, device_type: str = None):
        try:
            devices = self.peripheral_device_repository.get_user_devices(
                user_uuid, device_type
            )

            return [peripheral_device_transformer(device) for device in devices]
        except Exception as e:
            raise e

    def get_business_devices(
        self, user_uuid, business_profile_uuid, device_type: str = None
    ):
        try:
            devices = self.peripheral_device_repository.get_business_devices(
                business_profile_uuid, device_type
            )

            return [peripheral_device_transformer(device) for device in devices]
        except Exception as e:
            raise e

    def get_building_devices(self, building_uuid, device_type: str = None):
        try:
            devices = self.peripheral_device_repository.get_building_devices(
                building_uuid, device_type=device_type
            )

            return [peripheral_device_transformer(device) for device in devices]
        except Exception as e:
            raise e
