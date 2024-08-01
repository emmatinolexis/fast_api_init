from app.repository.gas_cylinder_repository import GasCylinderRepository
from app.repository.gas_device_repository import GasDeviceRepository
from app.schema.gas_cylinder_schema import CreateGasCylinderPayload
from app.service.base_service import BaseService
from app.util.enums import DeviceStatus


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

    def create_gas_cylinder_without_device(
        self,
        payload: CreateGasCylinderPayload,
        user_uuid: str,
        business_uuid: str = None,
    ):
        try:
            return self.gas_cylinder_repository.create_gas_cylinder(
                payload, user_uuid, business_uuid
            )
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
