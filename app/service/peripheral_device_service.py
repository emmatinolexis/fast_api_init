from app.core import messages
from datetime import datetime
from app.core.constants import (
    INITIAL_GAS_DEVICE_SERIAL_NUMBER,
    INITIAL_GATEWAY_DEVICE_SERIAL_NUMBER,
    INITIAL_PYROGUARD_DEVICE_SERIAL_NUMBER,
)
from app.core.exceptions import AuthError, BadRequestError, NotFoundError
from app.repository.device_node_configuration_repository import (
    DeviceNodeConfigRepository,
)
from app.repository.peripheral_devices_repository import PeripheralDeviceRepository
from app.repository.user_repository import UserRepository
from app.schema.peripheral_device_schema import (
    CreatePeripheralDevice,
    CreatePeripheralDeviceInput,
    DefaultGasConfig,
    DefaultPyroConfig,
    UpdateDeviceConfigThreshold,
    UpdatePeripheralDevice,
    UpdatePeripheralDeviceFull,
)
from app.service.base_service import BaseService
from app.transfomers.peripheral_device_transformer import peripheral_device_transformer
from app.util.enums import DeviceType, PeripheralDeviceType
from app.util.utils import generate_serial_numbers
from app.service.device_events_service import DeviceEventService
from app.repository.device_events_repository import DeviceEventRepository


class PeripheralDeviceService(BaseService):
    def __init__(
        self,
        peripheral_device_repository: PeripheralDeviceRepository,
        device_events_service: DeviceEventService,
        user_repository: UserRepository,
        device_node_config_repository: DeviceNodeConfigRepository,
        device_event_repository: DeviceEventRepository
    ):
        self.peripheral_device_repository = peripheral_device_repository
        self.device_events_service = device_events_service
        self.user_repository = user_repository
        self.device_node_config_repository = device_node_config_repository
        self.device_event_repository = device_event_repository
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
                    peripheral_device = self.peripheral_device_repository.create(data)

                    # Create default configuration based on device type
                    self.create_default_config(peripheral_device.uuid, device_type)

            else:
                if device_type == DeviceType.PYROGUARD_NODE_DEVICE:
                    initial_data = CreatePeripheralDeviceInput(
                        serial_number=INITIAL_PYROGUARD_DEVICE_SERIAL_NUMBER,
                        device_type=device_type,
                    )
                    peripheral_device = self.peripheral_device_repository.create(
                        initial_data
                    )

                    # Create default configuration
                    self.create_default_config(peripheral_device.uuid, device_type)

                if device_type == DeviceType.GAS_NODE_DEVICE:
                    initial_data = CreatePeripheralDeviceInput(
                        serial_number=INITIAL_GAS_DEVICE_SERIAL_NUMBER,
                        device_type=device_type,
                    )
                    peripheral_device = self.peripheral_device_repository.create(
                        initial_data
                    )

                    # Create default configuration
                    self.create_default_config(peripheral_device.uuid, device_type)

                if device_type == DeviceType.GATEWAY_DEVICE:
                    initial_data = CreatePeripheralDeviceInput(
                        serial_number=INITIAL_GATEWAY_DEVICE_SERIAL_NUMBER,
                        device_type=device_type,
                    )
                    peripheral_device = self.peripheral_device_repository.create(
                        initial_data
                    )
        except Exception as e:
            raise e

    def create_default_config(
        self, peripheral_device_uuid: str, device_type: PeripheralDeviceType
    ):
        if device_type == DeviceType.PYROGUARD_NODE_DEVICE:
            pyro_config = DefaultPyroConfig(
                peripheral_device_uuid=str(peripheral_device_uuid)
            )
            self.device_node_config_repository.create(pyro_config)

        elif device_type == DeviceType.GAS_NODE_DEVICE:
            gas_config = DefaultGasConfig(
                peripheral_device_uuid=str(peripheral_device_uuid)
            )
            self.device_node_config_repository.create(gas_config)

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

            return [
                peripheral_device_transformer(
                    device,
                    self.peripheral_device_repository,
                    self.device_node_config_repository,
                )
                for device in devices
            ]
        except Exception as e:
            raise e

    def get_business_devices(
        self, user_uuid, business_profile_uuid, device_type: str = None
    ):
        try:
            dev_data = []
            devices = self.peripheral_device_repository.get_business_devices(
                business_profile_uuid, device_type
            )

            for device in devices:
                latest_event = self.device_events_service.get_devices_latest_reading(device.node_id)
                data = {
                    "uuid": str(device.uuid),
                    "serial_number": device.serial_number,
                    "node_id": str(device.node_id) if device.node_id else None,
                    "status": device.status.name if device.status else None,
                    "user_uuid": str(device.user_uuid) if device.user_uuid else None,
                    "business_profile_uuid": str(device.business_profile_uuid)
                    if device.business_profile_uuid
                    else None,
                    "building_uuid": str(device.building_uuid) if device.building_uuid else None,
                    "location": device.location,
                    "device_type": device.device_type.name if device.device_type else None,
                    "current_device_reading": latest_event.measurements if latest_event else None
                }
                dev_data.append(data)
            return dev_data

        except Exception as e:
            raise e

    def get_building_devices(self, building_uuid, device_type: str = None):
        try:
            devices = self.peripheral_device_repository.get_building_devices(
                building_uuid, device_type=device_type
            )

            return [
                peripheral_device_transformer(
                    device,
                    self.peripheral_device_repository,
                    self.device_node_config_repository,
                    self.device_event_repository
                )
                for device in devices
            ]
        except Exception as e:
            raise e

    def set_device_configuration_to_default(self, peripheral_device_uuid: str):
        try:
            device = self.device_node_config_repository.set_peripheral_device_to_default(peripheral_device_uuid)
            return device
        except Exception as e:
            raise e

    def update_device_threshold(
        self,
        device_serial_number: str,
        payload: UpdateDeviceConfigThreshold,
        user_uuid: str,
    ):
        try:
            # Retrieve the peripheral device by serial number
            device = self.peripheral_device_repository.get_by_serial_number(
                device_serial_number
            )

            # Check if the device exists
            if not device:
                raise NotFoundError(
                    messages.PERIPHERAL_DEVICE_NOT_FOUND + device_serial_number
                )

            # Retrieve the user by UUID
            user = self.user_repository.get_user_by_uuid(user_uuid)

            # Check if the user exists
            if not user:
                raise NotFoundError(messages.USER_NOT_FOUND + user_uuid)

            # Check if the user is authorized to update this device
            is_user_authorized = (
                device.user_uuid == user.get("uuid")
                or device.business_profile_uuid == user.get("business_profile").uuid
            )

            if not is_user_authorized:
                raise AuthError(messages.UNAUTHORIZED_ACTION)

            # Handle the device configuration based on device type
            config = self.device_node_config_repository.get_device_node_config_by_device_uuid(
                device.uuid
            )

            # Create default configurations if they don't exist
            if not config:
                if device.device_type == DeviceType.PYROGUARD_NODE_DEVICE:
                    config = self.device_node_config_repository.create(
                        DefaultPyroConfig(peripheral_device_uuid=str(device.uuid))
                    )
                elif device.device_type == DeviceType.GAS_NODE_DEVICE:
                    config = self.device_node_config_repository.create(
                        DefaultGasConfig(peripheral_device_uuid=str(device.uuid))
                    )

            # Update the device configuration
            self.device_node_config_repository.update_by_uuid(config.uuid, payload)

            # Return the transformed device data
            return peripheral_device_transformer(
                device,
                self.peripheral_device_repository,
                self.device_node_config_repository,
                self.device_event_repository
            )

        except Exception as e:
            raise e
