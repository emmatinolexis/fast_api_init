from typing import List

from app.core import messages
from app.core.exceptions import NotFoundError
from app.repository.gas_device_repository import GasDeviceRepository
from app.schema.fire_device_schema import UploadFireDevice
from app.schema.gas_cylinder_schema import CreateGasDevice, UploadGasDeviceCSV
from app.service.base_service import BaseService
from app.transfomers.gas_device_transformer import gas_device_transformer
from app.util.enums import DeviceType


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

    def load_csv(self, serial_numbers: List[str], user):
        try:
            for serial_number in serial_numbers:
                schema = UploadGasDeviceCSV(
                    serial_number=serial_number,
                    user_uuid=user.uuid,
                )
                self.gas_device_repository.create(schema)

            return "Gas Devices uploaded successfully"
        except Exception as e:
            raise e

    def load_fire_devices(self, serial_numbers: List[str], user):
        try:
            with self.gas_device_repository.session_factory() as session:
                # Start a transaction
                for serial_number in serial_numbers:
                    existing_device = (
                        self.gas_device_repository.get_device_by_serial_no(
                            str(serial_number)
                        )
                    )

                    if existing_device:
                        raise ValueError(
                            f"Device with serial number {serial_number} already exists"
                        )

                    schema = UploadFireDevice(
                        device_name="Fire Device",
                        serial_number=str(serial_number),
                        device_type=DeviceType.FIRE_DETECTOR,  # Explicitly set enum value
                    )
                    self.gas_device_repository.create(schema)

                # Commit the transaction only after all devices are processed successfully
                session.commit()

            return "Fire Devices uploaded successfully"
        except ValueError as e:
            # Roll back the transaction in case of any error
            session.rollback()
            raise e
        except Exception as e:
            # Roll back the transaction in case of any error
            session.rollback()
            raise e

    def get_all_devices(self, serial_number: str = None):
        try:
            if serial_number:
                return self.gas_device_repository.search(serial_number)

            return self.gas_device_repository.read_all()
        except Exception as e:
            raise e

    def create_device(
        self,
        payload: CreateGasDevice,
        user_uuid: str = None,
        business_profile_uuid: str = None,
    ):
        try:
            # Retrieve the device by serial number
            existing_device = self.gas_device_repository.get_device_by_serial_no(
                payload.serial_number
            )

            # If the device exists, update its attributes
            if existing_device:
                self.gas_device_repository.update_attr_by_uuid(
                    existing_device.uuid, "user_uuid", user_uuid
                )
                self.gas_device_repository.update_attr_by_uuid(
                    existing_device.uuid, "business_profile_uuid", business_profile_uuid
                )
                self.gas_device_repository.update_attr_by_uuid(
                    existing_device.uuid, "building_uuid", payload.building_uuid
                )
                return gas_device_transformer(existing_device)
            else:
                raise NotFoundError(messages.DEVICE_DOES_NOT_EXIST)
        except NotFoundError as e:
            raise e
        except Exception as e:
            raise e

    def get_user_devices(self, user_uuid: str):
        try:
            devices = self.gas_device_repository.get_user_devices(user_uuid)
            return [gas_device_transformer(device) for device in devices]
        except Exception as e:
            raise e

    def get_business_devices(self, business_profile_uuid: str):
        try:
            devices = self.gas_device_repository.get_business_devices(
                business_profile_uuid
            )
            return [gas_device_transformer(device) for device in devices]
        except Exception as e:
            raise e

    def get_building_devices(self, building_uuid: str):
        try:
            devices = self.gas_device_repository.get_building_devices(building_uuid)
            return [gas_device_transformer(device) for device in devices]
        except Exception as e:
            raise e
