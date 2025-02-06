from typing import List

from app.core import messages
from app.core.exceptions import BadRequestError, NotFoundError
from app.model.user import User
from app.repository.gas_device_repository import GasDeviceRepository
from app.schema.fire_device_schema import (
    CreateFireDevice,
    CreateFireDevicePayload,
    UploadFireDevice,
)
from app.schema.gas_cylinder_schema import CreateGasDevice, UploadGasDeviceCSV
from app.service.base_service import BaseService
from app.transfomers.gas_device_transformer import gas_device_transformer
from app.util.enums import DeviceType


class GasDeviceService(BaseService):
    def __init__(self, gas_device_repository: GasDeviceRepository):
        self.gas_device_repository = gas_device_repository
        super().__init__(gas_device_repository)

    async def get_device_by_uuid(self, uuid: str):
        return await self.gas_device_repository.read_by_uuid(uuid)

    async def get_gas_device_by_serial_no(self, device_serial_no: str):
        try:
            device = await self.gas_device_repository.get_device_by_serial_no(
                device_serial_no
            )
            return device
        except Exception as e:
            raise e

    async def load_csv(self, serial_numbers: List[str], user):
        try:
            for serial_number in serial_numbers:
                schema = UploadGasDeviceCSV(
                    serial_number=str(serial_number),
                    user_uuid=user.uuid,
                    device_type=DeviceType.GAS_DEVICE,
                )
                await self.gas_device_repository.create(schema)

            return "Gas Devices uploaded successfully"
        except Exception as e:
            raise e

    async def load_fire_devices(self, serial_numbers: List[str], user):
        try:
            with self.gas_device_repository.session_factory() as session:
                # Start a transaction
                for serial_number in serial_numbers:
                    existing_device = (
                        await self.gas_device_repository.get_device_by_serial_no(
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
                    await self.gas_device_repository.create(schema)

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

    async def get_all_devices(
        self,
        serial_number: str = None,
        device_type: DeviceType = None,
        page: int = 1,
        limit: int = 10,
    ):
        try:
            devices = await self.gas_device_repository.get_all_devices(
                serial_number=serial_number, device_type=device_type
            )

            # Paginate the results

            paginated_devices = devices[(page - 1) * limit : page * limit]
            total_devices = len(devices)

            return {
                "total_devices": total_devices,
                "devices": [
                    gas_device_transformer(device) for device in paginated_devices
                ],
                "page": page,
                "limit": limit,
            }
        except Exception as e:
            raise e

    async def create_device(
        self,
        payload: CreateGasDevice,
        user_uuid: str = None,
        business_profile_uuid: str = None,
    ):
        try:
            existing_device = await self.gas_device_repository.get_device_by_serial_no(
                payload.serial_number
            )
            if existing_device:
                if existing_device.device_type != payload.device_type:
                    raise BadRequestError(messages.DEVICE_TYPE_MISMATCH)

                await self.gas_device_repository.update_attr_by_uuid(
                    existing_device.uuid, "user_uuid", user_uuid
                )
                await self.gas_device_repository.update_attr_by_uuid(
                    existing_device.uuid, "business_profile_uuid", business_profile_uuid
                )
                await self.gas_device_repository.update_attr_by_uuid(
                    existing_device.uuid, "building_uuid", payload.building_uuid
                )

                return gas_device_transformer(existing_device)
            else:
                raise NotFoundError(messages.DEVICE_DOES_NOT_EXIST)
        except NotFoundError as e:
            raise e
        except Exception as e:
            raise e

    async def get_user_devices(self, user_uuid: str):
        try:
            devices = await self.gas_device_repository.get_user_devices(user_uuid)
            return [gas_device_transformer(device) for device in devices]
        except Exception as e:
            raise e

    async def get_business_devices(self, business_profile_uuid: str):
        try:
            devices = await self.gas_device_repository.get_business_devices(
                business_profile_uuid
            )
            return [gas_device_transformer(device) for device in devices]
        except Exception as e:
            raise e

    async def get_building_devices(self, building_uuid: str, device_type: str = None):
        try:
            devices = await self.gas_device_repository.get_building_devices(
                building_uuid, device_type
            )
            return [gas_device_transformer(device) for device in devices]
        except Exception as e:
            raise e

    async def add_fire_device_to_building(
        self, building_uuid: str, payload: CreateFireDevice, user: User
    ):
        try:
            schema = CreateFireDevicePayload(
                serial_number=payload.serial_number,
                location=payload.location,
                building_uuid=building_uuid,
                user_uuid=str(user.uuid),
                business_profile_uuid=(
                    str(user.business_profile.uuid) if user.business_profile else None
                ),
                device_type=DeviceType.FIRE_DETECTOR,
            )

            existing_device = await self.gas_device_repository.get_device_by_serial_no(
                payload.serial_number
            )

            if not existing_device:
                raise NotFoundError(messages.DEVICE_DOES_NOT_EXIST)

            if existing_device.device_type != payload.device_type:
                raise BadRequestError(messages.DEVICE_TYPE_MISMATCH)

            existing_device = await self.gas_device_repository.update_by_uuid(
                existing_device.uuid, schema
            )
            return gas_device_transformer(existing_device)
        except Exception as e:
            raise e
