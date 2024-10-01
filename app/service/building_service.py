from typing import Optional

from app.core import messages
from app.core.exceptions import NotFoundError,BadRequestError,AuthError
from app.repository.building_repository import BuildingRepository
from app.repository.gas_cylinder_repository import GasCylinderRepository
from app.repository.gas_device_repository import GasDeviceRepository
from app.repository.user_repository import UserRepository
from app.repository.peripheral_devices_repository import PeripheralDeviceRepository
from app.schema.asset_schema import (
    BuildingInput,
    CreateBuildingInput,
    CreateFireDeviceInput,
    GasCylinderPayload,
    UpdateBuildingPayload,
)
from app.service.base_service import BaseService
from app.transfomers.building_transformers import building_transformer
from app.util.enums import DeviceStatus, DeviceType
from app.schema.peripheral_device_schema import CreateBuildingWithDeviceFull,CreateBuildingWithDevice,UpdateBuildingWithDevice


class BuildingService(BaseService):
    def __init__(
        self,
        building_repository: BuildingRepository,
        gas_device_repository: GasDeviceRepository,
        gas_cylinder_repository: GasCylinderRepository,
        user_repository: UserRepository,
        peripheral_device_repository: PeripheralDeviceRepository,
    ):
        self.building_repository = building_repository
        self.gas_device_repository = gas_device_repository
        self.gas_cylinder_repository = gas_cylinder_repository
        self.user_repository = user_repository
        self.peripheral_device_repository = peripheral_device_repository
        super().__init__(building_repository)

    def create_building(self, payload: BuildingInput):
        try:
            # Handle building creation
            if payload.building:
                building_data = CreateBuildingInput(
                    building_name=payload.building.building_name,
                    longitude=payload.building.longitude,
                    latitude=payload.building.latitude,
                    image_url=payload.building.image_url,
                    status=payload.building.status,
                    user_uuid=payload.building.user_uuid,
                    business_profile_uuid=payload.building.business_profile_uuid,
                )
                building = self.building_repository.create(building_data)
                building_uuid = building.uuid
            elif payload.building_uuid:
                building_uuid = payload.building_uuid
                building = self.building_repository.read_by_uuid(building_uuid)
                if not building:
                    raise ValueError(f"No building found with UUID: {building_uuid}")
            else:
                raise ValueError(
                    "Either 'building' or 'building_uuid' must be provided"
                )

            # Conditionally create gas cylinder if required
            if payload.create_gas and payload.gas_cylinder:
                cylinder_data = GasCylinderPayload(
                    cylinder_name=payload.gas_cylinder.cylinder_name,
                    # material_type=payload.gas_cylinder.material_type,
                    gas_device_serial_number=payload.gas_cylinder.device_serial_number,
                    cylinder_type_uuid=payload.gas_cylinder.cylinder_type_uuid,
                    building_uuid=building_uuid,
                    user_uuid=building.user_uuid,
                    business_profile_uuid=building.business_profile_uuid,
                )
                self.gas_cylinder_repository.create(cylinder_data)

            # Conditionally create fire device if required
            if payload.create_fire_device and payload.fire_device:
                fire_device_data = CreateFireDeviceInput(
                    serial_number=payload.fire_device.serial_number,
                    building_uuid=building_uuid,
                    user_uuid=building.user_uuid,
                    business_profile_uuid=building.business_profile_uuid,
                    location=payload.fire_device.location,
                    device_type=DeviceType.PYROGUARD_NODE_DEVICE,
                )
                device = self.gas_device_repository.get_device_by_serial_no(
                    fire_device_data.serial_number
                )
                if device:
                    self.gas_device_repository.update_by_uuid(
                        device.uuid, fire_device_data
                    )
                    self.gas_device_repository.update_attr_by_uuid(
                        device.uuid, "status", DeviceStatus.ASSIGNED
                    )

            return building

        except Exception as e:
            # Rollback building creation if necessary
            if payload.building and "building" in locals():
                self.building_repository.delete_by_uuid(building.uuid)
            raise e

    def get_all_buildings(
        self,
        user_uuid: str = None,
        business_uuid: str = None,
        page_size: int = 10,
        page: int = 1,
    ):
        try:
            report = self.building_repository.read_all_building(
                user_uuid=user_uuid,
                business_uuid=business_uuid,
                page=page,
                page_size=page_size,
            )
            return report
        except Exception as e:
            raise e

    def get_building_by_uuid(
        self,
        building_uuid: str = None,
    ):
        try:
            report = self.building_repository.read_building_by_uuid(building_uuid)
            return report
        except Exception as e:
            raise e

    def get_building_cylinder_assets(
        self,
        building_uuid: str,
        cylinder_status: Optional[str] = None,
        page_size: int = 10,
        page: int = 1,
    ):
        try:
            cylinders = self.gas_cylinder_repository.get_gas_cylinder_by_building_uuid(
                building_uuid=building_uuid, cylinder_status=cylinder_status
            )

            total = len(cylinders)
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            paginated_cylinders = cylinders[start_index:end_index]

            return {
                "cylinders": paginated_cylinders,
                "total_cylinders": total,
                "total_pages": (total + page_size - 1) // page_size,
                "current_page": page,
                "page_size": page_size,
            }

        except Exception as e:
            raise e

    def update_building(self, building_uuid: str, payload: UpdateBuildingPayload):
        try:
            building = self.building_repository.read_by_uuid(building_uuid)
            if not building:
                raise NotFoundError(messages.BUILDING_NOT_FOUND + building_uuid)

            building = self.building_repository.update_by_uuid(building_uuid, payload)
            return building_transformer(building)
        except Exception as e:
            raise e
        

    def create_building_with_peripheral_device(self, user_uuid: str, payload: CreateBuildingWithDevice):
        try:
            user = self.user_repository.get_user_by_uuid(user_uuid)
            if not user:
                raise NotFoundError(messages.USER_NOT_FOUND + user_uuid)

            device = self.peripheral_device_repository.get_by_serial_number(payload.serial_number)
            if not device:
                raise BadRequestError(messages.DEVICE_DOES_NOT_EXIST)

            if payload.device_type != device.device_type:
                raise BadRequestError(messages.DEVICE_TYPE_MISMATCH)

            user_business_uuid = user.get("business_profile")
            user_business_uuid_str = str(user_business_uuid.uuid) if user_business_uuid else None

            # Check business profile first
            if device.business_profile_uuid:
                print(user_business_uuid_str,device.business_profile_uuid)
                print(type(user_business_uuid_str),type(device.business_profile_uuid))
                if not user_business_uuid_str or user_business_uuid_str != str(device.business_profile_uuid):
                    raise AuthError(messages.ACTION_NOT_ALLOWED)
            # If no business profile, then check user
            elif device.user_uuid and device.user_uuid != user_uuid:
                raise AuthError(messages.ACTION_NOT_ALLOWED)

            # If we've reached this point, the user is allowed to add the device to a building

            building_data = CreateBuildingWithDeviceFull(
                building_name=payload.building_name,
                longitude=payload.longitude,
                latitude=payload.latitude,
                image_url=payload.image_url,
                user_uuid=str(user_uuid),
                business_profile_uuid=user_business_uuid_str
            )

            building = self.building_repository.create(building_data)

            device = self.peripheral_device_repository.update_by_uuid(
                device.uuid,
                UpdateBuildingWithDevice(
                    building_uuid=str(building.uuid),
                    location=payload.location,
                    status=DeviceStatus.ASSIGNED,
                    user_uuid=str(user_uuid),
                    business_profile_uuid=user_business_uuid_str
                )
            )

            return building_transformer(building)

        except Exception as e:
            raise e

