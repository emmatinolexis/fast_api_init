from app.core import messages
from app.core.exceptions import AuthError, NotFoundError
from app.model.user import User
from app.repository.gas_cylinder_repository import GasCylinderRepository
from app.repository.gas_device_repository import GasDeviceRepository
from app.schema.gas_cylinder_schema import (
    CreateGasCylinderPayload,
    CreateSpareGasCylinder,
    CreateSpareGasCylinderSchema,
)
from app.service.base_service import BaseService
from app.transfomers.gas_cylinder_transformers import gas_cylinder_transformer
from app.util.enums import AccountType, DeviceStatus


class GasCylinderService(BaseService):
    def __init__(
        self,
        gas_cylinder_repository: GasCylinderRepository,
        gas_device_repository: GasDeviceRepository,
    ):
        self.gas_cylinder_repository = gas_cylinder_repository
        self.gas_device_repository = gas_device_repository
        super().__init__(gas_cylinder_repository)

    def link_to_gas_device(self, gas_cylinder_uuid: str, gas_device_uuid: str):
        self.gas_cylinder_repository.update_attr_by_uuid(
            gas_cylinder_uuid, "gas_device_uuid", gas_device_uuid
        )

        self.gas_device_repository.update_attr_by_uuid(
            gas_device_uuid, "status", DeviceStatus.ASSIGNED
        )

        return self.get_by_uuid(gas_cylinder_uuid)

    def unlink_gas_cylinder(self, gas_cylinder_uuid: str):
        cylinder = self.get_by_uuid(gas_cylinder_uuid)
        gas_device_uuid = cylinder.gas_device_uuid

        self.gas_cylinder_repository.update_attr_by_uuid(
            gas_cylinder_uuid, "gas_device_uuid", None
        )

        self.gas_device_repository.update_attr_by_uuid(
            gas_device_uuid, "status", DeviceStatus.NOT_ASSIGNED
        )

        return cylinder

    def get_user_cylinders(self, user_uuid: str):
        return self.gas_cylinder_repository.read_all_by_user_uuid(user_uuid)

    def create_gas_cylinder_without_device(
        self,
        payload: CreateGasCylinderPayload,
        user_uuid: str,
        business_uuid: str = None,
    ):
        try:
            cylinder = self.gas_cylinder_repository.create_gas_cylinder(
                payload, user_uuid, business_uuid
            )
            if payload.gas_cylinder_uuid and payload.gas_device_serial_number:
                gas_device = self.gas_device_repository.get_device_by_serial_no(
                    payload.gas_device_serial_number
                )
                self.gas_device_repository.update_attr_by_uuid(
                    gas_device.uuid, "status", DeviceStatus.ASSIGNED
                )
                self.gas_device_repository.update_attr_by_uuid(
                    gas_device.uuid, "building_uuid", payload.building_uuid
                )

            return cylinder

        except Exception as e:
            raise e

    def get_cylinder_by_uuid(
        self,
        cylinder_uuid: str = None,
    ):
        try:
            return self.gas_cylinder_repository.get_gas_cylinder_by_uuid(cylinder_uuid)
        except Exception as e:
            raise e

    def delete_gas_cylinder(self, cylinder_uuid: str, user: User):
        try:
            user_uuid = user.uuid
            user_account_type = user.account_type

            cylinder = self.gas_cylinder_repository.read_by_uuid(cylinder_uuid)
            if not cylinder:
                raise NotFoundError(messages.GAS_CYLINDER_NOT_FOUND + cylinder_uuid)

            if (
                user_account_type == AccountType.INDIVIDUAL
                and cylinder.user_uuid != user_uuid
            ):
                raise AuthError(messages.ACTION_NOT_ALLOWED)
            elif (
                user_account_type == AccountType.BUSINESS
                and cylinder.business_profile_uuid != user.business_profile.uuid
            ):
                raise AuthError(messages.ACTION_NOT_ALLOWED)

            device = self.gas_device_repository.get_device_by_serial_no(
                cylinder.gas_device_serial_number
            )
            if device:
                self.gas_device_repository.update_attr_by_uuid(
                    device.uuid, "status", DeviceStatus.NOT_ASSIGNED
                )

            self.gas_cylinder_repository.delete_by_uuid(cylinder_uuid)

        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")

    def create_spare_cylinder(
        self,
        payload: CreateSpareGasCylinder,
        user_uuid: str,
        business_profile_uuid: str = None,
    ):
        try:
            full_payload = CreateSpareGasCylinderSchema(
                **payload.dict(),
                user_uuid=user_uuid,
                business_profile_uuid=business_profile_uuid,
            )
            created_cylinder = self.gas_cylinder_repository.create(full_payload)
            return gas_cylinder_transformer(created_cylinder)

        except Exception as e:
            raise e
